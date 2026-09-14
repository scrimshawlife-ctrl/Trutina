# T04A — DECOMPOSE contract registration

Status: SHADOW schema-only cycle. DECOMPOSE runtime remains NOT_COMPUTABLE.

## Scope

This cycle registers the explicit input/report contracts required before DECOMPOSE activation:

- `contracts/brier.decompose.input.v0.schema.json`
- `contracts/brier.decompose.report.v0.schema.json`
- `tests/test_decompose_contracts.py`

The only registered methods are:

- `MURPHY_EXACT_V1`
- `MURPHY_BINNED_V1`

CORP/PAV, ECE, Yates moments, Murphy diagrams, and T05 uncertainty remain outside this activation slice.

## Boundaries

- Existing BATCH contracts and behavior are unchanged.
- DECOMPOSE remains a runtime stub during this schema cycle.
- No promotion, forecast routing, ledger finalization, or weight mutation is introduced.
- The runtime implementation must use the validated BATCH cohort rather than invent a parallel settlement or weighting path.

## Next lawful cycle

T04B may activate DECOMPOSE against these contracts and must cover A17–A20. T05 interval/resampling work remains a later independent cycle.

```text
DECOMPOSE_RUNTIME_ENABLED=false
INTERVAL_RUNTIME_ENABLED=false
CAN_PROMOTE=false
FORECAST_ROUTING=false
WEIGHT_MUTATION=false
LEDGER_FINALIZATION=false
```

Provenance: Trutina Spec 000 / T04 contract registration; T03 merged baseline `1bbf8efa346e99ced5c3bfb9ec9d7eb0b5eacc37`.
