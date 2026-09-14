"""SCORE, bounded BATCH, and bounded DECOMPOSE dispatch."""

from __future__ import annotations

from datetime import datetime
import re
from typing import Any

from .core import compute_atomic_brier

SCHEMA = "brier.score.v0"
SPECIALIST = "abx.brier"
DISPLAY = "Trutina"
FORMULA = "BRIER_BINARY_V1"
OTHER_ATOMS = {"slang_atom", "tradition_atom", "sign_atom", "route_atom"}
LIVE_MODES = {"SCORE", "BATCH", "DECOMPOSE"}
STUB_MODES = {"FUSION_ADVISORY", "ROUTER_MICRO", "GATE_ADVISORY", "PROJECT"}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


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


_TIMESTAMP = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])"
)


def _nonblank(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_timestamp(value: Any) -> bool:
    if value is None:
        return True
    if not isinstance(value, str) or _TIMESTAMP.fullmatch(value) is None:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _number(atom: dict[str, Any], canonical: str, alias: str, *, binary: bool = False) -> float:
    values = [atom[key] for key in (canonical, alias) if key in atom]
    if not values:
        raise ValueError("missing number")
    for value in values:
        if type(value) not in (int, float) or not 0 <= value <= 1:
            raise ValueError("invalid number")
        if binary and value not in (0, 1):
            raise ValueError("nonbinary outcome")
    if len(values) == 2 and values[0] != values[1]:
        raise ValueError("conflicting aliases")
    return float(values[0])


def _refuse(ref: str | None = None, *, mode: str = "SCORE", lane: bool = False) -> dict[str, Any]:
    return _base(
        mode=mode,
        brier=None,
        honesty="NOT_COMPUTABLE",
        failure="SPECIALIST_LANE_VIOLATION" if lane else "NOT_COMPUTABLE",
        corpus_ref=ref,
    )


def _registered_decompose_request(atom: dict[str, Any]) -> bool:
    if atom.get("schema") != "brier.decompose.input.v0":
        return False
    if atom.get("specialist") != SPECIALIST or atom.get("display") != DISPLAY:
        return False
    manifest = atom.get("manifest")
    if not isinstance(manifest, dict) or manifest.get("schema") != "brier.batch.input.v0":
        return False
    manifest_hash = manifest.get("manifest_hash")
    if not isinstance(manifest_hash, str) or _SHA256.fullmatch(manifest_hash) is None:
        return False
    method = atom.get("method")
    if method == "MURPHY_EXACT_V1":
        return atom.get("bin_edges") is None
    if method == "MURPHY_BINNED_V1":
        return isinstance(atom.get("bin_edges"), list)
    return False


def score(atom: Any) -> dict[str, Any]:
    """Validate SCORE or dispatch registered BATCH/DECOMPOSE inputs."""
    if not isinstance(atom, dict):
        return _refuse()
    raw_ref = atom.get("corpus_ref")
    ref = raw_ref if _nonblank(raw_ref) else None
    mode = atom.get("mode", "SCORE")
    if not isinstance(mode, str):
        return _refuse(ref)
    if mode in STUB_MODES:
        return _refuse(ref, mode=mode)
    if mode not in LIVE_MODES:
        return _refuse(ref)

    if mode == "BATCH":
        from .batch import BatchContractError, aggregate_batch
        try:
            return aggregate_batch(atom)
        except BatchContractError:
            return _refuse(ref, mode="BATCH")

    if mode == "DECOMPOSE":
        if not _registered_decompose_request(atom):
            return _refuse(ref, mode="DECOMPOSE")
        from .decompose import decompose
        return decompose(atom)

    payload = atom.get("payload_class")
    if not isinstance(payload, str) or payload == "forecast_request":
        return _refuse(ref)
    if payload != "settled_forecast":
        return _refuse(ref, lane=True)

    settlement = atom.get("settlement")
    if not isinstance(settlement, str) or settlement not in ("TRUE", "FALSE"):
        return _refuse(ref)
    if not _nonblank(atom.get("settled_by")):
        return _refuse(ref)
    if not _valid_timestamp(atom.get("settled_at")):
        return _refuse(ref)
    if raw_ref is not None and ref is None:
        return _refuse()

    try:
        p = _number(atom, "p", "expected_probability")
        y = _number(atom, "y", "observed_outcome", binary=True)
    except ValueError:
        return _refuse(ref)
    if (settlement == "TRUE") != (y == 1):
        return _refuse(ref)
    value = compute_atomic_brier(p, int(y))
    return _base(mode="SCORE", brier=value, honesty="OBSERVED", failure=None, corpus_ref=ref)


# Provenance: Trutina Spec 001 / T01 + Spec 000 / T03/T04B.
