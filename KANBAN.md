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
| `tests/test_score_contract.py`: **67 failing** | The author's call on which side is stale | The test was last touched **2026-09-13** (`41f62f4`). The scoring source changed **2026-09-15** (`7de239b`, "resolve: spec-000 score guards onto current main"), which rewrote `src/brier/score.py` (166 lines, mostly deletions) and updated `tests/test_score.py` — but not this file. `specs/001-score/` documents the newer behaviour, so the test is the stale side; confirming that is the author's call, not a passer-by's. |
| `tests/test_batch.py`: **1 failing** | Same reconciliation | Same commit range; a batch-mode counterpart of the drift above. |
| `tests/test_decompose.py`: **2 failing** | Same reconciliation | Same commit range; a decompose-mode counterpart. |

Whole suite as measured: **70 failed, 141 passed**.

Two of the failures are worth naming, because they are the kind that matter:
`assert 0.0 is None` (`test_score_contract.py:44`) and
`assert 'SPECIALIST_LANE_VIOLATION' == 'NOT_COMPUTABLE'` (`:45`). The first is a packet the *old* contract
called refused and the *new* one scores — `p=0, y=0` is a legitimate Brier of 0.0, not a refusal, which is
exactly why this needs an author's eye rather than a passer-by's edit. The second is a *more specific* refusal
reason where the old test wanted a generic one, which reads as an improvement rather than a regression.

## Done

- Brier scoring with honest uncertainty output — the core surface this library exists for.
- Closed JSON Schemas for every mode (`contracts/`), with `additionalProperties: false` throughout.
- `jsonschema>=4` declared as a dev dependency rather than assumed present.
- **CI on every push** (3.10 / 3.11 / 3.12), added this session. This repository had tests and **no workflow**,
  so nothing ever ran them — which is why the drift above sat unnoticed for three weeks. `git log -- .github/`
  was empty before this. The workflow is expected to be red until the blocked items are reconciled, and it says
  so in a comment: the red is the point, because an invisible failure is worse than a visible one.
- MIT licence, plus the roadmap and contributing docs every sibling repository now carries.
