# T04B — DECOMPOSE calibration diagnostics

Status: SHADOW bounded implementation. DECOMPOSE opens only for registered exact and binned Murphy diagnostics.

## Implements

- `MURPHY_EXACT_V1`: exact weighted Murphy REL/RES/UNC identity on the validated BATCH cohort.
- `MURPHY_BINNED_V1`: explicit bin edges, empty-bin preservation, weighted bin means, within-bin variance/covariance correction, and raw-score reconstruction.
- deterministic grouping/order and reconstruction residual checks at absolute tolerance `1e-12`.
- exact elementary Murphy-loss integral used by A20.
- acceptance coverage A17–A20.

## Does not implement

- CORP/PAV recalibration diagnostics;
- ECE;
- Yates moment decomposition;
- Murphy dominance curves beyond the A20 elementary integral;
- T05 confidence intervals, bootstrap, clustered or serial resampling;
- ledger finalization, forecast routing, promotion, or weight mutation.

## Public dispatch

Only a registered `brier.decompose.input.v0` request with a linked `brier.batch.input.v0` manifest and a registered method enters DECOMPOSE. Malformed or unregistered requests retain the legacy `brier.score.v0` NOT_COMPUTABLE refusal behavior.

```text
DECOMPOSE_RUNTIME_ENABLED=true
INTERVAL_RUNTIME_ENABLED=false
CAN_PROMOTE=false
FORECAST_ROUTING=false
WEIGHT_MUTATION=false
LEDGER_FINALIZATION=false
```

Provenance: Trutina Spec 000 / T04B; T04A merged baseline `d6a0af93d8dd464fe96c85940f23042e9760d2cb`.
