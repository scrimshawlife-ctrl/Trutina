from copy import deepcopy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from brier.batch import aggregate_batch, compare_reference
from brier.score import score

ROOT = Path(__file__).resolve().parents[1]
REPORT_SCHEMA = json.loads((ROOT / "contracts/brier.batch.report.v0.schema.json").read_text())
REPORT_VALIDATOR = Draft202012Validator(REPORT_SCHEMA, format_checker=FormatChecker())
HASH = "a" * 64


def settled(case_id, p, y, weight=1.0, *, issued_at="2026-09-12T10:00:00Z", settled_at="2026-09-12T12:00:00Z"):
    return {
        "case_id": case_id,
        "forecast_id": f"forecast-{case_id}",
        "forecast_revision": "r1",
        "event_id": f"event-{case_id}",
        "issued_at": issued_at,
        "p": p,
        "weight": weight,
        "state": "SETTLED",
        "y": y,
        "settlement": "TRUE" if y == 1 else "FALSE",
        "settled_by": "operator",
        "settled_at": settled_at,
        "settlement_ref": f"settlement-{case_id}",
    }


def void(case_id="void-1"):
    return {
        "case_id": case_id,
        "forecast_id": f"forecast-{case_id}",
        "forecast_revision": "r1",
        "event_id": f"event-{case_id}",
        "issued_at": "2026-09-12T10:00:00Z",
        "p": 0.5,
        "weight": 1.0,
        "state": "VOID",
        "settlement": "VOID",
        "settled_by": "operator",
        "settled_at": "2026-09-12T12:00:00Z",
        "settlement_ref": f"settlement-{case_id}",
        "void_reason": "cancelled",
    }


def unsettled(case_id="open-1"):
    return {
        "case_id": case_id,
        "forecast_id": f"forecast-{case_id}",
        "forecast_revision": "r1",
        "event_id": f"event-{case_id}",
        "issued_at": "2026-09-12T10:00:00Z",
        "p": 0.5,
        "weight": 1.0,
        "state": "UNSETTLED",
    }


def manifest(members):
    return {
        "schema": "brier.batch.input.v0",
        "specialist": "abx.brier",
        "display": "Trutina",
        "mode": "BATCH",
        "cohort_id": "cohort-001",
        "corpus_ref": "corpus-001",
        "manifest_hash": HASH,
        "forecast_version": "v1",
        "event_definition": "binary event",
        "positive_label": 1,
        "horizon": "24h",
        "issued_window": {"start": "2026-09-12T00:00:00Z", "end": "2026-09-13T00:00:00Z"},
        "settlement_cutoff": "2026-09-12T12:00:00Z",
        "snapshot_ref": "snapshot-001",
        "snapshot_as_of": "2026-09-12T12:00:00Z",
        "eligibility_policy": "settled-at-cutoff-v1",
        "weight_policy": "equal-case-v1",
        "member_order": "case_id-ascending",
        "members": members,
    }


def checked(payload):
    report = aggregate_batch(payload)
    REPORT_VALIDATOR.validate(report)
    assert report["forecast_eligible"] is False
    assert report["can_promote"] is False
    assert report["weight_mutation"] is False
    assert report["phenomenal"] is False
    assert report["ledger_id"] is None
    return report


def test_a10_weighted_and_uniform_brier():
    weighted = checked(manifest([settled("a", 0.8, 1, 1), settled("b", 0.8, 0, 3)]))
    assert weighted["weight_sum"] == pytest.approx(4.0)
    assert weighted["sum_weighted_loss"] == pytest.approx(1.96)
    assert weighted["brier"] == pytest.approx(0.49)
    uniform = checked(manifest([settled("a", 0.8, 1), settled("b", 0.8, 0)]))
    assert uniform["brier"] == pytest.approx(0.34)


def test_a11_empty_void_unsettled_and_zero_weight():
    empty = checked(manifest([]))
    assert empty["brier"] is None and empty["reasons"] == ["EMPTY_COHORT"]
    excluded = checked(manifest([void(), unsettled()]))
    assert excluded["n_void"] == 1 and excluded["n_unsettled"] == 1
    assert excluded["brier"] is None and excluded["reasons"] == ["EMPTY_COHORT"]
    zero = checked(manifest([settled("z", 0.8, 1, 0)]))
    assert zero["n_zero_weight"] == 1
    assert zero["brier"] is None and zero["reasons"] == ["ZERO_WEIGHT"]


