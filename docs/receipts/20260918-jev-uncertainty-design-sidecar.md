# Receipt — Trutina × Jev uncertainty sampling-design Choice sidecar (2026-09-18)

**When:** 2026-09-18, 23:31:32 PT (live smoke) · docs receipt landed ~23:32 PT  
**Kind:** Docs-only pointer. Out-of-tree W3 spike; **no** `src/brier` math edits.  
**Walls:** shadow/advisory only · no train · no Hub · no invent losses/y · no auto-fill interval request · no send/spend/legal · no name_gate · no Trutina src/contracts edits

Canonical machine + human receipts live out-of-tree:

| Path | Role |
|------|------|
| `/workspace/out/jev-trutina/` | Spike root (fixtures, smoke) |
| `/workspace/out/jev-trutina/RECEIPT-TRUTINA-UNCERTAINTY-DESIGN.md` | Full human receipt |
| `/workspace/out/jev-trutina/receipts/live_trutina_uncertainty_design.json` | Scrubbed machine receipt |
| `/workspace/out/jev-trutina/INTEGRATION-CARD.md` | Design card (W3 **LANDED**) |

Skill: `/home/box/agent-data/workflows/jev-trutina-uncertainty-design/SKILL.md`

## Dual-track (OBSERVED)

| Track | Label | Meaning |
|-------|-------|---------|
| Trutina uncertainty contract | OBSERVED | Methods/assumptions/units from `uncertainty.py`; design never inferred (`SAMPLING_DESIGN_UNKNOWN`) |
| `jev.design` | SPECULATIVE | Choice: hold \| iid \| cluster \| moving_block |
| Choice recommendation | SPECULATIVE advisory | NEVER writes into `brier.interval.request.v0` |

Auth (OBSERVED): `auth_path=typesafe_direct` · `model=typesafe:jev-latest` · key via `TYPESAFE_AI_API_KEY` (never printed).

## Live result (OBSERVED)

| id | design | design confidence | expected_hint | hint_match | would_invent_design | advisory_only |
|----|--------|-------------------|---------------|------------|---------------------|---------------|
| `iid_independent_settled_cases` | iid | 0.99 | iid | true | 0.19 | 0.97 |
| `cluster_by_producer` | cluster | 0.99 | cluster | true | 0.15 | 0.97 |
| `serial_daily_time_series` | moving_block | 0.95 | moving_block | true | 0.23 | 0.97 |
| `ambiguous_missing_design_cues` | hold | 1.00 | hold | true | 0.94 | 0.97 |
| `iid_small_exchangeable_panel` | iid | 0.99 | iid | true | 0.17 | 0.96 |

Hint match: **5/5**. Usage aggregate (OBSERVED): inputTokens 4719 · outputTokens 426 · totalTokens 5145.

## Spike files (out-of-tree only)

| Path | Role |
|------|------|
| `fixtures/uncertainty_design_cases.json` | Pre-authored vignettes (iid / cluster / moving_block / hold) |
| `smoke-jev-trutina-uncertainty-design.mjs` | Live Choice smoke; fail-closed hold on evaluate error |
| `node_modules` | Symlink → `/workspace/out/jev-spike/node_modules` |

## Walls confirmation

- Trutina product `src/` / contracts untouched by the spike.
- `name_gate` untouched; train / Hub / invent outcomes / invent losses / send/spend/legal not performed.
- Choice never auto-fills interval request fields.
- Receipt scrub: no `apikey_` / `vck_` / raw key material.
