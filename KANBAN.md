# Kanban — Trutina

Board state as measured, not as remembered. Every item below was true on the date at the bottom.

| | Backlog | In progress | Blocked | Done |
|---|---|---|---|---|
| **Count** | 2 | 0 | 3 | 5 |

**Blocked** matters more than the other columns: an item sits there when it is waiting on something this
repository cannot supply, and the blocker is named rather than implied.

_Last reviewed: 2026-10-07._

## Backlog

- Additional calibration metrics, **only** where a consumer names a specific one it needs.
- Downstream adoption: this library is the calibration surface for the Abraxas stack; a consumer that scores
  forecasts is what would exercise it end to end.

## In progress

- Nothing. The scoring core is in a consistent state; what is unresolved is the contract test below, which is
  a decision rather than a build.

## Blocked

| Item | Blocked on | Evidence |
|---|---|---|
| `tests/test_score_contract.py`: **67 failing** | The author's call on which side is stale | The test was last touched **2026-09-13** (`41f62f4`). The scoring source changed **2026-09-15** (`7de239b`, "resolve: spec-000 score guards onto current main"), which rewrote `src/brier/score.py` (166 lines, mostly deletions) and updated `tests/test_score.py` -- but not this file. `specs/001-score/` documents the newer behaviour. |
| `tests/test_decompose.py`: **2 failing** | Same reconciliation | Same commit range; a decompose-mode counterpart. |
| `tests/test_batch.py`: **1 failing** | Same reconciliation | Same commit range; a batch-mode counterpart. |

Whole suite as measured: **70 failed, 141 passed**.

### The failures, grouped by what they actually are

Grouping the 70 by assertion shape separates stale expectations from things that are wrong regardless of which
contract is current. Twenty-eight are `assert <number> is None`, which is the ambiguous class -- `p=0, y=0` is a
legitimate Brier of 0.0, so a number there may be correct. The rest are not:

| Count | Failure | Reading |
|---|---|---|
| 28 | `assert N.N is None` | **Ambiguous.** The test calls the packet refused; the new code scores it. Needs the author: some of these inputs are legitimately scorable. |
| 14 | `ValidationError: {} is not of type 'string','null'` (7) / `[] ...` (7) | **Code defect.** The packet carries a dict/list where the closed schema allows string-or-null. The schema is explicit, so this is a shape bug in the emitter, not a contract question. |
| 4 | `assert 'SPECIALIST_LANE_VIOLATION' == 'NOT_COMPUTABLE'` | **Ambiguous, probably fine.** A more specific refusal reason where the old test wanted a generic one. |
| 3 | `DID NOT RAISE NotImplementedError` | **Code defect.** `to_brier_score_packet` / `to_brier_ledger_entry` are `def f(): pass` -- deferred exports that return silently instead of refusing. A stub that does nothing is a fail-open, which is worse than the refusal it was meant to make. |
| 2 | `ValidationError: Additional properties are not allowed ('brier','corpus_ref','failure','formula' ...)` | **Wrong schema.** The score packet is being validated against a schema that does not describe it. |
| 2+2 | `TypeError: cannot use 'list'/'dict' as a set element` | **Code defect.** Unhashable values passed where a set is built. Nothing to do with the contract. |
| ~4 | `ValidationError: True is not one of [SCORE, BATCH, ...]` / `N is not one of [...]` | **Code defect (probable).** A boolean or number reaching a field the schema types as an enum string. `True` is an instance of `int` in Python, which is a classic way to pass a type check and fail a schema. |

**So "the test is stale" was too generous.** Part of this is drift, and part is the 2026-09-15 rewrite leaving
real defects that the closed schemas catch precisely because they are closed. The 28 ambiguous cases and the 4
refusal-reason cases need the author; the 14 + 3 + 2 + 4 + 4 above do not obviously do so, and are worth
reading before deciding which side moves.

### Research verdicts on all seven failure classes

Each class was settled against `specs/001-score/` and `contracts/*.json` on one side and the exact code line on
the other. Six are **code defects**; one is a **stale test**.

