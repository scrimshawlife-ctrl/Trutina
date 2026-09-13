"""SCORE acceptance A01-A09 and the binary-only boundary in A24."""
from copy import deepcopy
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import pytest

import brier


@pytest.fixture(scope="module")
def checked_score():
    schema = json.loads((Path(__file__).parents[1] / "contracts/brier.score.v0.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    def checked(atom):
        packet = brier.score(atom)
        validator.validate(packet)
        assert set(packet) == set(schema["properties"])
        assert packet["formula"] == "BRIER_BINARY_V1"
        for flag in ("forecast_eligible", "can_promote", "weight_mutation", "phenomenal"):
            assert packet[flag] is False
        assert packet["ledger_id"] is None
        assert json.loads(json.dumps(packet, allow_nan=False)) == packet
        if packet["brier"] is None:
            assert packet["honesty"] == "NOT_COMPUTABLE"
            assert packet["failure"] in ("NOT_COMPUTABLE", "SPECIALIST_LANE_VIOLATION")
        else:
            assert packet["honesty"] == "OBSERVED"
            assert packet["failure"] is None
        return packet
    return checked


def settled(p=.8, y=1):
    return {"payload_class": "settled_forecast", "p": p, "y": y,
            "settlement": "TRUE" if y == 1 else "FALSE", "settled_by": "operator", "corpus_ref": "E-B0"}


def refused(checked, atom, failure="NOT_COMPUTABLE", mode="SCORE"):
    packet = checked(atom)
    assert packet["brier"] is None
    assert packet["failure"] == failure
    assert packet["mode"] == mode
    return packet


@pytest.mark.parametrize("p,y,loss", [(0,0,0),(1,1,0),(0,1,1),(1,0,1),(.8,1,.04),(.8,0,.64),(.7,1,.09),(.5,0,.25),(.5,1,.25)])
def test_binary_arithmetic(checked_score, p, y, loss):
    packet = checked_score(settled(p,y))
    assert packet["brier"] == pytest.approx(loss, abs=1e-12, rel=1e-12)
    assert packet["corpus_ref"] == "E-B0"
    assert checked_score(settled(1-p,1-y))["brier"] == pytest.approx(loss, abs=1e-12, rel=1e-12)


def test_replay_and_input_immutability(checked_score):
    atom = {**settled(), "extra": {"unchanged": [1,2]}, "settled_at": "2026-09-12T12:00:00Z"}
    before = deepcopy(atom)
    first = checked_score(atom)
    assert checked_score(atom) == first
    assert atom == before
    assert "extra" not in first


@pytest.mark.parametrize("field", ["payload_class", "settlement", "settled_by", "p", "y"])
def test_missing_required(checked_score, field):
    atom = settled()
    del atom[field]
    refused(checked_score, atom)


@pytest.mark.parametrize("field", ["p", "y"])
@pytest.mark.parametrize("value", [-1, 2, float("nan"), float("inf"), -float("inf"), True, False, "1", None, [], {}, 10**400, [.2,.8]])
def test_invalid_numbers(checked_score, field, value):
    refused(checked_score, {**settled(), field: value})


@pytest.mark.parametrize("y", [.2, .9, 1.9])
def test_fractional_outcomes(checked_score, y):
    refused(checked_score, {**settled(), "y": y})


@pytest.mark.parametrize("atom", [None, [], "settled_forecast", 1, True])
def test_nonobject(checked_score, atom):
    refused(checked_score, atom)


@pytest.mark.parametrize("value", [None, [], {}, 1, True, "", "UNKNOWN"])
def test_invalid_mode(checked_score, value):
    refused(checked_score, {**settled(), "mode": value})


@pytest.mark.parametrize("mode", ["BATCH", "DECOMPOSE", "FUSION_ADVISORY", "ROUTER_MICRO", "GATE_ADVISORY", "PROJECT"])
def test_stubs_precede_payload_validation(checked_score, mode):
    refused(checked_score, {"mode": mode, "payload_class": "slang_atom", "corpus_ref": []}, mode=mode)


@pytest.mark.parametrize("payload", [None, [], {}, 1, True, "forecast_request"])
def test_invalid_or_unsettled_payload(checked_score, payload):
    refused(checked_score, {**settled(), "payload_class": payload})


@pytest.mark.parametrize("payload", ["slang_atom", "tradition_atom", "sign_atom", "route_atom", "other", ""])
def test_specialist_lanes(checked_score, payload):
    packet = refused(checked_score, {"payload_class": payload, "corpus_ref": {}}, "SPECIALIST_LANE_VIOLATION")
    assert packet["corpus_ref"] is None


@pytest.mark.parametrize("value", ["VOID", "FALSE", "true", "", None, [], {}, True])
def test_bad_or_contradictory_settlement(checked_score, value):
    refused(checked_score, {**settled(), "settlement": value})


def test_true_with_negative_outcome(checked_score):
    refused(checked_score, {**settled(.8,0), "settlement": "TRUE"})


@pytest.mark.parametrize("value", [None, "", " \t\n", True, 1, [], {}])
def test_invalid_operator(checked_score, value):
    refused(checked_score, {**settled(), "settled_by": value})


@pytest.mark.parametrize("value", ["", " \n", True, 1, [], {}])
def test_invalid_reference_is_sanitized(checked_score, value):
    assert refused(checked_score, {**settled(), "corpus_ref": value})["corpus_ref"] is None


@pytest.mark.parametrize("value", [None, "receipt-1", " receipt-1 "])
def test_optional_reference(checked_score, value):
    packet = checked_score({**settled(), "corpus_ref": value})
    assert packet["brier"] is not None
    assert packet["corpus_ref"] == value


@pytest.mark.parametrize("value", [None, "2026-09-12T12:00:00Z", "2026-09-12T05:00:00-07:00", "2024-02-29T23:59:59.123456+00:00"])
def test_optional_offset_timestamp(checked_score, value):
    assert checked_score({**settled(), "settled_at": value})["brier"] is not None


@pytest.mark.parametrize("value", ["", "2026-09-12", "2026-09-12T12:00:00", "2026-02-29T12:00:00Z", "2026-09-12T24:00:00Z", "2026-09-12T12:00:60Z", "2026-09-12T12:00:00+01:99", "2026-09-12T12:00:00+24:00", [], {}, 123, True])
def test_invalid_timestamp(checked_score, value):
    refused(checked_score, {**settled(), "settled_at": value})


@pytest.mark.parametrize("aliases_only", [False, True])
@pytest.mark.parametrize("y", [0.0, 1.0])
def test_numeric_alias_compatibility(checked_score, aliases_only, y):
    atom = {**settled(.8,y), "expected_probability": .8, "observed_outcome": int(y)}
    if aliases_only:
        del atom["p"]
        del atom["y"]
    assert checked_score(atom)["brier"] == pytest.approx((.8-y)**2)


@pytest.mark.parametrize("changes", [
    {"expected_probability": .7}, {"expected_probability": "0.8"}, {"expected_probability": None},
    {"p": None, "expected_probability": .8}, {"p": True, "expected_probability": 1},
    {"observed_outcome": 0}, {"observed_outcome": "1"}, {"observed_outcome": True},
    {"y": .9, "observed_outcome": 1}, {"y": None, "observed_outcome": 1},
])
def test_alias_conflicts_and_invalid_values(checked_score, changes):
    refused(checked_score, {**settled(), **changes})


@pytest.mark.parametrize("operation", [brier.emit_performance_ledger, brier.to_brier_score_packet, brier.to_brier_ledger_entry])
def test_deferred_exports_remain_closed(operation):
    with pytest.raises(NotImplementedError):
        operation()


# Provenance: Trutina Spec 001 / T01; specification baseline ecbf403.
