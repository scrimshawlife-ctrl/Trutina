# Receipt — Trutina × Jev GATE_ADVISORY Choice sidecar (2026-09-18)

**When:** 2026-09-18, 23:24:43 PT (live smoke) · docs receipt landed ~23:25 PT  
**Kind:** Docs-only pointer. Out-of-tree K3 spike; **no** `src/brier` math edits.  
**Walls:** shadow/advisory only · no train · no Hub · no invent y/settlements · no send/spend/legal · no name_gate · no Trutina src/contracts edits  

Canonical machine + human receipts live out-of-tree:

| Path | Role |
|------|------|
| `/workspace/out/jev-trutina/` | Spike root (fixtures, smoke) |
| `/workspace/out/jev-trutina/RECEIPT-TRUTINA-GATE-ADVISORY.md` | Full human receipt |
| `/workspace/out/jev-trutina/receipts/live_trutina_gate_advisory.json` | Scrubbed machine receipt |
| `/workspace/out/jev-trutina/NEXT-K3-BRIEF.md` | K3 brief (implemented) |
| `/workspace/out/jev-trutina/INTEGRATION-CARD.md` | Design card (K1–K3) |

Skill: `/home/box/agent-data/workflows/jev-trutina-gate-advisory/SKILL.md`

## Dual-track (OBSERVED)

| Track | Label | Meaning |
|-------|-------|---------|
| `trutina.packet_summary` | OBSERVED / NOT_COMPUTABLE | Precomputed SCORE fields |
| `jev.disposition` | SPECULATIVE | Choice: hold \| review \| ok_to_surface |
| `ok_to_surface` | SPECULATIVE advisory | NEVER implies can_promote / forecast_eligible / weight_mutation / phenomenal |

Auth (OBSERVED): `auth_path=typesafe_direct` · `model=typesafe:jev-latest` · key via `TYPESAFE_AI_API_KEY` (never printed).

## Live result (OBSERVED)

| id | trutina track | disposition | disposition confidence | walls_intact |
|----|---------------|-------------|------------------------|--------------|
| `accept_score_true_08` | OBSERVED | ok_to_surface | 0.85 | 0.88 |
| `refuse_forecast_request` | NOT_COMPUTABLE | hold | 0.31 | 0.83 |
| `refuse_slang_atom` | NOT_COMPUTABLE | hold | 0.60 | 0.85 |
| `accept_score_false_08` | OBSERVED | ok_to_surface | 0.47 | 0.87 |

Usage aggregate (OBSERVED): inputTokens 2775 · outputTokens 252 · totalTokens 3027.

Promote flags on every packet: `forecast_eligible` / `can_promote` / `weight_mutation` / `phenomenal` = **false**.

## Spike files (out-of-tree only)

| Path | Role |
|------|------|
| `fixtures/gate_advisory_cases.json` | Mixed SCORE accept + NOT_COMPUTABLE refuse summaries |
| `smoke-jev-trutina-gate-advisory.mjs` | Live Choice smoke; fail-closed hold on evaluate error |
| `node_modules` | Symlink → `/workspace/out/jev-spike/node_modules` |

## Walls confirmation

- Trutina product `src/` / contracts untouched by the spike.
- `name_gate` untouched; train / Hub / invent outcomes / send/spend/legal not performed.
- Receipt scrub: no `apikey_` / `vck_` / raw key material.
