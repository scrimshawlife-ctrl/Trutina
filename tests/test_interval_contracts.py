import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[1]
REQUEST = json.loads((ROOT / "contracts/brier.interval.request.v0.schema.json").read_text())
REPORT = json.loads((ROOT / "contracts/brier.interval.report.v0.schema.json").read_text())
BATCH_REPORT = json.loads((ROOT / "contracts/brier.batch.report.v0.schema.json").read_text())
REQUEST_VALIDATOR = Draft202012Validator(REQUEST)
REPORT_VALIDATOR = Draft202012Validator(REPORT)
BATCH_REPORT_VALIDATOR = Draft202012Validator(BATCH_REPORT)
HASH = "c" * 64


def iid_request(estimand="BRIER_MEAN"):
    payload = {
        "schema": "brier.interval.request.v0",
        "specialist": "abx.brier",
        "display": "Trutina",
        "estimand": estimand,
        "method": "IID_PERCENTILE_BOOTSTRAP_V1",
        "manifest_hash": HASH,
        "confidence_level": 0.95,
        "seed": 7,
        "rng_version": "python-random-v1",
        "replicates": 2000,
        "resampling_unit": "CASE",
        "sampling_assumption": "IID",
        "weight_design": "EQUAL_FIXED",
        "cluster_field": None,
        "block_length": None,
        "reference_id": None,
        "matched_reference_hash": None,
    }
    if estimand in {"PAIRED_DELTA", "BSS"}:
        payload["reference_id"] = "ref-1"
        payload["matched_reference_hash"] = HASH
    return payload


def interval_report():
    return {
        "schema": "brier.interval.report.v0",
        "specialist": "abx.brier",
        "display": "Trutina",
        "estimand": "BRIER_MEAN",
        "method": "IID_PERCENTILE_BOOTSTRAP_V1",
        "confidence_level": 0.95,
        "seed": 7,
        "rng_version": "python-random-v1",
        "replicates_requested": 2000,
        "replicates_valid": 2000,
        "resampling_unit": "CASE",
        "block_length": None,
        "lower": 0.1,
        "upper": 0.3,
        "status": "COMPUTABLE",
        "reason": None,
        "zero_reference_replicates": 0,
    }


def batch_report(interval=None):
    return {
        "schema": "brier.batch.report.v0",
        "specialist": "abx.brier",
        "display": "Trutina",
        "mode": "BATCH",
        "status": "COMPUTABLE",
        "honesty": "OBSERVED",
        "formula": "BRIER_BINARY_V1",
        "score_scale": "binary_0_1",
        "manifest_hash": HASH,
        "corpus_ref": "c",
        "snapshot_ref": "s",
        "snapshot_as_of": "2026-09-12T12:00:00Z",
        "settlement_cutoff": "2026-09-12T12:00:00Z",
        "n_total": 2,
        "n_scored": 2,
        "n_void": 0,
        "n_unsettled": 0,
        "n_zero_weight": 0,
        "weight_sum": 2.0,
        "sum_weighted_loss": 0.5,
        "brier": 0.25,
        "event_count": 1,
        "nonevent_count": 1,
        "prevalence": 0.5,
        "weight_ess": 2.0,
        "coverage": 1.0,
        "baseline": None,
        "decomposition": None,
        "interval": interval,
        "reasons": [],
        "forecast_eligible": False,
        "can_promote": False,
        "weight_mutation": False,
        "phenomenal": False,
        "ledger_id": None,
    }


def test_iid_request_contract():
    REQUEST_VALIDATOR.validate(iid_request())


def test_cluster_request_requires_declared_cluster_field():
    payload = iid_request()
    payload.update(
        method="CLUSTER_PERCENTILE_BOOTSTRAP_V1",
        resampling_unit="CLUSTER",
        sampling_assumption="INDEPENDENT_CLUSTERS",
        cluster_field=None,
    )
    with pytest.raises(ValidationError):
        REQUEST_VALIDATOR.validate(payload)
    payload["cluster_field"] = "cluster_id"
    REQUEST_VALIDATOR.validate(payload)


def test_moving_block_requires_block_length():
    payload = iid_request()
    payload.update(
        method="MOVING_BLOCK_PERCENTILE_BOOTSTRAP_V1",
        resampling_unit="MOVING_BLOCK",
        sampling_assumption="APPROX_STATIONARY_SERIAL",
        block_length=None,
    )
    with pytest.raises(ValidationError):
        REQUEST_VALIDATOR.validate(payload)
    payload["block_length"] = 4
    REQUEST_VALIDATOR.validate(payload)


@pytest.mark.parametrize("estimand", ["PAIRED_DELTA", "BSS"])
def test_paired_estimands_require_reference_linkage(estimand):
    payload = iid_request(estimand)
    REQUEST_VALIDATOR.validate(payload)
    payload["reference_id"] = None
    with pytest.raises(ValidationError):
        REQUEST_VALIDATOR.validate(payload)


def test_interval_report_contract():
    REPORT_VALIDATOR.validate(interval_report())


def test_batch_report_accepts_registered_interval_or_null():
    BATCH_REPORT_VALIDATOR.validate(batch_report(None))
    BATCH_REPORT_VALIDATOR.validate(batch_report(interval_report()))


def test_unregistered_interval_shape_fails_closed():
    bad = interval_report()
    bad["clock_seeded"] = True
    with pytest.raises(ValidationError):
        BATCH_REPORT_VALIDATOR.validate(batch_report(bad))


def test_contract_cycle_does_not_claim_interval_runtime():
    # T05A registers data contracts only. Runtime tests for bootstrap belong to T05B.
    payload = batch_report(None)
    BATCH_REPORT_VALIDATOR.validate(payload)
    assert payload["interval"] is None
