# T05A — uncertainty/resampling contract registration

Status: SHADOW schema-only cycle. Interval computation remains disabled.

## Scope

This cycle registers the request/report contracts needed before any inferential runtime work:

- `contracts/brier.interval.request.v0.schema.json`
- `contracts/brier.interval.report.v0.schema.json`
- optional `interval` subrecord in `brier.batch.report.v0`
- `tests/test_interval_contracts.py`

Registered methods:

- `IID_PERCENTILE_BOOTSTRAP_V1`
- `CLUSTER_PERCENTILE_BOOTSTRAP_V1`
- `MOVING_BLOCK_PERCENTILE_BOOTSTRAP_V1`

Registered estimands:

- `BRIER_MEAN`
- `PAIRED_DELTA`
- `BSS`

## Boundaries

- Sampling uncertainty is distinct from Murphy decomposition `UNC`.
- A caller must declare the sampling assumption and resampling unit; runtime may not infer them from the data.
- Seed and RNG version are explicit contract fields. No clock-derived seed is permitted.
- Paired estimands require reference identity and matched-reference hash.
- The contract allows unavailable intervals with explicit reasons; point estimates remain separate.
- BATCH, DECOMPOSE, SCORE arithmetic and authority flags are unchanged.
- No bootstrap/resampling code is activated in this cycle.

## Next lawful cycle

T05B may implement only the registered methods against these contracts and must satisfy A21–A23. It must preserve matched records, report zero-reference BSS replicates instead of dropping them, and fail unavailable when the declared design is insufficient.

```text
INTERVAL_RUNTIME_ENABLED=false
CLOCK_DERIVED_SEED=false
CAN_PROMOTE=false
FORECAST_ROUTING=false
WEIGHT_MUTATION=false
LEDGER_FINALIZATION=false
```

Provenance: Trutina Spec 000 / T05A; T04B merged baseline `56237d1ef544add51d37f25bf9ba21293d894d65`.
