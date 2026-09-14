# T05B — statistical uncertainty + temporal dependence

Status: SHADOW bounded implementation. Inferential intervals are optional diagnostics over frozen evaluation records; deterministic point scores and Murphy decomposition are unchanged.

## Implements

- `IID_PERCENTILE_BOOTSTRAP_V1` for an explicitly declared IID case-sampling design.
- `CLUSTER_PERCENTILE_BOOTSTRAP_V1` resampling whole declared independent clusters.
- `MOVING_BLOCK_PERCENTILE_BOOTSTRAP_V1` resampling contiguous ordered blocks with a declared block length.
- estimands `BRIER_MEAN`, `PAIRED_DELTA`, and `BSS`.
- matched model/reference records are always resampled together.
- caller-supplied seed and pinned `TRUTINA_LCG32_V1` deterministic resampling generator.
- linear percentile quantiles at the requested confidence level.
- explicit `DEGENERATE_SAMPLE`, `ZERO_REFERENCE_REPLICATE`, `SAMPLING_DESIGN_UNKNOWN`, `INVALID_DESIGN`, `RESOURCE_LIMIT`, and `NONFINITE_RESULT` unavailable states.
- A21–A23 acceptance coverage.

## Important semantics

- Sampling uncertainty is not Murphy decomposition `UNC` and does not change the observed point estimate.
- The runtime never infers IID, cluster, stationarity, cluster field, block length, seed, or weighting design.
- A BSS replicate with zero reference loss is counted and makes the BSS interval unavailable; it is never silently dropped. A paired-delta interval may still be computed from the same matched records.
- One case, fewer than two independent clusters, or a degenerate estimand sample returns no population interval instead of a false zero-width interval.
- Fixed case weights travel with sampled cases only when the caller explicitly declares a supported fixed-weight design.
- The 20-million case-draw work cap is checked before resampling; clustered work uses a worst-case per-replicate bound.

## Not implemented / not authorized

- model refitting or training uncertainty;
- automatic block-length selection or stationarity diagnosis;
- automatic cluster discovery;
- survey/inclusion-weight bootstrap guarantees;
- sequential/multiplicity inference;
- promotion, forecast routing, ledger finalization, or weight mutation.

```text
INTERVAL_RUNTIME_ENABLED=true
POINT_ARITHMETIC_MUTATION=false
MURPHY_UNC_IS_SAMPLING_INTERVAL=false
CLOCK_DERIVED_SEED=false
CAN_PROMOTE=false
FORECAST_ROUTING=false
WEIGHT_MUTATION=false
LEDGER_FINALIZATION=false
```

Provenance: Trutina Spec 000 / T05B; T05A merged baseline `58e596d15bb4980fc6000f2f2e44964221b83518`.
