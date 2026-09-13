# Engineering — SCORE

Live: `src/brier/score.py` → `score(atom) -> brier.score.v0`
Kernel: `src/brier/core.py` (`compute_atomic_brier`)
Does not import Abraxas-v2.0.
Package name stays `brier` this cycle.
BATCH / DECOMPOSE / advisory modes stub `NOT_COMPUTABLE`.
`ledger_id` stays null.

## T01 validation implementation

OBSERVED implementation: `score(atom)` validates a JSON object, explicit settled payload and settlement, native numeric probabilities/outcomes, agreeing aliases, operator identity presence, optional reference and timestamp. It refuses booleans, numeric strings, nonfinite values and fractional outcomes before conversion. Invalid mode/payload containers produce packets rather than unhashable-value exceptions. All outputs retain the existing v0 schema and frozen flags.

INFERRED timestamp profile for T01: calendar-date `YYYY-MM-DDTHH:MM:SS[.fraction]` followed by `Z` or a numeric `+/-HH:MM` offset; valid calendar/time fields required. Date-only, timezone-free, leap-second and 24:00 forms are refused. Omitted/null `settled_at` remains accepted for atomic SCORE, consistent with Spec 001; BATCH's stronger cutoff contract remains deferred. Timestamp validation does not authenticate receipt history.

Prerequisite repair: the baseline ledger and compatibility files contained literal backslash-n text in comments, leaving the functions imported by `brier.__init__` undefined. They now expose explicit `NotImplementedError` stubs. No adapter or ledger operation is implemented.

Validation: `python -B -m pytest -q -p no:cacheprovider tests/test_score_contract.py tests/test_score.py tests/test_core.py` passes 142 tests on Python 3.12.14, pytest 9.1.1, jsonschema 4.26.0. The contract tests validate success/refusal packets with Draft 2020-12 and semantic invariants. Existing decimal fixtures use 1e-12 tolerances. `jsonschema` is a development dependency only; runtime dependencies remain empty. The numeric kernel, output schema and live-mode set are unchanged.

Scope: A01-A09 and the current binary refusal boundary in A24; future BATCH/DECOMPOSE/multiclass behavior is not validated or opened. External settlement authenticity and live Spec 009/010 parity remain NOT_COMPUTABLE.

Provenance: Trutina Spec 001 / T01 + specification baseline ecbf403fa45a61c43ce17e2d84f82891392813fd.
