import pytest

from brier.score import score


def test_a24_future_multiclass_arithmetic_and_current_refusal():
    probabilities = [0.2, 0.8]
    observed_index = 1
    unscaled = sum((p - (1 if index == observed_index else 0)) ** 2 for index, p in enumerate(probabilities))
    assert unscaled == pytest.approx(0.08)
    assert 0.5 * unscaled == pytest.approx(0.04)

    packet = score({
        "payload_class": "settled_forecast",
        "p": probabilities,
        "y": observed_index,
        "settlement": "TRUE",
        "settled_by": "operator",
    })
    assert packet["schema"] == "brier.score.v0"
    assert packet["brier"] is None
    assert packet["honesty"] == "NOT_COMPUTABLE"
    assert packet["failure"] == "NOT_COMPUTABLE"
    assert packet["can_promote"] is False
    assert packet["weight_mutation"] is False
    assert packet["ledger_id"] is None


def test_t06_does_not_add_extension_mode():
    packet = score({"mode": "MULTICLASS"})
    assert packet["schema"] == "brier.score.v0"
    assert packet["honesty"] == "NOT_COMPUTABLE"
    assert packet["failure"] == "NOT_COMPUTABLE"
