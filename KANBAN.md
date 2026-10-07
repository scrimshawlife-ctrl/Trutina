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

## Done

- Brier scoring with honest uncertainty output — the core surface this library exists for.
- Closed JSON Schemas for every mode (`contracts/`), with `additionalProperties: false` throughout.
- `jsonschema>=4` declared as a dev dependency rather than assumed present.
- **CI on every push** (3.10 / 3.11 / 3.12), added this session. This repository had tests and **no workflow**,
  so nothing ever ran them — which is why the drift above sat unnoticed for three weeks. `git log -- .github/`
  was empty before this. The workflow is expected to be red until the blocked items are reconciled, and it says
  so in a comment: the red is the point, because an invisible failure is worse than a visible one.
- MIT licence, plus the roadmap and contributing docs every sibling repository now carries.
