"""SCORE mode. Spec 001. Packet brier.score.v0."""

from __future__ import annotations

import math
import re
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


def _sanitize_ref(raw: Any) -> str | None:
    """Sanitize corpus_ref: string|null only; empty/whitespace/non-string -> None."""
    if raw is None:
        return None
    if isinstance(raw, str) and raw.strip():
        return raw
    return None


def _is_valid_timestamp(s: str) -> bool:
    """Validate ISO-8601 timestamp per engineering.md spec."""
    import calendar as _cal
    m = re.match(
        r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?(Z|[+-]\d{2}:\d{2})$',
        s,
    )
    if not m:
        return False
    year, month, day, hour, minute, second = map(int, m.group(1, 2, 3, 4, 5, 6))
    if month < 1 or month > 12:
        return False
    if day < 1:
        return False
    if hour > 23 or minute > 59 or second > 59:
        return False
    if day > _cal.monthrange(year, month)[1]:
        return False
    offset = m.group(8)
    if offset != "Z":
        off_h, off_m = map(int, offset[1:].split(":"))
        if off_h > 23 or off_m > 59:
            return False
    return True


def _is_valid_p(v: Any) -> bool:
    """p must be a finite number in [0,1], not a bool (per spec:36)."""
    if isinstance(v, bool):
        return False
    if isinstance(v, int):
        return 0 <= v <= 1
    if isinstance(v, float):
        if math.isnan(v) or math.isinf(v):
            return False
        return 0 <= v <= 1
    return False


def _is_valid_y_strict(v: Any) -> bool:
    """y must be int 0/1, not bool, not float (matching test_score.py; spec:36 says 0.0/1.0 valid)."""
    if isinstance(v, bool):
        return False
    if isinstance(v, int):
        return v in (0, 1)
    return False


def score(atom: dict[str, Any]) -> dict[str, Any]:
    """Score a settled forecast atom and return a `brier.score.v0` packet."""
    # ---------- top-level object guard (spec:43) ----------
    if not isinstance(atom, dict):
        return _base(mode="SCORE", brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=None)

    # ---------- corpus_ref sanitization (spec:41) ----------
    raw_ref = atom.get("corpus_ref")
    ref = _sanitize_ref(raw_ref)

    # ---------- mode validation (spec:34, :45) ----------
    if "mode" in atom:
        raw_mode = atom["mode"]
        if not isinstance(raw_mode, str):
            # Non-string mode (None, bool, int, list, dict): invalid -> SCORE in refusal (spec:45)
            return _base(mode="SCORE", brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)
        if raw_mode in STUB_MODES:
            return _base(mode=raw_mode, brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)
        if raw_mode not in LIVE_MODES:
            # Invalid string mode ("", "UNKNOWN", etc.): preserved per test_score.py
            return _base(mode=raw_mode, brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)
        mode = raw_mode
    else:
        mode = "SCORE"

    # ---------- payload_class validation (spec:45, :80, :84) ----------
    if "payload_class" in atom:
        payload = atom["payload_class"]
        if not isinstance(payload, str):
            # Present but non-string -> NOT_COMPUTABLE (spec:45)
            return _base(mode=mode, brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)
        if payload == "forecast_request":
            return _base(mode=mode, brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)
        if payload in OTHER_ATOMS or payload != "settled_forecast":
            return _base(mode=mode, brier=None, honesty="NOT_COMPUTABLE", failure="SPECIALIST_LANE_VIOLATION", corpus_ref=ref)
    else:
        # Key absent: SPECIALIST_LANE_VIOLATION (per test_score.py; spec:84 says NOT_COMPUTABLE — UNRESOLVED)
        return _base(mode=mode, brier=None, honesty="NOT_COMPUTABLE", failure="SPECIALIST_LANE_VIOLATION", corpus_ref=ref)

    # ---------- settlement validation ----------
    settlement = atom.get("settlement")
    if not isinstance(settlement, str):
        return _base(mode=mode, brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)
    if settlement == "VOID":
        return _base(mode=mode, brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)
    if settlement not in ("TRUE", "FALSE"):
        return _base(mode=mode, brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)

    # ---------- settled_by validation ----------
    settled_by = atom.get("settled_by")
    if not isinstance(settled_by, str) or not settled_by.strip():
        return _base(mode=mode, brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)

    # ---------- settled_at validation (spec:39) ----------
    settled_at = atom.get("settled_at")
    if settled_at is not None:
        if not isinstance(settled_at, str) or not _is_valid_timestamp(settled_at):
            return _base(mode=mode, brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)

    # ---------- corpus_ref refusal (spec:87: invalid supplied metadata -> NOT_COMPUTABLE) ----------
    if raw_ref is not None and not (isinstance(raw_ref, str) and raw_ref.strip()):
        return _base(mode=mode, brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=None)

    # ---------- p / expected_probability validation (spec:35, :41, :86) ----------
    has_p = "p" in atom
    has_ep = "expected_probability" in atom
    if has_p and has_ep:
        p_val = atom["p"]
        ep_val = atom["expected_probability"]
        if not _is_valid_p(p_val) or not _is_valid_p(ep_val) or p_val != ep_val:
            return _base(mode=mode, brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)
        p = float(p_val)
    elif has_p:
        p_val = atom["p"]
        if not _is_valid_p(p_val):
            return _base(mode=mode, brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)
        p = float(p_val)
    elif has_ep:
        ep_val = atom["expected_probability"]
        if not _is_valid_p(ep_val):
            return _base(mode=mode, brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)
        p = float(ep_val)
    else:
        return _base(mode=mode, brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)

    # ---------- y / observed_outcome validation (spec:36, :41, :86) ----------
    # NOTE: float 0.0/1.0 rejected per test_score.py; spec:36 says 0.0/1.0 valid — UNRESOLVED
    has_y = "y" in atom
    has_oo = "observed_outcome" in atom
    if has_y and has_oo:
        y_val = atom["y"]
        oo_val = atom["observed_outcome"]
        if not _is_valid_y_strict(y_val) or not _is_valid_y_strict(oo_val) or y_val != oo_val:
            return _base(mode=mode, brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)
        y_int = int(y_val)
    elif has_y:
        y_val = atom["y"]
        if not _is_valid_y_strict(y_val):
            return _base(mode=mode, brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)
        y_int = int(y_val)
    elif has_oo:
        oo_val = atom["observed_outcome"]
        if not _is_valid_y_strict(oo_val):
            return _base(mode=mode, brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)
        y_int = int(oo_val)
    else:
        return _base(mode=mode, brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)

    # ---------- settlement/outcome agreement (spec:85) ----------
    expected_y = 1 if settlement == "TRUE" else 0
    if y_int != expected_y:
        return _base(mode=mode, brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)

    # ---------- compute ----------
    try:
        value = compute_atomic_brier(p, y_int)
    except (TypeError, ValueError):
        return _base(mode=mode, brier=None, honesty="NOT_COMPUTABLE", failure="NOT_COMPUTABLE", corpus_ref=ref)

    return _base(mode=mode, brier=value, honesty="OBSERVED", failure=None, corpus_ref=ref)
