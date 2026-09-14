import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

from brier.score import score

ROOT = Path(__file__).resolve().parents[1]
INPUT_SCHEMA = json.loads((ROOT / "contracts/brier.batch.input.v0.schema.json").read_text())
REPORT_SCHEMA = json.loads((ROOT / "contracts/brier.batch.report.v0.schema.json").read_text())
INPUT_VALIDATOR = Draft202012Validator(INPUT_SCHEMA, format_checker=FormatChecker())
REPORT_VALIDATOR = Draft202012Validator(REPORT_SCHEMA, format_checker=FormatChecker())
HASH = "a" * 64


def member(state: str, suffix: str = "1") -> dict:
    base = {
        "case_id": f"case-{suffix}",
        "forecast_id": f"forecast-{suffix}",
        "forecast_revision": "r1",
        "event_id": f"event-{suffix}",
        "issued_at": "2026-09-12T10:00:00Z",
        "p": 0.8,
        "weight": 1.0,
        "state": state,
    }
    if state == "SETTLED":
        base.update(
            y=1,
            settlement="TRUE",
            settled_by="operator",
            settled_at="2026-09-12T12:00:00Z",
            settlement_ref=f"settlement-{suffix}",
        )
    elif state == "VOID":
        base.update(
            settlement="VOID",
            settled_by="operator",
            settled_at="2026-09-12T12:00:00Z",
            settlement_ref=f"settlement-{suffix}",
            void_reason="event cancelled",
        )
    return base


def manifest() -> dict:
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
        "issued_window": {
            "start": "2026-09-12T00:00:00Z",
            "end": "2026-09-13T00:00:00Z",
        },
        "settlement_cutoff": "2026-09-12T12:00:00Z",
        "snapshot_ref": "snapshot-001",
        "snapshot_as_of": "2026-09-12T12:00:00Z",
        "eligibility_policy": "settled-at-cutoff-v1",
        "weight_policy": "equal-case-v1",
        "member_order": "case_id-ascending",
        "members": [member("SETTLED", "1"), member("VOID", "2"), member("UNSETTLED", "3")],
    }


def report() -> dict:
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
        "corpus_ref": "corpus-001",
        "snapshot_ref": "snapshot-001",
        "snapshot_as_of": "2026-09-12T12:00:00Z",
        "settlement_cutoff": "2026-09-12T12:00:00Z",
        "n_total": 3,
        "n_scored": 1,
        "n_void": 1,
        "n_unsettled": 1,
        "n_zero_weight": 0,
        "weight_sum": 1.0,
        "sum_weighted_loss": 0.04,
        "brier": 0.04,
        "event_count": 1,
        "nonevent_count": 0,
        "prevalence": 1.0,
        "weight_ess": 1.0,
        "coverage": 1 / 3,
        "reasons": [],
        "forecast_eligible": False,
        "can_promote": False,
        "weight_mutation": False,
        "phenomenal": False,
        "ledger_id": None,
    }


def test_t02_input_contract_accepts_closed_member_union():
    INPUT_VALIDATOR.validate(manifest())


def test_t02_report_contract_accepts_bounded_future_shape():
    REPORT_VALIDATOR.validate(report())


@pytest.mark.parametrize("state", ["SETTLED", "VOID", "UNSETTLED"])
def test_t02_member_states_are_discriminated(state):
    payload = manifest()
    payload["members"] = [member(state)]
    INPUT_VALIDATOR.validate(payload)


def test_t02_unsettled_forbids_outcome_fields():
    payload = manifest()
    row = member("UNSETTLED")
    row["y"] = None
    payload["members"] = [row]
    with pytest.raises(ValidationError):
        INPUT_VALIDATOR.validate(payload)


def test_t02_void_forbids_y_and_requires_reason():
    payload = manifest()
    row = member("VOID")
    row.pop("void_reason")
    payload["members"] = [row]
    with pytest.raises(ValidationError):
        INPUT_VALIDATOR.validate(payload)


def test_t02_snapshot_linkage_is_structurally_required():
    payload = manifest()
    payload.pop("snapshot_ref")
    with pytest.raises(ValidationError):
        INPUT_VALIDATOR.validate(payload)


def test_t02_hash_and_unknown_fields_fail_closed():
    payload = manifest()
    payload["manifest_hash"] = "not-a-sha256"
    with pytest.raises(ValidationError):
        INPUT_VALIDATOR.validate(payload)
    payload = manifest()
    payload["runtime_enabled"] = True
    with pytest.raises(ValidationError):
        INPUT_VALIDATOR.validate(payload)


def test_t02_authority_flags_are_locked_false_and_ledger_null():
    payload = report()
    payload["can_promote"] = True
    with pytest.raises(ValidationError):
        REPORT_VALIDATOR.validate(payload)
    payload = report()
    payload["ledger_id"] = "ledger-1"
    with pytest.raises(ValidationError):
        REPORT_VALIDATOR.validate(payload)


def test_t02_does_not_activate_batch_runtime():
    packet = score({"mode": "BATCH", "payload_class": "settled_forecast"})
    assert packet["mode"] == "BATCH"
    assert packet["brier"] is None
    assert packet["honesty"] == "NOT_COMPUTABLE"
    assert packet["failure"] == "NOT_COMPUTABLE"
    assert packet["can_promote"] is False
    assert packet["weight_mutation"] is False
    assert packet["ledger_id"] is None
