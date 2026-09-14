"""T05 statistical uncertainty for Trutina.

Deterministic, caller-seeded percentile intervals over frozen evaluation records.
Sampling design is explicit and never inferred. This module estimates evaluation-
sample uncertainty only; it does not alter point scores, Murphy UNC, authority,
weights, forecasts, or ledger state.
"""

from __future__ import annotations

from math import fsum, isfinite
import re
from typing import Any

SCHEMA = "brier.interval.report.v0"
SPECIALIST = "abx.brier"
DISPLAY = "Trutina"
RNG_VERSION = "TRUTINA_LCG32_V1"
MAX_CASE_DRAWS = 20_000_000
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class _LCG32:
    """Pinned 32-bit LCG used only for deterministic resampling indices."""

    def __init__(self, seed: int):
        self.state = seed & 0xFFFFFFFF

    def next_u32(self) -> int:
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return self.state

    def index(self, n: int) -> int:
        if n <= 0:
            raise ValueError("empty population")
        return (self.next_u32() * n) >> 32


def _base(request: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "specialist": SPECIALIST,
        "display": DISPLAY,
        "estimand": request.get("estimand", "BRIER_MEAN"),
        "method": request.get("method", "IID_PERCENTILE_BOOTSTRAP_V1"),
        "confidence_level": request.get("confidence_level", 0.95),
        "seed": request.get("seed", 0),
        "rng_version": request.get("rng_version", RNG_VERSION),
        "replicates_requested": request.get("replicates", 0),
        "replicates_valid": 0,
        "resampling_unit": request.get("resampling_unit", "CASE"),
        "block_length": request.get("block_length"),
        "lower": None,
        "upper": None,
        "status": "NOT_COMPUTABLE",
        "reason": "INVALID_DESIGN",
        "zero_reference_replicates": 0,
    }


def _unavailable(request: dict[str, Any], reason: str, *, valid: int = 0, zero_ref: int = 0) -> dict[str, Any]:
    report = _base(request)
    report.update(reason=reason, replicates_valid=valid, zero_reference_replicates=zero_ref)
    return report


def _number(value: Any, *, nonnegative: bool = False) -> float:
    if type(value) not in (int, float):
        raise ValueError("not numeric")
    value = float(value)
    if not isfinite(value) or (nonnegative and value < 0):
        raise ValueError("invalid numeric")
    return value


