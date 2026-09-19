# Receipt — Trutina DECOMPOSE × Jev Jevals sidecar (2026-09-18)

**When:** 2026-09-18, 23:54:13 PT (live smoke) · docs receipt landed ~same evening PT  
**Kind:** Docs-only pointer. Out-of-tree thin DECOMPOSE Jevals; **no** `src/brier` math edits.  
**Walls:** shadow/advisory only · no train · no Hub · no invent y/settlements · no send/spend/legal · no name_gate · no Trutina src/contracts edits  
**Closes:** BATCH **SKIP_DECOMPOSE** thinly (exact/binned accept+refuse only; not full Murphy matrix)

Canonical machine + human receipts live out-of-tree:

| Path | Role |
|------|------|
| `/workspace/out/jev-trutina/` | Spike root (fixtures, smoke, runner) |
| `/workspace/out/jev-trutina/RECEIPT-TRUTINA-DECOMPOSE-JEVALS.md` | Full human receipt |
| `/workspace/out/jev-trutina/receipts/live_trutina_decompose_jevals.json` | Scrubbed machine receipt |
| `/workspace/out/jev-trutina/INTEGRATION-CARD.md` | Design card (K1 DECOMPOSE thin LANDED) |

Skill: `/home/box/agent-data/workflows/jev-trutina-decompose-jevals/SKILL.md`

## Dual-track (OBSERVED)

| Track | Label | Meaning |
|-------|-------|---------|
| `trutina.*` | OBSERVED / NOT_COMPUTABLE | Direct `exact_murphy` / `binned_murphy` report fields |
| `jev.*` | SPECULATIVE | TypeSafe Jevals judge probabilities |
| `operator_pass` | INFERRED | `pass_bar >= 0.7` AND `critical_regression <= 0.3` (sidecar only) |

Auth (OBSERVED): `auth_path=typesafe_direct` · `model=typesafe:jev-latest` · key via `TYPESAFE_AI_API_KEY` (never printed).

## Live result — 5/6 operator_pass · 6/6 trutina_match (OBSERVED)

| id | trutina_match | trutina track | operator_pass | matches_gold | critical_regression | pass_bar |
|----|---------------|---------------|---------------|--------------|---------------------|----------|
| `decompose_exact_accept` | True | OBSERVED | True | 0.87 | 0.09 | 0.80 |
| `decompose_exact_empty` | True | NOT_COMPUTABLE | True | 0.92 | 0.08 | 0.79 |
| `decompose_exact_zero_weight` | True | NOT_COMPUTABLE | True | 0.93 | 0.09 | 0.77 |
| `decompose_exact_invalid_weight` | True | NOT_COMPUTABLE | True | 0.87 | 0.11 | 0.70 |
| `decompose_binned_accept` | True | OBSERVED | True | 0.86 | 0.09 | 0.79 |
| `decompose_binned_invalid_edges` | True | NOT_COMPUTABLE | False | 0.87 | 0.13 | 0.68 |

Usage aggregate (OBSERVED): inputTokens 3779 · outputTokens 342 · totalTokens 4121.

Smoke exit 0. `decompose_binned_invalid_edges` pass_bar just under 0.7 → operator_pass False (fixture match still True). NUMERICAL_IDENTITY_FAILURE omitted (no clear gold fixture).

## Spike files (out-of-tree only)

| Path | Role |
|------|------|
| `fixtures/decompose_cases.json` | 6 fixture manifests + expected |
| `run_decompose_fixtures.py` | Calls `exact_murphy`/`binned_murphy`; float-tol match |
| `smoke-jev-trutina-decompose-jevals.mjs` | Live Jevals smoke; writes receipt |
| `node_modules` | Symlink → `/workspace/out/jev-spike/node_modules` |

## Walls confirmation

- Trutina product `src/` / contracts untouched by the spike.
- `name_gate` untouched; train / Hub / invent outcomes / send/spend/legal not performed.
- Receipt scrub: no `apikey_` / `vck_` / raw key material.
- Authority walls false: `forecast_eligible` / `can_promote` / `weight_mutation` / `phenomenal`.
