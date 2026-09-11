# Spec 000 — Trutina spine

Display: Trutina
Specialist: `abx.brier`
Function: `trutina.score`
Packet: `brier.score.v0`
Home: `yggdrasil.replay`
Parent: Notion Spec 010, Spec 009 R004B
Lane: SHADOW specify

## Owns

Calibration scoring of operator-settled (p, y). Modes SCORE, BATCH, DECOMPOSE. Advisory stubs FUSION_ADVISORY, ROUTER_MICRO, GATE_ADVISORY, PROJECT.

## Does not own

Forecast mint. Promotion. Weight mutation. Hyperlex form. Athanor efficacy. Semion triad. Yggdrasil route_class. Canon ledger ids.

## Formula

`BRIER_BINARY_V1` = (p − y)²

- p ∈ [0, 1]
- y ∈ {0, 1}
- VOID → NOT_COMPUTABLE, no score
- missing settlement receipt → NOT_COMPUTABLE

## Router

| packet | rule | result |
|---|---|---|
| `settled_forecast` | R004B | `abx.brier` |
| `forecast_request` | R004 | NOT_COMPUTABLE |
| slang_atom / tradition_atom / sign_atom / route_atom | other specialists | SPECIALIST_LANE_VIOLATION if forced here |

## Honesty

Every packet carries OBSERVED / INFERRED / SPECULATIVE / NOT_COMPUTABLE. SCORE on a settled pair with a receipt is OBSERVED. BATCH mean over settled members is OBSERVED. Fusion weights are INFERRED and ADVISORY_ONLY.

## Precursor

`specs/000-brier-spine` is derivative. Do not delete. Do not treat it as the live spine.
