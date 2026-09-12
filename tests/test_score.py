from decimal import Decimal

from brier.score import score


def _settled(p, y, settlement="TRUE"):
    return {
        "payload_class": "settled_forecast",
        "p": p,
        "y": y,
        "settlement": settlement,
        "settled_by": "operator",
        "corpus_ref": "E-B0",
    }


def test_score_true_08() -> None:
    pkt = score(_settled(0.8, 1))
    assert pkt["schema"] == "brier.score.v0"
    assert pkt["specialist"] == "abx.brier"
    assert pkt["display"] == "Trutina"
    assert pkt["mode"] == "SCORE"
    assert pkt["formula"] == "BRIER_BINARY_V1"
    assert pkt["brier"] == 0.04
    assert pkt["honesty"] == "OBSERVED"
    assert pkt["forecast_eligible"] is False
    assert pkt["can_promote"] is False
    assert pkt["weight_mutation"] is False
    assert pkt["ledger_id"] is None
    assert pkt["failure"] is None


def test_score_false_08() -> None:
    pkt = score(_settled(0.8, 0, settlement="FALSE"))
    assert pkt["brier"] == 0.64


def test_forecast_request_refused() -> None:
    pkt = score({"payload_class": "forecast_request", "p": 0.8, "settled_by": "operator"})
    assert pkt["brier"] is None
    assert pkt["failure"] == "NOT_COMPUTABLE"
    assert pkt["honesty"] == "NOT_COMPUTABLE"


def test_void_refused() -> None:
    pkt = score(_settled(0.8, 1, settlement="VOID"))
    assert pkt["failure"] == "NOT_COMPUTABLE"
    assert pkt["brier"] is None


def test_slang_refused() -> None:
    pkt = score({"payload_class": "slang_atom", "settled_by": "operator"})
    assert pkt["failure"] == "SPECIALIST_LANE_VIOLATION"


def test_missing_payload_class_refused() -> None:
    pkt = score({"p": 0.8, "y": 1, "settlement": "TRUE", "settled_by": "operator"})
    assert pkt["failure"] == "SPECIALIST_LANE_VIOLATION"
    assert pkt["brier"] is None


def test_missing_settled_by() -> None:
    pkt = score({"payload_class": "settled_forecast", "p": 0.8, "y": 1, "settlement": "TRUE"})
    assert pkt["failure"] == "NOT_COMPUTABLE"


def test_missing_settlement_refused() -> None:
    pkt = score({"payload_class": "settled_forecast", "p": 0.8, "y": 1, "settled_by": "operator"})
    assert pkt["failure"] == "NOT_COMPUTABLE"
    assert pkt["brier"] is None


def test_non_binary_outcome_refused() -> None:
    pkt = score(_settled(0.8, 2, settlement="TRUE"))
    assert pkt["failure"] == "NOT_COMPUTABLE"
    assert pkt["brier"] is None


def test_boolean_outcome_refused() -> None:
    pkt = score(_settled(0.8, True, settlement="TRUE"))
    assert pkt["failure"] == "NOT_COMPUTABLE"
    assert pkt["brier"] is None


def test_string_outcome_refused() -> None:
    pkt = score(_settled(0.8, "1", settlement="TRUE"))
    assert pkt["failure"] == "NOT_COMPUTABLE"
    assert pkt["brier"] is None


def test_decimal_outcome_refused() -> None:
    pkt = score(_settled(0.8, Decimal("1"), settlement="TRUE"))
    assert pkt["failure"] == "NOT_COMPUTABLE"
    assert pkt["brier"] is None


def test_settlement_outcome_mismatch_refused() -> None:
    pkt = score(_settled(0.8, 1, settlement="FALSE"))
    assert pkt["failure"] == "NOT_COMPUTABLE"
    assert pkt["brier"] is None


def test_batch_stub() -> None:
    pkt = score({**_settled(0.8, 1), "mode": "BATCH"})
    assert pkt["mode"] == "BATCH"
    assert pkt["failure"] == "NOT_COMPUTABLE"
    assert pkt["brier"] is None


def test_unknown_mode_is_preserved_when_refused() -> None:
    pkt = score({**_settled(0.8, 1), "mode": "UNKNOWN"})
    assert pkt["mode"] == "UNKNOWN"
    assert pkt["failure"] == "NOT_COMPUTABLE"
    assert pkt["brier"] is None