def test_a12_invalid_weight_duplicate_and_contradiction_fail_whole_request():
    bad = manifest([settled("a", 0.8, 1, -1)])
    assert checked(bad)["reasons"] == ["INVALID_MEMBER"]
    dup = manifest([settled("a", 0.8, 1), settled("a", 0.7, 1)])
    assert checked(dup)["reasons"] == ["DUPLICATE_CASE"]
    conflict = manifest([settled("a", 0.8, 1)])
    conflict["members"][0]["settlement"] = "FALSE"
    assert checked(conflict)["reasons"] == ["INVALID_MEMBER"]


def test_a13_order_and_positive_weight_scaling_invariant():
    rows = [settled("b", 0.8, 0, 3), settled("a", 0.8, 1, 1)]
    first = checked(manifest(rows))
    second = checked(manifest(list(reversed(deepcopy(rows)))))
    scaled_rows = deepcopy(rows)
    for row in scaled_rows:
        row["weight"] *= 7
    scaled = checked(manifest(scaled_rows))
    assert first["brier"] == pytest.approx(second["brier"], abs=1e-12, rel=1e-12)
    assert first["brier"] == pytest.approx(scaled["brier"], abs=1e-12, rel=1e-12)


def test_a14_brier_skill_score_examples():
    assert compare_reference(0.125, 0.25)["bss"] == pytest.approx(0.5)
    assert compare_reference(0.5, 0.25)["bss"] == pytest.approx(-1.0)


def test_a15_zero_missing_and_mismatched_reference_keep_model_available():
    zero = compare_reference(0.0, 0.0)
    assert zero["bss"] is None and zero["reason"] == "ZERO_REFERENCE_LOSS"
    missing = compare_reference(0.125, None)
    assert missing["bss"] is None and missing["reason"] == "REFERENCE_MISMATCH"
    mismatch = compare_reference(0.125, 0.25, matched_cases=False)
    assert mismatch["bss"] is None and mismatch["reason"] == "REFERENCE_MISMATCH"


def test_a16_reference_training_after_issue_cutoff_is_leakage():
    result = compare_reference(
        0.125,
        0.25,
        training_cutoff="2026-09-12T11:00:00Z",
        issue_cutoff="2026-09-12T10:00:00Z",
    )
    assert result["bss"] is None
    assert result["paired_delta"] is None
    assert result["reason"] == "REFERENCE_LEAKAGE"


def test_a25_cutoff_inclusive_and_timezone_normalized():
    at_cutoff = checked(manifest([settled("a", 0.8, 1, settled_at="2026-09-12T12:00:00Z")]))
    equivalent = checked(manifest([settled("a", 0.8, 1, settled_at="2026-09-12T05:00:00-07:00")]))
    assert at_cutoff["brier"] == pytest.approx(equivalent["brier"])


def test_a26_temporal_and_snapshot_failures():
    late = checked(manifest([settled("a", 0.8, 1, settled_at="2026-09-12T12:00:01Z")]))
    assert late["reasons"] == ["SETTLEMENT_AFTER_CUTOFF"]
    before = checked(manifest([settled("a", 0.8, 1, issued_at="2026-09-12T10:00:00Z", settled_at="2026-09-12T09:59:59Z")]))
    assert before["reasons"] == ["SETTLEMENT_BEFORE_ISSUE"]
    snap = manifest([settled("a", 0.8, 1)])
    snap["snapshot_as_of"] = "2026-09-12T11:59:59Z"
    with pytest.raises(Exception):
        aggregate_batch(snap)


def test_a27_void_and_unsettled_are_excluded_but_invalid_variant_refused():
    report = checked(manifest([settled("a", 0.8, 1), void(), unsettled()]))
    assert report["n_total"] == 3
    assert report["n_scored"] == 1
    assert report["n_void"] == 1
    assert report["n_unsettled"] == 1
    invalid = manifest([unsettled()])
    invalid["members"][0]["y"] = None
    assert checked(invalid)["reasons"] == ["INVALID_MEMBER"]


def test_a28_asof_snapshot_counts_and_runtime_dispatch():
    payload = manifest([settled("a", 0.8, 1), void(), unsettled()])
    report = score(payload)
    REPORT_VALIDATOR.validate(report)
    assert report["schema"] == "brier.batch.report.v0"
    assert report["n_scored"] == 1
    assert report["n_void"] == 1
    assert report["n_unsettled"] == 1
    assert report["brier"] == pytest.approx(0.04)


def test_decompose_remains_closed_after_t03():
    packet = score({"mode": "DECOMPOSE"})
    assert packet["schema"] == "brier.score.v0"
    assert packet["honesty"] == "NOT_COMPUTABLE"
    assert packet["failure"] == "NOT_COMPUTABLE"
