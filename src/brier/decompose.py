"""DECOMPOSE mode. Spec 000 / T04B.

Exact Murphy decomposition, corrected binned decomposition, and the elementary
Murphy-loss integral. Uses the same settled cohort contract as BATCH. Diagnostic
only: no promotion, forecast, ledger, interval, or weight-mutation authority.
"""

from __future__ import annotations

from collections import defaultdict
from math import fsum, isfinite
from typing import Any

from .batch import BatchContractError, aggregate_batch

SCHEMA = "brier.decompose.report.v0"
SPECIALIST = "abx.brier"
DISPLAY = "Trutina"
EXACT = "MURPHY_EXACT_V1"
BINNED = "MURPHY_BINNED_V1"
TOLERANCE = 1e-12
_REGISTERED_REASONS = {
    "EMPTY_COHORT",
    "ZERO_WEIGHT",
    "INVALID_MEMBER",
    "INVALID_BIN_EDGES",
    "NUMERICAL_IDENTITY_FAILURE",
}


def _base(method: str, manifest_hash: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "specialist": SPECIALIST,
        "display": DISPLAY,
        "mode": "DECOMPOSE",
        "status": "NOT_COMPUTABLE",
        "honesty": "NOT_COMPUTABLE",
        "method": method,
        "manifest_hash": manifest_hash,
        "raw_brier": None,
        "binned_brier": None,
        "reliability": None,
        "resolution": None,
        "uncertainty": None,
        "within_correction": None,
        "reconstruction_residual": None,
        "singleton_fraction": None,
        "bin_edges": None,
        "groups": [],
        "reasons": [],
        "forecast_eligible": False,
        "can_promote": False,
        "weight_mutation": False,
        "phenomenal": False,
        "ledger_id": None,
    }


def _reason(value: str) -> str:
    return value if value in _REGISTERED_REASONS else "INVALID_MEMBER"


def _refuse(method: str, manifest_hash: str, reason: str) -> dict[str, Any]:
    report = _base(method, manifest_hash)
    report["reasons"] = [_reason(reason)]
    return report


def _positive_scored_rows(manifest: dict[str, Any]) -> tuple[dict[str, Any], list[tuple[float, int, float]]]:
    batch = aggregate_batch(manifest)
    if batch.get("status") != "COMPUTABLE" or batch.get("brier") is None:
        return batch, []
    rows: list[tuple[float, int, float]] = []
    for row in manifest["members"]:
        if row.get("state") != "SETTLED":
            continue
        weight = float(row["weight"])
        if weight > 0:
            rows.append((float(row["p"]), int(row["y"]), weight))
    return batch, rows


def _common(rows: list[tuple[float, int, float]]) -> tuple[float, float, float]:
    weight_sum = fsum(weight for _, _, weight in rows)
    q = fsum(weight * y for _, y, weight in rows) / weight_sum
    return weight_sum, q, q * (1.0 - q)


def exact_murphy(manifest: dict[str, Any]) -> dict[str, Any]:
    manifest_hash = manifest.get("manifest_hash", "") if isinstance(manifest, dict) else ""
    batch, rows = _positive_scored_rows(manifest)
    if not rows:
        return _refuse(EXACT, manifest_hash, (batch.get("reasons") or ["EMPTY_COHORT"])[0])

    weight_sum, q, unc = _common(rows)
    grouped: dict[float, list[tuple[int, float]]] = defaultdict(list)
    for p, y, weight in rows:
        grouped[p].append((y, weight))

    rel_terms: list[float] = []
    res_terms: list[float] = []
    groups: list[dict[str, Any]] = []
    singleton_count = 0
    for p in sorted(grouped):
        members = grouped[p]
        group_weight = fsum(weight for _, weight in members)
        mass = group_weight / weight_sum
        q_g = fsum(weight * y for y, weight in members) / group_weight
        rel_terms.append(mass * (p - q_g) ** 2)
        res_terms.append(mass * (q_g - q) ** 2)
        singleton_count += int(len(members) == 1)
        groups.append({
            "count": len(members), "mass": mass, "mean_forecast": p,
            "event_rate": q_g, "left": None, "right": None,
            "within_variance": None, "within_covariance": None,
        })

    rel = fsum(rel_terms)
    res = fsum(res_terms)
    raw = float(batch["brier"])
    residual = raw - (rel - res + unc)
    report = _base(EXACT, manifest_hash)
    report.update(
        status="COMPUTABLE", honesty="OBSERVED", raw_brier=raw,
        reliability=rel, resolution=res, uncertainty=unc,
        reconstruction_residual=residual,
        singleton_fraction=singleton_count / len(groups), groups=groups,
    )
    if abs(residual) > TOLERANCE:
        report.update(status="NOT_COMPUTABLE", honesty="NOT_COMPUTABLE", reasons=["NUMERICAL_IDENTITY_FAILURE"])
    return report


