import pytest
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
    assert pkt["brier"] == pytest.approx(0.04, abs=1e-12, rel=1e-12)
    assert pkt["honesty"] == "OBSERVED"
    assert pkt["forecast_eligible"] is False
    assert pkt["can_promote"] is False
    assert pkt["weight_mutation"] is False
    assert pkt["ledger_id"] is None
    assert pkt["failure"] is None


def test_score_false_08() -> None:
    pkt = score(_settled(0.8, 0, settlement="FALSE"))
    assert pkt["brier"] == pytest.approx(0.64, abs=1e-12, rel=1e-12)


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


def test_missing_settled_by() -> None:
    pkt = score({"payload_class": "settled_forecast", "p": 0.8, "y": 1, "settlement": "TRUE"})
    assert pkt["failure"] == "NOT_COMPUTABLE"


def test_batch_stub() -> None:
    pkt = score({**_settled(0.8, 1), "mode": "BATCH"})
    assert pkt["mode"] == "BATCH"
    assert pkt["failure"] == "NOT_COMPUTABLE"
    assert pkt["brier"] is None
