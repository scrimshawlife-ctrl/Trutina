"""Deferred external adapters; no shape conversion is implemented."""


def to_brier_score_packet():
    raise NotImplementedError("External packet conversion is not implemented in Trutina T0")


def to_brier_ledger_entry():
    raise NotImplementedError("External ledger conversion is not implemented in Trutina T0")


# Provenance: Trutina Spec 001 / T01 import repair; baseline ecbf403.
