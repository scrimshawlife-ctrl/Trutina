# T06 — extension review without activation

Status: REVIEW COMPLETE / NO RUNTIME ACTIVATION.

This cycle evaluates future scoring extensions and records their contract boundaries. It does not add a mode, schema, packet, formula identifier, route, or authority flag.

## Decision summary

### Multiclass mutually exclusive outcomes

Candidate future score:

`BS_multi = sum_k((p_k - 1[y=k])^2)`

Disposition: **DEFERRED / SEPARATE CONTRACT REQUIRED**.

Requirements before any future activation:
- K >= 2 fixed class labels with explicit canonical order;
- finite nonnegative probabilities with simplex sum within declared tolerance;
- separate formula identifier, e.g. `BRIER_MULTICLASS_UNSCALED_V1`;
- explicit score range `[0,2]` for the unscaled convention;
- any half-scaled convention must use a different formula identifier and contract;
- no multiclass value may be emitted in `brier.score.v0` or under `BRIER_BINARY_V1`.

At K=2, the unscaled vector score is exactly twice the current binary Trutina score. Therefore compatibility is mathematical, not packet-level equivalence.

### Multilabel outcomes

Disposition: **DEFERRED / NOT AN AUTOMATIC MULTICLASS EXTENSION**.

Each label is a distinct binary target. Any future aggregate must declare macro/micro weighting, missing-label behavior, prevalence interpretation, and case correlation. No implicit conversion to a simplex score is allowed.

### Ordinal outcomes

Disposition: **DEFERRED / DISTINCT PROPER-SCORE FAMILY**.

Ranked probability score or another ordinal-aware rule may be appropriate, but it must use a separate formula identifier and contract. Nominal multiclass Brier is not automatically an ordinal score.

### Interval-valued probabilities

Disposition: **NOT_COMPUTABLE AS A UNIQUE SCORE**.

An interval `[l,u]` does not identify one issued probability. Trutina must not silently score the midpoint. If an independently issued point probability exists, score that point and preserve the interval as metadata. Sensitivity loss bounds are analysis artifacts, not scores or confidence intervals.

### Soft / probabilistic labels

Disposition: **NOT_COMPUTABLE FOR `BRIER_BINARY_V1`**.

Replacing binary y with q changes the estimand; `(p-q)^2` alone omits Bernoulli outcome variance. A separate probabilistic-label contract would be required.

### Survival / time-to-event outcomes

Disposition: **DEFERRED / SEPARATE SURVIVAL CONTRACT**.

Survival Brier scoring requires explicit evaluation time, censoring semantics, and inverse-censoring-weight assumptions. It must not be routed through current binary SCORE/BATCH/DECOMPOSE contracts.

### Generic quadratic scoring on the simplex

Disposition: **SPECULATIVE / NO IMPLEMENTATION**.

A future quadratic proper score requires an explicit matrix, theoretical domain, scale, positive-definiteness/propriety argument, and separate formula identifier. No generic matrix input is authorized.

## Acceptance A24

For two classes with `p=[0.2,0.8]` and the second class observed:
- unscaled vector score = `(0.2-0)^2 + (0.8-1)^2 = 0.08`;
- half-scaled convention = `0.04`;
- current binary Trutina SCORE must continue to refuse vector input.

## Authority boundary

```text
NEW_RUNTIME_MODE=false
NEW_PACKET=false
NEW_SCHEMA=false
BINARY_SCORE_CHANGED=false
FORECAST_ROUTING=false
CAN_PROMOTE=false
WEIGHT_MUTATION=false
LEDGER_FINALIZATION=false
PRODUCTION_ACTIVATION=false
```

## Re-entry rule

Any future extension must begin with a new contract/spec cycle and must not reuse `brier.score.v0` merely because the underlying mathematics is related.

Provenance: Trutina Spec 000 section 8 / T06; current runtime baseline includes bounded SCORE, BATCH, DECOMPOSE and separately gated T05 uncertainty surfaces.
