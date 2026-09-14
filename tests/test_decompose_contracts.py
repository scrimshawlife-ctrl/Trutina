import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

from brier.score import score

ROOT = Path(__file__).resolve().parents[1]
INPUT = json.loads((ROOT / "contracts/brier.decompose.input.v0.schema.json").read_text())
REPORT = json.loads((ROOT / "contracts/brier.decompose.report.v0.schema.json").read_text())
INPUT_VALIDATOR = Draft202012Validator(INPUT, format_checker=FormatChecker())
REPORT_VALIDATOR = Draft202012Validator(REPORT, format_checker=FormatChecker())
HASH = "a" * 64


def request(method="MURPHY_EXACT_V1", edges=None):
    return {
        "schema": "brier.decompose.input.v0",
        "specialist": "abx.brier",
        "display": "Trutina",
        "mode": "DECOMPOSE",
        "manifest": {"schema": "brier.batch.input.v0", "manifest_hash": HASH},
        "method": method,
        "bin_edges": edges,
    }


def report(method="MURPHY_EXACT_V1"):
    return {
        "schema": "brier.decompose.report.v0",
        "specialist": "abx.brier",
        "display": "Trutina",
        "mode": "DECOMPOSE",
        "status": "COMPUTABLE",
        "honesty": "OBSERVED",
        "method": method,
        "manifest_hash": HASH,
        "raw_brier": 0.3125,
        "binned_brier": None,
        "reliability": 0.0625,
        "resolution": 0.0,
        "uncertainty": 0.25,
        "within_correction": None,
        "reconstruction_residual": 0.0,
        "singleton_fraction": 0.0,
        "bin_edges": None,
        "groups": [],
        "reasons": [],
        "forecast_eligible": False,
        "can_promote": False,
        "weight_mutation": False,
        "phenomenal": False,
        "ledger_id": None,
    }


def test_exact_request_contract():
    INPUT_VALIDATOR.validate(request())


def test_binned_request_requires_edges():
    with pytest.raises(ValidationError):
        INPUT_VALIDATOR.validate(request("MURPHY_BINNED_V1", None))
    INPUT_VALIDATOR.validate(request("MURPHY_BINNED_V1", [0.0, 0.5, 1.0]))


def test_report_contract_locks_authority_flags():
    REPORT_VALIDATOR.validate(report())
    bad = report()
    bad["can_promote"] = True
    with pytest.raises(ValidationError):
        REPORT_VALIDATOR.validate(bad)


def test_report_rejects_unregistered_methods():
    bad = report()
    bad["method"] = "CORP_PAV_V1"
    with pytest.raises(ValidationError):
        REPORT_VALIDATOR.validate(bad)


def test_decompose_runtime_remains_closed_in_contract_cycle():
    packet = score({"mode": "DECOMPOSE"})
    assert packet["schema"] == "brier.score.v0"
    assert packet["mode"] == "DECOMPOSE"
    assert packet["honesty"] == "NOT_COMPUTABLE"
    assert packet["failure"] == "NOT_COMPUTABLE"
    assert packet["can_promote"] is False
    assert packet["weight_mutation"] is False
    assert packet["ledger_id"] is None
