# Spec 001 — SCORE

Mode: SCORE
Cycle: first implement when code is opened in this repo
Formula: `BRIER_BINARY_V1` = (p − y)²

## Accept

`payload_class = settled_forecast` with p in [0,1], y in {0,1}, settlement TRUE or FALSE, settled_by present.

## Refuse

| input | failure |
|---|---|
| forecast_request | NOT_COMPUTABLE (R004) |
| VOID | NOT_COMPUTABLE |
| slang_atom, tradition_atom, sign_atom, route_atom | SPECIALIST_LANE_VIOLATION |
| p outside [0,1] | NOT_COMPUTABLE |
| y not in {0,1} | NOT_COMPUTABLE |
| missing settled_by | NOT_COMPUTABLE |

## Fixtures (from Spec 010 E-B0)

- compute(0.8, 1.0) = 0.04
- compute(0.8, 0.0) = 0.64
- GATE_ADVISORY promotion stays false
- SHADOW computes score, ledger_id stays null

## Later modes (not this cycle)

BATCH mean over settled members.
DECOMPOSE Murphy identity: mean = reliability − resolution + uncertainty.
FUSION_ADVISORY inverse-Brier mix, ADVISORY_ONLY.
ROUTER_MICRO (predicted_quality − observed_quality)².
GATE_ADVISORY informs review, cannot promote.
PROJECT AAL-Viz only.
