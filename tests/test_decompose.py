import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from brier.decompose import (
    BINNED,
    EXACT,
    binned_murphy,
    exact_murphy,
    murphy_elementary_integral,
)
from brier.score import score

ROOT = Path(__file__).resolve().parents[1]
REPORT_SCHEMA = json.loads((ROOT / "contracts/brier.decompose.report.v0.schema.json").read_text())
REPORT_VALIDATOR = Draft202012Validator(REPORT_SCHEMA)
HASH = "b" * 64


def settled(case_id, p, y, weight=1.0):
    return {
        "case_id": case_id,
        "forecast_id": f"forecast-{case_id}",
        "forecast_revision": "r1",
        "event_id": f"event-{case_id}",
        "issued_at": "2026-09-12T10:00:00Z",
        "p": p,
        "weight": weight,
        "state": "SETTLED",
        "y": y,
        "settlement": "TRUE" if y == 1 else "FALSE",
        "settled_by": "operator",
        "settled_at": "2026-09-12T12:00:00Z",
        "settlement_ref": f"settlement-{case_id}",
    }


def manifest(rows):
    return {
        "schema": "brier.batch.input.v0",
        "specialist": "abx.brier",
        "display": "Trutina",
        "mode": "BATCH",
        "cohort_id": "cohort-decompose",
        "corpus_ref": "corpus-decompose",
        "manifest_hash": HASH,
        "forecast_version": "v1",
        "event_definition": "binary event",
        "positive_label": 1,
        "horizon": "24h",
        "issued_window": {
            "start": "2026-09-12T00:00:00Z",
            "end": "2026-09-13T00:00:00Z",
        },
        "settlement_cutoff": "2026-09-12T12:00:00Z",
        "snapshot_ref": "snapshot-decompose",
        "snapshot_as_of": "2026-09-12T12:00:00Z",
        "eligibility_policy": "settled-at-cutoff-v1",
        "weight_policy": "equal-case-v1",
        "member_order": "case_id-ascending",
        "members": rows,
    }


def checked(report):
    REPORT_VALIDATOR.validate(report)
    assert report["forecast_eligible"] is False
    assert report["can_promote"] is False
    assert report["weight_mutation"] is False
    assert report["phenomenal"] is False
    assert report["ledger_id"] is None
    return report


def test_a17_exact_murphy_identity():
    rows = [
        settled("a", 0.25, 0),
        settled("b", 0.25, 1),
        settled("c", 0.75, 0),
        settled("d", 0.75, 1),
    ]
    report = checked(exact_murphy(manifest(rows)))
    assert report["method"] == EXACT
    assert report["raw_brier"] == pytest.approx(0.3125)
    assert report["reliability"] == pytest.approx(0.0625)
    assert report["resolution"] == pytest.approx(0.0)
    assert report["uncertainty"] == pytest.approx(0.25)
    assert report["reconstruction_residual"] == pytest.approx(0.0, abs=1e-12)
    assert report["singleton_fraction"] == 0.0


def test_a18_binned_identity_requires_negative_within_correction():
    rows = [settled("a", 0.1, 0), settled("b", 0.4, 1)]
    report = checked(binned_murphy(manifest(rows), [0.0, 1.0]))
    assert report["method"] == BINNED
    assert report["raw_brier"] == pytest.approx(0.185)
    assert report["binned_brier"] == pytest.approx(0.3125)
    assert report["within_correction"] == pytest.approx(-0.1275)
    assert report["reconstruction_residual"] == pytest.approx(0.0, abs=1e-12)


