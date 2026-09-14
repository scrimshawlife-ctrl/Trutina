import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from brier.uncertainty import RNG_VERSION, estimate_interval

ROOT = Path(__file__).resolve().parents[1]
REPORT = json.loads((ROOT / "contracts/brier.interval.report.v0.schema.json").read_text())
VALIDATOR = Draft202012Validator(REPORT)
HASH = "d" * 64


def request(
    *,
    estimand="BRIER_MEAN",
    method="IID_PERCENTILE_BOOTSTRAP_V1",
    seed=17,
    replicates=400,
):
    payload = {
        "schema": "brier.interval.request.v0",
        "specialist": "abx.brier",
        "display": "Trutina",
        "estimand": estimand,
        "method": method,
        "manifest_hash": HASH,
        "confidence_level": 0.95,
        "seed": seed,
        "rng_version": RNG_VERSION,
        "replicates": replicates,
        "resampling_unit": "CASE",
        "sampling_assumption": "IID",
        "weight_design": "EQUAL_FIXED",
        "cluster_field": None,
        "block_length": None,
        "reference_id": None,
        "matched_reference_hash": None,
    }
    if estimand in {"PAIRED_DELTA", "BSS"}:
        payload["reference_id"] = "reference-v1"
        payload["matched_reference_hash"] = HASH
    if method == "CLUSTER_PERCENTILE_BOOTSTRAP_V1":
        payload.update(
            resampling_unit="CLUSTER",
            sampling_assumption="INDEPENDENT_CLUSTERS",
            cluster_field="cluster_id",
        )
    elif method == "MOVING_BLOCK_PERCENTILE_BOOTSTRAP_V1":
        payload.update(
            resampling_unit="MOVING_BLOCK",
            sampling_assumption="APPROX_STATIONARY_SERIAL",
            block_length=2,
        )
    return payload


def rows(*, paired=False, clustered=False):
    model = [0.01, 0.04, 0.16, 0.36, 0.09, 0.25]
    reference = [0.04, 0.09, 0.25, 0.49, 0.16, 0.36]
    out = []
    for index, loss in enumerate(model):
        row = {"case_id": f"c{index}", "model_loss": loss, "weight": 1.0}
        if paired:
            row["reference_loss"] = reference[index]
        if clustered:
            row["cluster_id"] = f"g{index // 2}"
        out.append(row)
    return out


def checked(payload, records):
    report = estimate_interval(payload, records)
    VALIDATOR.validate(report)
    return report


def test_a21_fixed_seed_and_version_are_reproducible():
    payload = request(seed=101, replicates=500)
    first = checked(payload, rows())
    second = checked(payload, rows())
    assert first == second
    assert first["status"] == "COMPUTABLE"
    assert first["reason"] is None
    assert first["replicates_valid"] == 500
    assert first["rng_version"] == RNG_VERSION
    assert first["lower"] <= first["upper"]


def test_a21_wrong_rng_version_is_explicitly_unavailable():
    payload = request()
    payload["rng_version"] = "ambient-python-random"
    report = checked(payload, rows())
    assert report["status"] == "NOT_COMPUTABLE"
    assert report["reason"] == "INVALID_DESIGN"


def test_a22_paired_delta_resamples_model_and_reference_together():
    payload = request(estimand="PAIRED_DELTA", replicates=500)
    report = checked(payload, rows(paired=True))
    assert report["status"] == "COMPUTABLE"
    assert report["zero_reference_replicates"] == 0
    assert report["lower"] <= report["upper"]


def test_a22_clustered_design_resamples_whole_declared_clusters():
    payload = request(method="CLUSTER_PERCENTILE_BOOTSTRAP_V1", replicates=300)
    report = checked(payload, rows(clustered=True))
    assert report["status"] == "COMPUTABLE"
    assert report["resampling_unit"] == "CLUSTER"


def test_a22_moving_block_design_uses_declared_block_length():
    payload = request(method="MOVING_BLOCK_PERCENTILE_BOOTSTRAP_V1", replicates=300)
    report = checked(payload, rows())
    assert report["status"] == "COMPUTABLE"
    assert report["resampling_unit"] == "MOVING_BLOCK"
    assert report["block_length"] == 2


def test_a22_missing_sampling_design_is_not_computable():
    payload = request()
    payload.pop("sampling_assumption")
    report = checked(payload, rows())
    assert report["status"] == "NOT_COMPUTABLE"
    assert report["reason"] == "SAMPLING_DESIGN_UNKNOWN"


def test_a23_one_case_and_constant_loss_are_degenerate_not_zero_width():
    payload = request(replicates=100)
    one = checked(payload, [{"case_id": "only", "model_loss": 0.25, "weight": 1.0}])
    assert one["status"] == "NOT_COMPUTABLE"
    assert one["reason"] == "DEGENERATE_SAMPLE"
    assert one["lower"] is None and one["upper"] is None

    constant = checked(
        payload,
        [
            {"case_id": "a", "model_loss": 0.25, "weight": 1.0},
            {"case_id": "b", "model_loss": 0.25, "weight": 1.0},
        ],
    )
    assert constant["status"] == "NOT_COMPUTABLE"
    assert constant["reason"] == "DEGENERATE_SAMPLE"
    assert constant["lower"] is None and constant["upper"] is None


def test_a23_zero_reference_bss_replicates_are_reported_not_dropped():
    payload = request(estimand="BSS", seed=3, replicates=500)
    records = [
        {"case_id": "a", "model_loss": 0.01, "reference_loss": 0.0, "weight": 1.0},
        {"case_id": "b", "model_loss": 0.25, "reference_loss": 0.25, "weight": 1.0},
    ]
    report = checked(payload, records)
    assert report["status"] == "NOT_COMPUTABLE"
    assert report["reason"] == "ZERO_REFERENCE_REPLICATE"
    assert report["zero_reference_replicates"] > 0
    assert report["replicates_valid"] < report["replicates_requested"]
    assert report["lower"] is None and report["upper"] is None


def test_a23_paired_delta_can_still_report_when_reference_loss_can_be_zero():
    payload = request(estimand="PAIRED_DELTA", seed=3, replicates=500)
    records = [
        {"case_id": "a", "model_loss": 0.01, "reference_loss": 0.0, "weight": 1.0},
        {"case_id": "b", "model_loss": 0.25, "reference_loss": 0.25, "weight": 1.0},
    ]
    report = checked(payload, records)
    assert report["status"] == "COMPUTABLE"
    assert report["reason"] is None


def test_cluster_requires_two_independent_units():
    payload = request(method="CLUSTER_PERCENTILE_BOOTSTRAP_V1")
    records = rows(clustered=True)
    for row in records:
        row["cluster_id"] = "same"
    report = checked(payload, records)
    assert report["status"] == "NOT_COMPUTABLE"
    assert report["reason"] == "DEGENERATE_SAMPLE"


def test_runtime_does_not_accept_clock_or_implicit_design_shortcuts():
    payload = request()
    payload["seed"] = -1
    report = checked(payload, rows())
    assert report["status"] == "NOT_COMPUTABLE"
    assert report["reason"] == "INVALID_DESIGN"
