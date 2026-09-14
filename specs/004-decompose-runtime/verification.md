# T04B verification boundary

Scope: DECOMPOSE exact/binned Murphy diagnostics only.

Acceptance mapping:
- A17 exact weighted Murphy identity.
- A18 corrected binned identity with negative within-bin correction permitted.
- A19 empty bins, ties/endpoint behavior, singleton groups, single-class outcomes, invalid edge refusal.
- A20 elementary Murphy-loss integral equals binary Brier loss.

Fail-closed boundaries:
- partial but registered DECOMPOSE manifests return a registered NOT_COMPUTABLE diagnostic report;
- requests with unregistered top-level fields retain the legacy brier.score.v0 refusal packet;
- CORP/PAV, ECE, Yates moments, interval/bootstrap and PROJECT remain closed.

Authority remains false for forecast eligibility, promotion, weight mutation, phenomenal status, and ledger finalization.

This document records test intent and reviewed scope. It is not a claim that a local pytest run occurred in the assistant container.

Provenance: Trutina Spec 000 / T04B; T04A baseline d6a0af93d8dd464fe96c85940f23042e9760d2cb.