def test_a19_empty_bins_ties_endpoint_singletons_and_single_class_are_defined():
    rows = [settled("a", 0.0, 0), settled("b", 0.5, 0), settled("c", 1.0, 0)]
    binned = checked(binned_murphy(manifest(rows), [0.0, 0.25, 0.5, 0.75, 1.0]))
    assert [group["count"] for group in binned["groups"]] == [1, 0, 1, 1]
    assert binned["groups"][1]["mean_forecast"] is None
    assert binned["groups"][3]["mean_forecast"] == 1.0
    assert binned["uncertainty"] == 0.0
    assert binned["reconstruction_residual"] == pytest.approx(0.0, abs=1e-12)

    exact = checked(exact_murphy(manifest(rows)))
    assert exact["singleton_fraction"] == 1.0
    assert exact["uncertainty"] == 0.0
    assert exact["reconstruction_residual"] == pytest.approx(0.0, abs=1e-12)


def test_a19_invalid_bin_edges_fail_closed():
    payload = manifest([settled("a", 0.5, 1)])
    for edges in ([0.1, 1.0], [0.0, 0.5, 0.5, 1.0], [0.0, 0.8], [0.0, float("nan"), 1.0]):
        report = checked(binned_murphy(payload, edges))
        assert report["status"] == "NOT_COMPUTABLE"
        assert report["reasons"] == ["INVALID_BIN_EDGES"]


def test_a20_elementary_murphy_integral_matches_binary_brier():
    assert murphy_elementary_integral(0.8, 1) == pytest.approx(0.04)
    assert murphy_elementary_integral(0.8, 0) == pytest.approx(0.64)


def test_public_dispatch_exact_and_binned_reports():
    cohort = manifest([
        settled("a", 0.25, 0),
        settled("b", 0.25, 1),
        settled("c", 0.75, 0),
        settled("d", 0.75, 1),
    ])
    exact_request = {
        "schema": "brier.decompose.input.v0",
        "specialist": "abx.brier",
        "display": "Trutina",
        "mode": "DECOMPOSE",
        "manifest": cohort,
        "method": EXACT,
        "bin_edges": None,
    }
    exact = checked(score(exact_request))
    assert exact["status"] == "COMPUTABLE"

    binned_request = dict(exact_request)
    binned_request["method"] = BINNED
    binned_request["bin_edges"] = [0.0, 0.5, 1.0]
    binned = checked(score(binned_request))
    assert binned["status"] == "COMPUTABLE"


def test_registered_partial_manifest_fails_closed_as_decompose_report():
    request = {
        "schema": "brier.decompose.input.v0",
        "specialist": "abx.brier",
        "display": "Trutina",
        "mode": "DECOMPOSE",
        "manifest": {"schema": "brier.batch.input.v0", "manifest_hash": HASH},
        "method": EXACT,
        "bin_edges": None,
    }
    report = checked(score(request))
    assert report["status"] == "NOT_COMPUTABLE"
    assert report["reasons"] == ["INVALID_MEMBER"]


def test_unregistered_extra_top_level_field_uses_legacy_refusal_packet():
    request = {
        "schema": "brier.decompose.input.v0",
        "specialist": "abx.brier",
        "display": "Trutina",
        "mode": "DECOMPOSE",
        "manifest": manifest([settled("a", 0.8, 1)]),
        "method": EXACT,
        "bin_edges": None,
        "runtime_enabled": True,
    }
    packet = score(request)
    assert packet["schema"] == "brier.score.v0"
    assert packet["mode"] == "DECOMPOSE"
    assert packet["honesty"] == "NOT_COMPUTABLE"
    assert packet["failure"] == "NOT_COMPUTABLE"


def test_t05_and_other_diagnostics_remain_closed():
    malformed = score({"mode": "DECOMPOSE", "method": "CORP_PAV_V1"})
    assert malformed["schema"] == "brier.score.v0"
    assert malformed["honesty"] == "NOT_COMPUTABLE"
    assert malformed["failure"] == "NOT_COMPUTABLE"

    interval_mode = score({"mode": "PROJECT"})
    assert interval_mode["honesty"] == "NOT_COMPUTABLE"
    assert interval_mode["can_promote"] is False


def test_decompose_report_has_no_interval_surface_before_t05():
    report = checked(exact_murphy(manifest([settled("a", 0.8, 1)])))
    assert "interval" not in report
