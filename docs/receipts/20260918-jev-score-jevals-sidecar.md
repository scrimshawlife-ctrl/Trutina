# Receipt — Trutina SCORE × Jev Jevals sidecar (2026-09-18)

**When:** 2026-09-18, 23:16:18 PT (live smoke) · receipt landed in-repo 2026-09-18 ~23:20 PT  
**Kind:** Docs-only pointer. Out-of-tree spike; **no** `src/brier` math edits.  
**Walls:** shadow/advisory only · no train · no Hub · no invent y/settlements · no send/spend/legal · no name_gate · no Trutina src/contracts edits  

Canonical machine + human receipts live out-of-tree:

| Path | Role |
|------|------|
| `/workspace/out/jev-trutina/` | Spike root (fixtures, smoke, runner) |
| `/workspace/out/jev-trutina/RECEIPT-TRUTINA-SCORE-JEVALS.md` | Full human receipt |
| `/workspace/out/jev-trutina/receipts/live_trutina_score_jevals.json` | Scrubbed machine receipt |
| `/workspace/out/jev-trutina/INTEGRATION-CARD.md` | Design card (K1–K3) |
| `/workspace/out/jev-trutina/SPIKE-BRIEF.md` | Implemented spike brief (K1 + thin K2) |

Skill: `/home/box/agent-data/workflows/jev-trutina-score-jevals/SKILL.md`

## Dual-track (OBSERVED)

| Track | Label | Meaning |
|-------|-------|---------|
| `trutina.*` | OBSERVED / NOT_COMPUTABLE | Direct `brier.score.score` packet fields |
| `jev.*` | SPECULATIVE | TypeSafe Jevals judge probabilities |
| `operator_pass` | INFERRED | `pass_bar >= 0.7` AND `critical_regression <= 0.3` (sidecar only) |

Auth (OBSERVED): `auth_path=typesafe_direct` · `model=typesafe:jev-latest` · key via `TYPESAFE_AI_API_KEY` (never printed).

## Live result — 6/6 operator_pass (OBSERVED)

| id | trutina_match | trutina track | operator_pass | matches_gold | critical_regression | pass_bar |
|----|---------------|---------------|---------------|--------------|---------------------|----------|
| `score_true_08` | True | OBSERVED | True | 0.98 | 0.07 | 0.85 |
| `score_false_08` | True | OBSERVED | True | 0.96 | 0.07 | 0.81 |
| `forecast_request` | True | NOT_COMPUTABLE | True | 0.97 | 0.08 | 0.71 |
| `void` | True | NOT_COMPUTABLE | True | 0.97 | 0.09 | 0.76 |
| `slang` | True | NOT_COMPUTABLE | True | 0.97 | 0.1 | 0.73 |
| `missing_settled_by` | True | NOT_COMPUTABLE | True | 0.97 | 0.09 | 0.74 |

Usage aggregate (OBSERVED): inputTokens 3042 · outputTokens 342 · totalTokens 3384.

## Spike files (out-of-tree only)

| Path | Role |
|------|------|
| `fixtures/score_cases.json` | 6 fixture atoms + expected |
| `run_score_fixtures.py` | Calls `brier.score.score`; float-tol match |
| `smoke-jev-trutina-score-jevals.mjs` | Live Jevals smoke; writes receipt |
| `node_modules` | Symlink → `/workspace/out/jev-spike/node_modules` |

## Walls confirmation

- Trutina product `src/` / contracts untouched by the spike.
- `name_gate` untouched; train / Hub / invent outcomes / send/spend/legal not performed.
- Receipt scrub: no `apikey_` / `vck_` / raw key material.

## Note (pre-existing pytest)

`tests/test_score.py` exact float equality (`== 0.04` / `== 0.64`) can fail on IEEE noise on this clone; spike did not edit Trutina. Fixture runner uses `math.isclose` abs_tol=1e-9.

## Next (KEEP, not this commit)

**K3** — GATE_ADVISORY Choice sidecar (advisory `review` / `hold` / `ok_to_surface` only). Brief: `/workspace/out/jev-trutina/NEXT-K3-BRIEF.md`. Do not activate promote flags.
