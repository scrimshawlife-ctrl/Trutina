# T03 — BATCH aggregation + matched-reference BSS

Status: SHADOW bounded implementation. BATCH opens; DECOMPOSE remains NOT_COMPUTABLE.

## Implements

- cross-field cutoff/snapshot validation over the T02 contracts;
- deterministic weighted Brier aggregation using stable summation and canonical case ordering;
- exclusion/counting of VOID and UNSETTLED members without SCORE calls;
- zero-weight handling and effective sample-size diagnostic;
- matched-reference Brier Skill Score and paired loss difference;
- leakage refusal when a frozen reference was trained after the issue cutoff;
- acceptance coverage for A10–A16 and A25–A28.

## Does not implement

- Murphy decomposition or calibration bins (T04);
- confidence intervals/resampling (T05);
- multiclass/vector extensions (T06);
- ledger finalization;
- forecast minting or routing;
- promotion decisions;
- runtime weight mutation.

## Public dispatch

A structurally valid T02 manifest with `mode=BATCH` is dispatched through `brier.score()` to the BATCH report contract. Structurally incomplete BATCH requests continue to fail closed through the legacy score refusal packet. Semantically invalid but sufficiently linked manifests return a registered `brier.batch.report.v0` packet with the corresponding reason.

## Authority seal

```text
BATCH_RUNTIME_ENABLED=true
DECOMPOSE_RUNTIME_ENABLED=false
FORECAST_ROUTING=false
CAN_PROMOTE=false
WEIGHT_MUTATION=false
LEDGER_FINALIZATION=false
```

Provenance: Trutina Spec 000 / T03; T02 merged baseline `f808fc4bdd328a98e3d7becbc382ccc93da0e478`.
