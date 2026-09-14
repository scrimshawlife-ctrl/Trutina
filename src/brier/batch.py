"""BATCH mode. Spec 000 / T03.

Deterministic cohort validation, weighted Brier aggregation, and matched-reference
Brier skill comparison. This module does not implement DECOMPOSE or grant any
promotion, forecast, ledger, or weight-mutation authority.
"""

from __future__ import annotations

from datetime import datetime, timezone
from math import fsum, isfinite
import re
from typing import Any

from .core import compute_atomic_brier

SCHEMA = "brier.batch.report.v0"
INPUT_SCHEMA = "brier.batch.input.v0"
SPECIALIST = "abx.brier"
DISPLAY = "Trutina"
FORMULA = "BRIER_BINARY_V1"
SCALE = "binary_0_1"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class BatchContractError(ValueError):
    """Fail-closed semantic contract error for a structurally valid manifest."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def _nonblank(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _number(value: Any, *, minimum: float = 0.0, maximum: float | None = None) -> float:
    if type(value) not in (int, float):
        raise BatchContractError("INVALID_MEMBER")
    value = float(value)
    if not isfinite(value) or value < minimum or (maximum is not None and value > maximum):
        raise BatchContractError("INVALID_MEMBER")
    return value


def _instant(value: Any) -> datetime:
    if not isinstance(value, str):
        raise BatchContractError("INVALID_MEMBER")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise BatchContractError("INVALID_MEMBER") from exc
    if parsed.tzinfo is None:
        raise BatchContractError("INVALID_MEMBER")
    return parsed.astimezone(timezone.utc)


def _base_report(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "specialist": SPECIALIST,
        "display": DISPLAY,
        "mode": "BATCH",
        "status": "NOT_COMPUTABLE",
        "honesty": "NOT_COMPUTABLE",
        "formula": FORMULA,
        "score_scale": SCALE,
        "manifest_hash": manifest["manifest_hash"],
        "corpus_ref": manifest["corpus_ref"],
        "snapshot_ref": manifest["snapshot_ref"],
        "snapshot_as_of": manifest["snapshot_as_of"],
        "settlement_cutoff": manifest["settlement_cutoff"],
        "n_total": len(manifest["members"]),
        "n_scored": 0,
        "n_void": 0,
        "n_unsettled": 0,
        "n_zero_weight": 0,
        "weight_sum": None,
        "sum_weighted_loss": None,
        "brier": None,
        "event_count": 0,
        "nonevent_count": 0,
        "prevalence": None,
        "weight_ess": None,
        "coverage": None,
        "reasons": [],
        "forecast_eligible": False,
        "can_promote": False,
        "weight_mutation": False,
        "phenomenal": False,
        "ledger_id": None,
    }


def _refuse(manifest: dict[str, Any], reason: str, *, counts: dict[str, int] | None = None) -> dict[str, Any]:
    report = _base_report(manifest)
    report["reasons"] = [reason]
    if counts:
        report.update(counts)
        total = report["n_total"]
        report["coverage"] = report["n_scored"] / total if total else None
    return report


def _validate_manifest_header(manifest: Any) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise BatchContractError("INVALID_MEMBER")
    required = {
        "schema", "specialist", "display", "mode", "manifest_hash", "corpus_ref",
        "snapshot_ref", "snapshot_as_of", "settlement_cutoff", "issued_window",
        "members", "event_definition", "horizon", "member_order", "weight_policy",
    }
    if not required.issubset(manifest):
        raise BatchContractError("CUTOFF_SNAPSHOT_REQUIRED")
    if manifest.get("schema") != INPUT_SCHEMA or manifest.get("specialist") != SPECIALIST or manifest.get("display") != DISPLAY or manifest.get("mode") != "BATCH":
        raise BatchContractError("INVALID_MEMBER")
    if not isinstance(manifest["manifest_hash"], str) or _SHA256.fullmatch(manifest["manifest_hash"]) is None:
        raise BatchContractError("INVALID_MEMBER")
    if not isinstance(manifest["members"], list):
        raise BatchContractError("INVALID_MEMBER")
    if not all(_nonblank(manifest[k]) for k in ("corpus_ref", "snapshot_ref", "event_definition", "horizon", "member_order", "weight_policy")):
        raise BatchContractError("INVALID_MEMBER")
    window = manifest["issued_window"]
    if not isinstance(window, dict) or set(window) != {"start", "end"}:
        raise BatchContractError("INVALID_MEMBER")
    start, end = _instant(window["start"]), _instant(window["end"])
    cutoff = _instant(manifest["settlement_cutoff"])
    snapshot = _instant(manifest["snapshot_as_of"])
    if not start < end:
        raise BatchContractError("MIXED_ESTIMAND")
    if snapshot != cutoff:
        raise BatchContractError("CUTOFF_SNAPSHOT_REQUIRED")
    return {"start": start, "end": end, "cutoff": cutoff}


def aggregate_batch(manifest: Any) -> dict[str, Any]:
    """Validate a T02 manifest and compute the T03 weighted Brier report."""
    times = _validate_manifest_header(manifest)
    report = _base_report(manifest)
    if not manifest["members"]:
        report["reasons"] = ["EMPTY_COHORT"]
        return report

    seen_cases: set[str] = set()
    seen_revisions: set[tuple[str, str]] = set()
    scored: list[tuple[str, float, float, int]] = []
    n_void = n_unsettled = n_zero = 0
    event_count = nonevent_count = 0

    try:
        for row in manifest["members"]:
            if not isinstance(row, dict):
                raise BatchContractError("INVALID_MEMBER")
            case_id = row.get("case_id")
            forecast_id = row.get("forecast_id")
            revision = row.get("forecast_revision")
            if not all(_nonblank(v) for v in (case_id, forecast_id, revision, row.get("event_id"))):
                raise BatchContractError("INVALID_MEMBER")
            if case_id in seen_cases or (forecast_id, revision) in seen_revisions:
                raise BatchContractError("DUPLICATE_CASE")
            seen_cases.add(case_id)
            seen_revisions.add((forecast_id, revision))

            issued = _instant(row.get("issued_at"))
            if not times["start"] <= issued < times["end"] or issued > times["cutoff"]:
                raise BatchContractError("MIXED_ESTIMAND")
            p = _number(row.get("p"), maximum=1.0)
            weight = _number(row.get("weight"))
            state = row.get("state")

            if state == "UNSETTLED":
                forbidden = {"y", "settlement", "settled_by", "settled_at", "settlement_ref", "void_reason"}
                if forbidden.intersection(row):
                    raise BatchContractError("INVALID_MEMBER")
                n_unsettled += 1
                continue

            if state not in {"SETTLED", "VOID"}:
                raise BatchContractError("INVALID_MEMBER")
            if not _nonblank(row.get("settled_by")) or not _nonblank(row.get("settlement_ref")):
                raise BatchContractError("INVALID_MEMBER")
            if "settled_at" not in row or row["settled_at"] is None:
                raise BatchContractError("SETTLEMENT_TIME_REQUIRED")
            settled = _instant(row["settled_at"])
            if settled < issued:
                raise BatchContractError("SETTLEMENT_BEFORE_ISSUE")
            if settled > times["cutoff"]:
                raise BatchContractError("SETTLEMENT_AFTER_CUTOFF")

            if state == "VOID":
                if row.get("settlement") != "VOID" or "y" in row or not _nonblank(row.get("void_reason")):
                    raise BatchContractError("INVALID_MEMBER")
                n_void += 1
                continue

            y = row.get("y")
            if type(y) not in (int, float) or y not in (0, 1):
                raise BatchContractError("INVALID_MEMBER")
            settlement = row.get("settlement")
            if settlement not in {"TRUE", "FALSE"} or ((settlement == "TRUE") != (y == 1)):
                raise BatchContractError("INVALID_MEMBER")
            y_int = int(y)
            loss = compute_atomic_brier(p, y_int)
            scored.append((case_id, weight, loss, y_int))
            if weight == 0:
                n_zero += 1
            if y_int:
                event_count += 1
            else:
                nonevent_count += 1
    except BatchContractError as exc:
        return _refuse(manifest, exc.reason)

    report.update(
        n_scored=len(scored),
        n_void=n_void,
        n_unsettled=n_unsettled,
        n_zero_weight=n_zero,
        event_count=event_count,
        nonevent_count=nonevent_count,
    )
    report["coverage"] = len(scored) / report["n_total"] if report["n_total"] else None
    if not scored:
        report["reasons"] = ["EMPTY_COHORT"]
        return report

    scored.sort(key=lambda item: item[0])
    weights = [item[1] for item in scored]
    weight_sum = fsum(weights)
    if weight_sum <= 0:
        report["reasons"] = ["ZERO_WEIGHT"]
        report["weight_sum"] = weight_sum
        return report

    weighted_losses = [weight * loss for _, weight, loss, _ in scored]
    sum_weighted_loss = fsum(weighted_losses)
    event_weight = fsum(weight for _, weight, _, y in scored if y == 1)
    weight_sq_sum = fsum(weight * weight for weight in weights)

    report.update(
        status="COMPUTABLE",
        honesty="OBSERVED",
        weight_sum=weight_sum,
        sum_weighted_loss=sum_weighted_loss,
        brier=sum_weighted_loss / weight_sum,
        prevalence=event_weight / weight_sum,
        weight_ess=(weight_sum * weight_sum / weight_sq_sum) if weight_sq_sum else None,
        reasons=[],
    )
    return report


def compare_reference(
    model_brier: float,
    reference_brier: float | None,
    *,
    matched_cases: bool = True,
    reference_id: str = "reference",
    reference_version: str = "v1",
    kind: str = "external_frozen",
    matched_manifest_hash: str = "",
    training_cutoff: str | None = None,
    issue_cutoff: str | None = None,
) -> dict[str, Any]:
    """Compute a bounded matched-reference comparison for A14-A16."""
    model = _number(model_brier, maximum=1.0)
    result = {
        "reference_id": reference_id,
        "reference_version": reference_version,
        "training_cutoff": training_cutoff,
        "kind": kind,
        "matched_manifest_hash": matched_manifest_hash,
        "brier": reference_brier,
        "bss": None,
        "paired_delta": None,
        "reason": None,
    }
    if not matched_cases or reference_brier is None:
        result["reason"] = "REFERENCE_MISMATCH"
        return result
    reference = _number(reference_brier, maximum=1.0)
    result["brier"] = reference
    if training_cutoff is not None and issue_cutoff is not None:
        if _instant(training_cutoff) > _instant(issue_cutoff):
            result["reason"] = "REFERENCE_LEAKAGE"
            return result
    result["paired_delta"] = model - reference
    if reference == 0:
        result["reason"] = "ZERO_REFERENCE_LOSS"
        return result
    result["bss"] = 1.0 - model / reference
    if 0 < reference < 1e-12:
        result["reason"] = "SMALL_REFERENCE_LOSS"
    return result


# Provenance: Trutina Spec 000 / T03; T02 contract baseline f808fc4.