def _records(records: Any, request: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(records, list) or not records:
        raise ValueError("records required")
    estimand = request["estimand"]
    seen: set[str] = set()
    checked: list[dict[str, Any]] = []
    for position, raw in enumerate(records):
        if not isinstance(raw, dict):
            raise ValueError("record object required")
        case_id = raw.get("case_id")
        if not isinstance(case_id, str) or not case_id or case_id in seen:
            raise ValueError("unique case_id required")
        seen.add(case_id)
        model_loss = _number(raw.get("model_loss"), nonnegative=True)
        if model_loss > 1:
            raise ValueError("binary Brier loss out of range")
        weight = _number(raw.get("weight", 1.0), nonnegative=True)
        if request.get("weight_design") == "EQUAL_FIXED" and weight != 1.0:
            raise ValueError("equal-weight design required")
        record = {
            "case_id": case_id,
            "model_loss": model_loss,
            "weight": weight,
            "position": position,
        }
        if estimand in {"PAIRED_DELTA", "BSS"}:
            reference_loss = _number(raw.get("reference_loss"), nonnegative=True)
            if reference_loss > 1:
                raise ValueError("binary reference loss out of range")
            record["reference_loss"] = reference_loss
        cluster_field = request.get("cluster_field")
        if cluster_field is not None:
            cluster = raw.get(cluster_field)
            if not isinstance(cluster, str) or not cluster:
                raise ValueError("declared cluster missing")
            record["cluster"] = cluster
        checked.append(record)
    return checked


def _weighted_mean(rows: list[dict[str, Any]], key: str) -> float | None:
    weight_sum = fsum(row["weight"] for row in rows)
    if weight_sum <= 0:
        return None
    return fsum(row["weight"] * row[key] for row in rows) / weight_sum


def _statistic(rows: list[dict[str, Any]], estimand: str) -> tuple[float | None, bool]:
    model = _weighted_mean(rows, "model_loss")
    if model is None:
        return None, False
    if estimand == "BRIER_MEAN":
        return model, False
    reference = _weighted_mean(rows, "reference_loss")
    if reference is None:
        return None, False
    if estimand == "PAIRED_DELTA":
        return model - reference, False
    if estimand == "BSS":
        if reference == 0:
            return None, True
        return 1.0 - model / reference, False
    return None, False


def _iid_sample(rows: list[dict[str, Any]], rng: _LCG32) -> list[dict[str, Any]]:
    return [rows[rng.index(len(rows))] for _ in range(len(rows))]


def _cluster_units(rows: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    order: list[str] = []
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        cluster = row["cluster"]
        if cluster not in grouped:
            grouped[cluster] = []
            order.append(cluster)
        grouped[cluster].append(row)
    return [grouped[key] for key in order]


def _cluster_sample(units: list[list[dict[str, Any]]], rng: _LCG32) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for _ in range(len(units)):
        out.extend(units[rng.index(len(units))])
    return out


def _moving_block_sample(rows: list[dict[str, Any]], block_length: int, rng: _LCG32) -> list[dict[str, Any]]:
    n = len(rows)
    starts = n - block_length + 1
    if starts <= 0:
        raise ValueError("block longer than series")
    out: list[dict[str, Any]] = []
    while len(out) < n:
        start = rng.index(starts)
        out.extend(rows[start:start + block_length])
    return out[:n]


def _linear_quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    h = (len(ordered) - 1) * probability
    lower = int(h)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = h - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _is_degenerate(rows: list[dict[str, Any]], estimand: str) -> bool:
    if estimand == "BRIER_MEAN":
        return len({row["model_loss"] for row in rows}) < 2
    if estimand == "PAIRED_DELTA":
        return len({row["model_loss"] - row["reference_loss"] for row in rows}) < 2
    if estimand == "BSS":
        return len({(row["model_loss"], row["reference_loss"]) for row in rows}) < 2
    return True


def estimate_interval(request: Any, records: Any) -> dict[str, Any]:
    """Estimate a registered percentile interval or return an explicit unavailable report."""
    if not isinstance(request, dict):
        return _unavailable({}, "INVALID_DESIGN")
    required = {
        "schema", "specialist", "display", "estimand", "method", "manifest_hash",
        "confidence_level", "seed", "rng_version", "replicates", "resampling_unit",
        "sampling_assumption", "weight_design",
    }
    if not required.issubset(request):
        return _unavailable(request, "SAMPLING_DESIGN_UNKNOWN")
    if request.get("schema") != "brier.interval.request.v0" or request.get("specialist") != SPECIALIST or request.get("display") != DISPLAY:
        return _unavailable(request, "INVALID_DESIGN")
    if not isinstance(request.get("manifest_hash"), str) or _SHA256.fullmatch(request["manifest_hash"]) is None:
        return _unavailable(request, "INVALID_DESIGN")
    if request.get("rng_version") != RNG_VERSION:
        return _unavailable(request, "INVALID_DESIGN")
    if type(request.get("seed")) is not int or request["seed"] < 0:
        return _unavailable(request, "INVALID_DESIGN")
    if type(request.get("replicates")) is not int or not 0 < request["replicates"] <= 100_000:
        return _unavailable(request, "INVALID_DESIGN")
    confidence = request.get("confidence_level")
    if type(confidence) not in (int, float) or not 0 < float(confidence) < 1:
        return _unavailable(request, "INVALID_DESIGN")
    if request.get("weight_design") not in {"EQUAL_FIXED", "OUTCOME_INDEPENDENT_FIXED"}:
        return _unavailable(request, "INVALID_DESIGN")

    method = request.get("method")
    assumption = request.get("sampling_assumption")
    unit = request.get("resampling_unit")
    if method == "IID_PERCENTILE_BOOTSTRAP_V1":
        if assumption != "IID" or unit != "CASE" or request.get("cluster_field") is not None or request.get("block_length") is not None:
            return _unavailable(request, "INVALID_DESIGN")
    elif method == "CLUSTER_PERCENTILE_BOOTSTRAP_V1":
        if assumption != "INDEPENDENT_CLUSTERS" or unit != "CLUSTER" or not isinstance(request.get("cluster_field"), str) or not request["cluster_field"] or request.get("block_length") is not None:
            return _unavailable(request, "INVALID_DESIGN")
    elif method == "MOVING_BLOCK_PERCENTILE_BOOTSTRAP_V1":
        if assumption != "APPROX_STATIONARY_SERIAL" or unit != "MOVING_BLOCK" or type(request.get("block_length")) is not int or request["block_length"] <= 0 or request.get("cluster_field") is not None:
            return _unavailable(request, "INVALID_DESIGN")
    else:
        return _unavailable(request, "INVALID_DESIGN")

    estimand = request.get("estimand")
    if estimand not in {"BRIER_MEAN", "PAIRED_DELTA", "BSS"}:
        return _unavailable(request, "INVALID_DESIGN")
    if estimand in {"PAIRED_DELTA", "BSS"}:
        reference_id = request.get("reference_id")
        reference_hash = request.get("matched_reference_hash")
        if not isinstance(reference_id, str) or not reference_id:
            return _unavailable(request, "INVALID_DESIGN")
        if not isinstance(reference_hash, str) or _SHA256.fullmatch(reference_hash) is None:
            return _unavailable(request, "INVALID_DESIGN")

    try:
        checked = _records(records, request)
    except (ValueError, KeyError):
        return _unavailable(request, "INVALID_DESIGN")

    if len(checked) < 2:
        return _unavailable(request, "DEGENERATE_SAMPLE")
    units = None
    if method == "CLUSTER_PERCENTILE_BOOTSTRAP_V1":
        units = _cluster_units(checked)
        if len(units) < 2:
            return _unavailable(request, "DEGENERATE_SAMPLE")
    if method == "MOVING_BLOCK_PERCENTILE_BOOTSTRAP_V1" and request["block_length"] > len(checked):
        return _unavailable(request, "INVALID_DESIGN")
    if _is_degenerate(checked, estimand):
        return _unavailable(request, "DEGENERATE_SAMPLE")

    draws_per_rep = len(checked)
    if method == "CLUSTER_PERCENTILE_BOOTSTRAP_V1":
        assert units is not None
        draws_per_rep = len(units) * max(len(unit_rows) for unit_rows in units)
    if request["replicates"] * draws_per_rep > MAX_CASE_DRAWS:
        return _unavailable(request, "RESOURCE_LIMIT")

    rng = _LCG32(request["seed"])
    values: list[float] = []
    zero_reference = 0
    for _ in range(request["replicates"]):
        if method == "IID_PERCENTILE_BOOTSTRAP_V1":
            sample = _iid_sample(checked, rng)
        elif method == "CLUSTER_PERCENTILE_BOOTSTRAP_V1":
            sample = _cluster_sample(units or [], rng)
        else:
            sample = _moving_block_sample(checked, request["block_length"], rng)
        value, zero_ref = _statistic(sample, estimand)
        if zero_ref:
            zero_reference += 1
            continue
        if value is None or not isfinite(value):
            return _unavailable(request, "NONFINITE_RESULT", valid=len(values), zero_ref=zero_reference)
        values.append(value)

    if estimand == "BSS" and zero_reference:
        return _unavailable(request, "ZERO_REFERENCE_REPLICATE", valid=len(values), zero_ref=zero_reference)
    if not values:
        return _unavailable(request, "DEGENERATE_SAMPLE", zero_ref=zero_reference)

    alpha = (1.0 - float(confidence)) / 2.0
    report = _base(request)
    report.update(
        replicates_valid=len(values),
        lower=_linear_quantile(values, alpha),
        upper=_linear_quantile(values, 1.0 - alpha),
        status="COMPUTABLE",
        reason=None,
        zero_reference_replicates=zero_reference,
    )
    return report


# Provenance: Trutina Spec 000 / T05B; T05A contract baseline 58e596d.