| Class | Count | Verdict | Code | Spec |
|---|---|---|---|---|
| `assert N.N is None` | 28 | **code wrong** | `score.py:79` — `compute_atomic_brier(float(p), y_int)` has no type guard, so `float(True)==1.0` and `float('1')==1.0` score a boolean or a string instead of refusing it. `score.py:41-42` also silently defaults `mode=None` to SCORE. | spec:34 (null/empty/non-string mode invalid), :36 (booleans and strings rejected for p/y), :85 (fractional/string/boolean p/y → NOT_COMPUTABLE) |
| `{} / [] is not of type 'string','null'` | 14 | **code wrong** | all ten `_base()` calls in `score()` pass `corpus_ref` through raw, so a list or dict is echoed verbatim. | spec:41 (corpus_ref nonempty if string; malformed refused and never echoed) |
| `'SPECIALIST_LANE_VIOLATION' == 'NOT_COMPUTABLE'` | 4 | **code wrong** | `score.py:54-55` falls through to SPECIALIST_LANE_VIOLATION for a missing or non-string `payload_class`; that reason is reserved for recognised non-settled atoms. | spec:45 and :84 (missing/non-string payload_class → NOT_COMPUTABLE), :80 (named atoms → SPECIALIST_LANE_VIOLATION) |
| `DID NOT RAISE NotImplementedError` | 3 | **FIXED this session** | `compat/abraxas.py:4,8` and `ledger.py:4` were bare `pass` — deferred exports returning `None` instead of refusing. They now raise. | `engineering.md:16` — "They now expose explicit NotImplementedError stubs" |
| `cannot use 'list'/'dict' as a set element` | 4 | **code wrong** | `score.py:45` does `mode in STUB_MODES` and `:52` does `payload in OTHER_ATOMS` without an isinstance check, so an unhashable value raises instead of refusing. | spec:34, :45 (non-string mode/payload_class → refusal, not an exception) |
| `True / N is not one of [SCORE, BATCH, ...]` | 4 | **code wrong** | `score.py:47-48` returns the refusal carrying the raw invalid `mode`, which the closed schema rejects. | spec:45 — "Invalid/unknown mode is represented as SCORE in the refusal packet" |
| `Additional properties ... were unexpected` | 3 | **test stale** | `tests/test_decompose.py:148,168` and `tests/test_batch.py:198` expect mode dispatch to decompose/batch handlers. The code correctly returns a score.v0 refusal for stub modes (`score.py:45-46`). | spec:99-105 lists these as "Later modes (not this cycle)"; `engineering.md:7` — "BATCH / DECOMPOSE / advisory modes stub NOT_COMPUTABLE" |

**Measured after the stub fix: 70 → 67 failed, 141 → 144 passed.**

The remaining five code classes are all spec-cited and unambiguous in direction — the code must refuse rather
than score or crash — but they are behavioural changes to the scoring path, so they are recorded rather than
applied. The three test-stale cases are deferred by the spec's own words and should be marked in place.

### Fixed this session: 70 -> 5 failed, 203 passed, 3 xfailed

Five of the six diagnosed code defects were repaired in `src/brier/score.py` (+161/-29), in two measured passes:
**67 -> 50 -> 8 -> 5 failed**, the last step being the three spec-deferred tests marked in place.

`sanitize` and type-guard work: `mode` and `payload_class` are isinstance-checked before any set membership
(previously an unhashable value raised `TypeError` instead of refusing); `p` is type-checked before `float()`
so a boolean or numeric string can no longer be scored; `corpus_ref` is sanitized on every return path;
non-string modes normalize to `SCORE`; `settled_at`, `settled_by`, aliases and the top-level object type are
now validated per spec.

**Three tests marked xfail, by name, with the citation** -- `test_public_dispatch_exact_and_binned_reports` and
`test_registered_partial_manifest_fails_closed_as_decompose_report` in test_decompose.py, and
`test_a28_asof_snapshot_counts_and_runtime_dispatch` in test_batch.py, each `strict=True` with the reason
"the spec defers this mode to a later cycle ... Remove the marker when dispatch is implemented." Deferred is
not deleted, and `strict=True` means the marker fails the run if the test ever starts passing.

An over-broad first attempt at this marked 16 tests instead of 3 and pushed the count to 18 failed; it was
reverted and the three were identified by name from the actual failures instead of by pattern.

### The five that remain are a spec-versus-newer-test conflict, not a defect

All five are in tests/test_score_contract.py and each disagrees with tests/test_score.py, which arrived with the
same commit (7de239b) that rewrote score.py:

| Failing contract test | The spec says | test_score.py says |
|---|---|---|
| `test_missing_required[payload_class]` | spec:84 -- missing payload_class or settlement -> NOT_COMPUTABLE | SPECIALIST_LANE_VIOLATION |
| `test_invalid_mode[]` | spec:45 -- invalid/unknown mode is represented as SCORE in the refusal packet | preserves the raw `''` |
| `test_invalid_mode[UNKNOWN]` | spec:45 -- as above | preserves the raw `'UNKNOWN'` |
| `test_numeric_alias_compatibility[0.0-False]` | spec:36 -- "0.0/1.0 valid" | refuses float y |
| `test_numeric_alias_compatibility[1.0-False]` | spec:36 -- as above | refuses float y |

The current code follows **test_score.py** on all five, which is why the contract tests fail. Two artifacts (the
spec and the older contract test) agree with each other and disagree with the newer test; the newer test
arrived with the rewrite that the spec predates. Flipping the code to the spec would move the five failures to
the other file rather than clear them, so it is left as a decision: either the spec is updated to record the
newer behaviour, or `test_score.py` is corrected to the spec. Both are the author's call.

Also added: a `.gitignore`, absent until now, so test runs stop leaving a dozen untracked `.pyc` files.

## Done

- Brier scoring with honest uncertainty output — the core surface this library exists for.
- Closed JSON Schemas for every mode (`contracts/`), with `additionalProperties: false` throughout.
- `jsonschema>=4` declared as a dev dependency rather than assumed present.
- **CI on every push** (3.10 / 3.11 / 3.12), added this session. This repository had tests and **no workflow**,
  so nothing ever ran them — which is why the drift above sat unnoticed for three weeks. `git log -- .github/`
  was empty before this. The workflow is expected to be red until the blocked items are reconciled, and it says
  so in a comment: the red is the point, because an invisible failure is worse than a visible one.
- MIT licence, plus the roadmap and contributing docs every sibling repository now carries.
