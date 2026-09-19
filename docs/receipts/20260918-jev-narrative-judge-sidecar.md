# Receipt — Trutina × Jev narrative calibration meta-judge sidecar (2026-09-18)

**When:** 2026-09-18, 23:44:26 PT (live smoke) · docs receipt landed ~23:45 PT  
**Kind:** Docs-only pointer. Out-of-tree W1 spike; **no** `src/brier` math edits.  
**Corpus:** `corpus_class: synthetic_eval` (explicitly labeled synthetic; not live Hyperlex/operator settlements).  
**Walls:** shadow/advisory only · narratives never become y/settlement · no merge jev.* into brier.score.v0 · no train · no Hub · no name_gate · no promote · no send/spend/legal · no Trutina src/contracts edits

Canonical machine + human receipts live out-of-tree:

| Path | Role |
|------|------|
| `/workspace/out/jev-trutina/` | Spike root (fixtures, smoke) |
| `/workspace/out/jev-trutina/RECEIPT-TRUTINA-NARRATIVE-JUDGE.md` | Full human receipt |
| `/workspace/out/jev-trutina/receipts/live_trutina_narrative_judge.json` | Scrubbed machine receipt |
| `/workspace/out/jev-trutina/INTEGRATION-CARD.md` | Design card (W1 **LANDED (synthetic corpus)**) |

Skill: `/home/box/agent-data/workflows/jev-trutina-narrative-judge/SKILL.md`

## Dual-track (OBSERVED)

| Track | Label | Meaning |
|-------|-------|---------|
| `packet_summary` Brier / honesty | OBSERVED or NOT_COMPUTABLE / missing | Precomputed from known p,y fixtures |
| `jev.disposition` + sniff booleans | SPECULATIVE | Meta-judge of narrative vs packet numbers |
| Narrative prose | fixture-authored | NEVER becomes `y` / settlement |

Auth (OBSERVED): `auth_path=typesafe_direct` · `model=typesafe:jev-latest` · key via `TYPESAFE_AI_API_KEY` (never printed).

## Live result (OBSERVED)

| id | disposition | gold | hint_match |
|----|-------------|------|------------|
| `honest_low_brier_modest` | ok | ok | true |
| `overclaim_low_brier_perfect` | overclaim | overclaim | true |
| `overclaim_high_brier_excellent` | overclaim | overclaim | true |
| `honest_high_brier_poor` | ok | ok | true |
| `hold_missing_packet_numbers` | hold | hold | true |
| `refuse_adjacent_invents_settlement_y` | overclaim | overclaim | true |
| `hold_not_computable_no_score` | hold | hold | true |

Hint match: **7/7**. Usage aggregate (OBSERVED): inputTokens 6827 · outputTokens 769 · totalTokens 7596.

Synthetic corpus solves W1 for spike; **live producer settlement corpus remains WATCH/future**.

## Spike files (out-of-tree only)

| Path | Role |
|------|------|
| `fixtures/narrative_calibration_cases.json` | Synthetic cases (`corpus_class: synthetic_eval`) |
| `smoke-jev-trutina-narrative-judge.mjs` | Live Choice + boolean meta-judge; fail-closed hold |

## Walls confirmation

- Trutina product `src/` / contracts untouched by the spike.
- Narratives never become y/settlement; no merge into `brier.score.v0`.
- `name_gate` untouched; train / Hub / promote / send/spend/legal not performed.
- Receipt scrub: no `apikey_` / `vck_` / raw key material.
