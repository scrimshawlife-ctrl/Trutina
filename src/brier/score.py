"""SCORE mode. Spec 001. Packet brier.score.v0."""

from __future__ import annotations

from typing import Any

from .core import compute_atomic_brier

SCHEMA = "brier.score.v0"
SPECIALIST = "abx.brier"
DISPLAY = "Trutina"
FORMULA = "BRIER_BINARY_V1"
OTHER_ATOMS = {"slang_atom", "tradition_atom", "sign_atom", "route_atom"}
LIVE_MODES = {"SCORE"}
STUB_MODES = {"BATCH", "DECOMPOSE", "FUSION_ADVISORY", "ROUTER_MICRO", "GATE_ADVISORY", "PROJECT"}


def _base(*, mode: str, brier: float | None, honesty: str, failure: str | None, corpus_ref: str | None) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "specialist": SPECIALIST,
        "display": DISPLAY,
        "mode": mode,
        "formula": FORMULA,
        "brier": brier,
        "honesty": honesty,
        "forecast_eligible": False,
        "can_promote": False,
        "weight_mutation": False,
        "phenomenal": False,
        "ledger_id": None,
        "failure": failure,
        "corpus_ref": corpus_ref,
    }


def score(atom: dict[str, Any]) -> dict[str, Any]:
    payload = atom.get("payload_class")
    mode = atom.get("mode") or "SCORE"
    ref = atom.get("corpus_ref")

    if mode in STUB_MODES:
        return _base(mode=mode, brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)
    if mode not in LIVE_MODES:
        return _base(mode="SCORE", brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)

    if payload == "forecast_request":
        return _base(mode="SCORE", brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)
    if payload in OTHER_ATOMS:
        return _base(mode="SCORE", brier=None, honesty="NOT_COMPUTABLE", failure="SPECIALIST_LANE_VIOLATION", corpus_ref=ref)
    if payload not in (None, "settled_forecast"):
        return _base(mode="SCORE", brier=None, honesty="NOT_COMPUTABLE", failure="SPECIALIST_LANE_VIOLATION", corpus_ref=ref)

    settlement = atom.get("settlement")
    if settlement == "VOID":
        return _base(mode="SCORE", brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)
    if settlement not in ("TRUE", "FALSE", None):
        return _base(mode="SCORE", brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)
    if not atom.get("settled_by"):
        return _base(mode="SCORE", brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)

    p = atom.get("p", atom.get("expected_probability"))
    y = atom.get("y", atom.get("observed_outcome"))
    try:
        value = compute_atomic_brier(float(p), int(y))
    except (TypeError, ValueError):
        return _base(mode="SCORE", brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)

    return _base(mode="SCORE", brier=value, honesty="OBSERVED", failure=None, corpus_ref=ref)