def _validate_edges(edges: Any) -> list[float] | None:
    if not isinstance(edges, list) or len(edges) < 2:
        return None
    if any(type(v) not in (int, float) or not isfinite(float(v)) for v in edges):
        return None
    values = [float(v) for v in edges]
    if values[0] != 0.0 or values[-1] != 1.0:
        return None
    if any(not 0.0 <= v <= 1.0 for v in values):
        return None
    if any(a >= b for a, b in zip(values, values[1:])):
        return None
    return values


def _bin_index(p: float, edges: list[float]) -> int:
    if p == 1.0:
        return len(edges) - 2
    for index, (left, right) in enumerate(zip(edges, edges[1:])):
        if left <= p < right:
            return index
    raise ValueError("probability outside registered bin edges")


def binned_murphy(manifest: dict[str, Any], edges: Any) -> dict[str, Any]:
    manifest_hash = manifest.get("manifest_hash", "") if isinstance(manifest, dict) else ""
    valid_edges = _validate_edges(edges)
    if valid_edges is None:
        return _refuse(BINNED, manifest_hash, "INVALID_BIN_EDGES")

    batch, rows = _positive_scored_rows(manifest)
    if not rows:
        return _refuse(BINNED, manifest_hash, (batch.get("reasons") or ["EMPTY_COHORT"])[0])

    weight_sum, q, unc = _common(rows)
    bins: list[list[tuple[float, int, float]]] = [[] for _ in range(len(valid_edges) - 1)]
    for row in rows:
        bins[_bin_index(row[0], valid_edges)].append(row)

    rel_terms: list[float] = []
    res_terms: list[float] = []
    within_terms: list[float] = []
    binned_loss_terms: list[float] = []
    groups: list[dict[str, Any]] = []

    for index, members in enumerate(bins):
        left, right = valid_edges[index], valid_edges[index + 1]
        if not members:
            groups.append({
                "count": 0, "mass": 0.0, "mean_forecast": None,
                "event_rate": None, "left": left, "right": right,
                "within_variance": None, "within_covariance": None,
            })
            continue

        group_weight = fsum(weight for _, _, weight in members)
        mass = group_weight / weight_sum
        p_bar = fsum(weight * p for p, _, weight in members) / group_weight
        q_g = fsum(weight * y for _, y, weight in members) / group_weight
        variance = fsum(weight * (p - p_bar) ** 2 for p, _, weight in members) / group_weight
        covariance = fsum(weight * (p - p_bar) * (y - q_g) for p, y, weight in members) / group_weight
        rel_terms.append(mass * (p_bar - q_g) ** 2)
        res_terms.append(mass * (q_g - q) ** 2)
        within_terms.append(mass * (variance - 2.0 * covariance))
        binned_loss_terms.append(fsum(weight * (p_bar - y) ** 2 for _, y, weight in members) / weight_sum)
        groups.append({
            "count": len(members), "mass": mass, "mean_forecast": p_bar,
            "event_rate": q_g, "left": left, "right": right,
            "within_variance": variance, "within_covariance": covariance,
        })

    rel = fsum(rel_terms)
    res = fsum(res_terms)
    within = fsum(within_terms)
    binned = fsum(binned_loss_terms)
    raw = float(batch["brier"])
    residual = raw - (rel - res + unc + within)
    report = _base(BINNED, manifest_hash)
    report.update(
        status="COMPUTABLE", honesty="OBSERVED", raw_brier=raw,
        binned_brier=binned, reliability=rel, resolution=res,
        uncertainty=unc, within_correction=within,
        reconstruction_residual=residual, singleton_fraction=None,
        bin_edges=valid_edges, groups=groups,
    )
    if abs(residual) > TOLERANCE:
        report.update(status="NOT_COMPUTABLE", honesty="NOT_COMPUTABLE", reasons=["NUMERICAL_IDENTITY_FAILURE"])
    return report


def decompose(request: Any) -> dict[str, Any]:
    if not isinstance(request, dict):
        return _refuse(EXACT, "", "INVALID_MEMBER")
    manifest = request.get("manifest")
    method = request.get("method")
    if not isinstance(manifest, dict):
        return _refuse(method if method in {EXACT, BINNED} else EXACT, "", "INVALID_MEMBER")
    manifest_hash = manifest.get("manifest_hash", "")
    try:
        if method == EXACT:
            return exact_murphy(manifest)
        if method == BINNED:
            return binned_murphy(manifest, request.get("bin_edges"))
    except BatchContractError as exc:
        return _refuse(method if method in {EXACT, BINNED} else EXACT, manifest_hash, exc.reason)
    return _refuse(EXACT, manifest_hash, "INVALID_MEMBER")


def murphy_elementary_integral(p: float, y: int) -> float:
    """Exact integral of the registered factor-two elementary Murphy loss."""
    if type(p) not in (int, float) or not isfinite(float(p)) or not 0 <= p <= 1:
        raise ValueError("p must be finite in [0,1]")
    if type(y) not in (int, float) or y not in (0, 1):
        raise ValueError("y must be binary")
    p = float(p)
    return p * p if y == 0 else (1.0 - p) ** 2


# Provenance: Trutina Spec 000 / T04B; T04A contract baseline d6a0af93.
