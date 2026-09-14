# T02 — BATCH contract registration

Status: SHADOW contract registration only. BATCH runtime remains NOT_COMPUTABLE.

## Scope

This cycle registers the closed data contracts required before T03 aggregation/BSS and T04 DECOMPOSE work:

- `contracts/brier.batch.input.v0.schema.json`
- `contracts/brier.batch.report.v0.schema.json`
- `tests/test_batch_contracts.py`

It does not add a BATCH implementation, does not compute an aggregate, does not open DECOMPOSE, and does not grant ledger, promotion, forecast, or weight-mutation authority.

## Contract invariants

The input contract freezes cohort identity, issue window, cutoff snapshot linkage, weighting policy, deterministic member ordering, and a closed discriminated member union:

- `SETTLED`: binary `y`, TRUE/FALSE settlement, operator/ref/timestamp evidence.
- `VOID`: no `y`, explicit VOID settlement and nonblank reason.
- `UNSETTLED`: no settlement/outcome fields.

The future report contract freezes bounded output fields and authority flags. `forecast_eligible`, `can_promote`, `weight_mutation`, and `phenomenal` are always false; `ledger_id` is always null.

## Semantic checks intentionally deferred to T03 validator/runtime work

JSON Schema validates shape, types, closed fields, hashes, and timestamp syntax. The following cross-field semantics remain requirements from Spec 000 and are not claimed as implemented by T02 alone:

- `snapshot_as_of` equals `settlement_cutoff` as an instant.
- issued window start is before end.
- `issued_at` is inside the half-open issued window and no later than cutoff.
- SETTLED/VOID satisfy `issued_at <= settled_at <= settlement_cutoff` after timezone normalization.
- TRUE agrees with `y=1`; FALSE agrees with `y=0`.
- case/revision identifiers are unique.
- all members share the declared estimand/event definition/horizon/score convention.
- report count identities, weight totals, Brier arithmetic, reorder invariance, and positive weight-scale invariance.

Those semantics belong to T03 implementation/validation. They must fail closed and must not be silently repaired.

## Acceptance mapping

- A10–A13: T02 freezes the structural inputs/outputs and refusal boundaries; numerical aggregation/invariance remains T03.
- A25: timestamp syntax and cutoff fields are registered; instant-equivalence/inclusive cutoff logic remains T03.
- A26: terminal timestamps and snapshot linkage are structurally required where applicable; temporal ordering/reason selection remains T03.
- A27: VOID/UNSETTLED are closed schema variants and forbidden outcome fields fail validation.
- A28: one SETTLED + one VOID + one UNSETTLED snapshot is schema-valid; arithmetic/count assertions remain T03.

## Seal

```text
BATCH_RUNTIME_ENABLED=false
DECOMPOSE_RUNTIME_ENABLED=false
FORECAST_ROUTING=false
CAN_PROMOTE=false
WEIGHT_MUTATION=false
LEDGER_FINALIZATION=false
```
