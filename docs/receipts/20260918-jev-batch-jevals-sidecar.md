# Receipt — Trutina BATCH × Jev Jevals sidecar (2026-09-18)

**When:** 2026-09-18, 23:40:16 PT (live smoke) · docs receipt landed ~same evening PT  
**Kind:** Docs-only pointer. Out-of-tree K1 KEEP extension; **no** `src/brier` math edits.  
**Walls:** shadow/advisory only · no train · no Hub · no invent y/settlements · no send/spend/legal · no name_gate · no Trutina src/contracts edits  
**DECOMPOSE:** **SKIP_DECOMPOSE** (Murphy/bin contracts heavy; not in this smoke)

Canonical machine + human receipts live out-of-tree:

| Path | Role |
|------|------|
| `/workspace/out/jev-trutina/` | Spike root (fixtures, smoke, runner) |
| `/workspace/out/jev-trutina/RECEIPT-TRUTINA-BATCH-JEVALS.md` | Full human receipt |
| `/workspace/out/jev-trutina/receipts/live_trutina_batch_jevals.json` | Scrubbed machine receipt |
| `/workspace/out/jev-trutina/INTEGRATION-CARD.md` | Design card (K1 BATCH LANDED) |

Skill: `/home/box/agent-data/workflows/jev-trutina-batch-jevals/SKILL.md`

## Dual-track (OBSERVED)

| Track | Label | Meaning |
|-------|-------|---------|
| `trutina.*` | OBSERVED / NOT_COMPUTABLE | Direct `aggregate_batch` report fields |
| `jev.*` | SPECULATIVE | TypeSafe Jevals judge probabilities |
| `operator_pass` | INFERRED | `pass_bar >= 0.7` AND `critical_regression <= 0.3` (sidecar only) |

Auth (OBSERVED): `auth_path=typesafe_direct` · `model=typesafe:jev-latest` · key via `TYPESAFE_AI_API_KEY` (never printed).

## Live result — 5/6 operator_pass · 6/6 trutina_match (OBSERVED)

| id | trutina_match | trutina track | operator_pass | matches_gold | critical_regression | pass_bar |
|----|---------------|---------------|---------------|--------------|---------------------|----------|
| `batch_uniform_accept` | True | OBSERVED | True | 0.93 | 0.08 | 0.75 |
| `batch_weighted_accept` | True | OBSERVED | True | 0.93 | 0.08 | 0.78 |
| `batch_empty` | True | NOT_COMPUTABLE | True | 0.93 | 0.08 | 0.78 |
| `batch_void_unsettled_only` | True | NOT_COMPUTABLE | True | 0.92 | 0.09 | 0.75 |
| `batch_zero_weight` | True | NOT_COMPUTABLE | False | 0.83 | 0.17 | 0.69 |
| `batch_invalid_weight` | True | NOT_COMPUTABLE | True | 0.89 | 0.09 | 0.72 |

Usage aggregate (OBSERVED): inputTokens 3203 · outputTokens 342 · totalTokens 3545.

Smoke exit 0. `batch_zero_weight` pass_bar just under 0.7 → operator_pass False (fixture match still True).

## Spike files (out-of-tree only)

| Path | Role |
|------|------|
| `fixtures/batch_cases.json` | 6 fixture manifests + expected |
| `run_batch_fixtures.py` | Calls `aggregate_batch`; float-tol match |
| `smoke-jev-trutina-batch-jevals.mjs` | Live Jevals smoke; writes receipt |
| `node_modules` | Symlink → `/workspace/out/jev-spike/node_modules` |

## Walls confirmation

- Trutina product `src/` / contracts untouched by the spike.
- `name_gate` untouched; train / Hub / invent outcomes / send/spend/legal not performed.
- Receipt scrub: no `apikey_` / `vck_` / raw key material.
