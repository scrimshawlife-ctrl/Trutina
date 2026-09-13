# Spec 000 — Trutina Brier module specification

Display: Trutina
Specialist: `abx.brier`
Function: `trutina.score`
Packet: `brier.score.v0`
Home: `yggdrasil.replay`
Parent: Notion Spec 010, Spec 009 R004B
Lane: SHADOW specify

## BOUNDARY

Status: SHADOW specification; research cutoff 2026-09-12. This does not govern or activate.
This revision completes the scoring design; it does not implement or open another mode.
The constitution, bind receipt, specialist identity, packet name and authority flags remain authoritative.
Requirements below are INFERRED implementation decisions unless explicitly marked OBSERVED or SPECULATIVE.
MUST means a proposed acceptance requirement within the existing engineering boundary, not an amendment to governance.

Assumptions: binary events have a stable definition and an upstream operator settlement; evaluation uses immutable issued probabilities; the package remains `brier`; no external adapter or settlement authority is inferred from a local numeric pair.

## EVIDENCE PACKET

OBSERVED repository baseline: `2724c9baf6e5837441f65e569347c8e713a2a32e` (2026-09-11).

| Surface | Observed evidence and consequence |
|---|---|
| `constitution.md`, `specs/BIND.md` | SCORE is binary T0; specialist `abx.brier`, home `yggdrasil.replay`; training, promotion, Hub and ledger finalization gated |
| `src/brier/score.py`, `specs/001-score/engineering.md` | Only SCORE is live; all six other recognized modes return null / NOT_COMPUTABLE |
| `contracts/brier.score.v0.schema.json` | Closed output object, binary `brier` in [0,1] or null; no aggregate, decomposition or interval fields |
| `src/brier/core.py` | Atomic squared error and an unvalidated arithmetic mean helper exist; no decomposition or BSS implementation |
| `specs/000-trutina-spine/data-model.md` | Settled input shape exists in prose; no executable input schema |
| `src/brier/compat/abraxas.py`, `src/brier/ledger.py` | Placeholder text exists; working adapters/ledger emission cannot be claimed |
| `specs/000-brier-spine/spec.md` | Preserved derivative precursor, with older packet/API examples; not the live contract |
| `tests/test_core.py`, `tests/test_score.py` | Limited arithmetic and refusal fixtures exist; coverage does not establish the stronger acceptance requirements below |
| Repository inventory | No repository AGENTS/CONTEXT file or documentation validator found; README is existing navigation |

Notion Spec 010 and Spec 009 R004B are referenced by the repository bind receipt. Their live contents are NOT_COMPUTABLE from this checkout; live Notion consistency is not claimed. Trutina follows its own constitution, bind receipt and normal PR/review workflow. Older milestone/model-card wording is not proof of current implementation; source inspection establishes the live-mode inventory above.

## TASK

Specify deterministic scoring of settled probabilities and the bounded analytical contracts needed for later BATCH and DECOMPOSE cycles. Measure probabilistic accuracy with a proper score and report calibration diagnostics with their assumptions. A single Brier value does not establish calibration, usefulness, causal improvement or promotion readiness. [R1, R2]

### Owns

Calibration scoring of operator-settled (p, y). Modes SCORE, BATCH, DECOMPOSE. Advisory stubs FUSION_ADVISORY, ROUTER_MICRO, GATE_ADVISORY, PROJECT.

### Does not own

Forecast mint. Promotion. Weight mutation. Hyperlex form. Athanor efficacy. Semion triad. Yggdrasil route_class. Canon ledger ids.

## OUTPUT EXPECTED

### 1. Binary scoring semantics and invariants

`BRIER_BINARY_V1` = (p − y)²

- p ∈ [0, 1]
- y ∈ {0, 1}
- VOID → NOT_COMPUTABLE, no score
- missing settlement receipt → NOT_COMPUTABLE

For an eligible pair, loss `l_i = (p_i - y_i)^2`; lower is better, range [0,1]. For a Bernoulli event with true conditional probability q, expected loss is `(p-q)^2 + q(1-q)`, uniquely minimized by p=q. This is an expectation property, not a promise that a more honest forecast wins on each realization. [R1]

The event represented by p is always y=1. Do not threshold p before scoring, invert label conventions implicitly, clip invalid probabilities, smooth endpoint values, or convert VOID/missing outcomes to zero. Exact p=0 and p=1 are valid. No minimum epsilon is needed for squared error. The atomic kernel is mathematical and cannot certify settlement; the public SCORE boundary MUST enforce settlement eligibility.

Use finite binary64 arithmetic, validate before numeric conversion, and compare expected values with absolute tolerance `1e-12` and relative tolerance `1e-12`. Preserve full precision internally; decimal rounding is presentation only. Use stable summation (for example `math.fsum`) and deterministic member ordering for aggregates. Canonical hashing belongs to a defined receipt serializer, not an assumed decimal display. No score operation reads a clock, generates identifiers or mutates inputs.

### 2. Behavioral chain

| Journey | Workflow | State Transition | Contract | Acceptance Test | Implementation Task |
|---|---|---|---|---|---|
| Inspect a settled claim | Validate atom and receipt; compute loss | received → eligible → scored | SCORE, section 3 | A01–A05 | T01 |
| Inspect an open or invalid claim | Validate lane/settlement; emit refusal | received → refused | Null score with failure | A06–A09 | T01 |
| Review a cohort | Freeze membership; validate; aggregate | proposed cohort → validated → reported | BATCH proposal, section 4 | A10–A13 | T02 then T03 |
| Compare with a benchmark | Join identical cases; evaluate both | matched → compared or comparison unavailable | BSS and paired difference, section 5 | A14–A16 | T03 |
| Diagnose forecast quality | Compute exact or binned components | scored cohort → diagnostic report | DECOMPOSE proposal, section 6 | A17–A20 | T02 then T04 |
| Assess statistical evidence | Freeze estimand/resampling design; estimate interval | report → uncertainty estimated or NOT_COMPUTABLE | Section 7 | A21–A23 | T05 |
| Review extension | Evaluate mathematical and schema compatibility | proposal → deferred | Section 8 | A24 | T06 |

These are analytical workflow states, not persisted canon states. Refusal is terminal for that immutable input; a corrected settlement creates a new input revision with its own provenance.

### 3. SCORE input/output contract

The detailed atomic contract and test matrix live in [Spec 001](../001-score/spec.md). The existing output schema remains unchanged. Successful packets have `formula=BRIER_BINARY_V1`, finite numeric `brier`, `honesty=OBSERVED`, `failure=null`, `ledger_id=null`, and all authority booleans false. Refusals have `brier=null`, `honesty=NOT_COMPUTABLE` and an existing failure code.

OBSERVED implementation gaps: the current wrapper permits omitted payload_class/settlement, coerces inputs with `float(p)` and `int(y)`, does not verify TRUE/y=1 or FALSE/y=0 agreement, and can propagate an invalid corpus_ref. Fractional y can be truncated. These are requirements to repair in T01, not verified capabilities of this specification change.

Receipt authenticity and forecast issue chronology are upstream responsibilities. `settled_by` alone is not cryptographic evidence. A structurally valid input can be scored locally, but missing externally verifiable lineage makes external provenance verification NOT_COMPUTABLE. Preserve this distinction in the accompanying evaluation record; do not invent fields in the closed v0 packet.

### 4. BATCH proposal: cohort, weights and report schema

Current runtime: NOT_COMPUTABLE stub. The following is an INFERRED contract for a later cycle, not a newly registered packet schema. Do not add these fields to `brier.score.v0`.

Freeze a cohort manifest before calculating any metric. Required manifest fields are `cohort_id`, `corpus_ref`, `manifest_hash`, `forecast_version`, `event_definition`, `positive_label`, `horizon`, `issued_window`, `settlement_cutoff`, `eligibility_policy`, `weight_policy`, `member_order` and `members`. IDs/references are nonempty strings, hashes are lowercase SHA-256 hex strings, times are offset-qualified ISO-8601, and windows are ordered start/end pairs. Unknown additional fields are refused by the future schema. Members are records with unique `case_id`, immutable `forecast_id` and `forecast_revision`, `event_id`, `issued_at`, optional `cluster_id`, a SCORE atom, and finite nonnegative `weight` (default 1). Hashing format must be explicitly versioned before implementation; the manifest hash cannot include itself.

Evaluation uses all validated TRUE/FALSE members eligible at the declared cutoff. VOID and genuinely unsettled cases are excluded and counted separately. Malformed records, contradictory settlements, duplicate case/revision IDs, mixed event definitions, mixed horizons or mixed score conventions fail the entire request; they are not silently dropped. For revisions or repeated forecasts of one event, select one revision by an outcome-independent manifest rule or retain them as correlated cases and disclose the estimand. Later settlement corrections create a superseding manifest; old reports are not overwritten.

For included weights, `W=sum(w_i)` and `BS=sum(w_i*l_i)/W`. Require W>0 and finite. Zero-weight valid members contribute no mass but remain counted. Default weight policy is equal case weights. Scaling all weights by a positive constant leaves BS unchanged. Positive outcome-independent weights preserve conditional propriety; weighting by realized class changes the target distribution. Report class-balanced loss separately and label its altered estimand. Do not call oversampled or inverse-class-weighted evaluation representative of deployment prevalence without a justified sampling correction. [R1, R2]

Future report field contract:

| Field | Type and semantics |
|---|---|
| `status`, `honesty` | `COMPUTABLE`/`NOT_COMPUTABLE`; empirical arithmetic OBSERVED, inferential estimates INFERRED |
| `formula`, `score_scale`, `manifest_hash`, `corpus_ref` | Binary formula, `binary_0_1`, immutable cohort linkage |
| `n_total`, `n_scored`, `n_void`, `n_unsettled`, `n_zero_weight` | Nonnegative integers; total = scored + void + unsettled for a valid manifest; zero-weight is a subset of scored |
| `weight_sum`, `sum_weighted_loss`, `brier` | Finite numeric sufficient statistics; brier null when no positive eligible mass |
| `event_count`, `nonevent_count`, `prevalence` | Unweighted counts plus weighted event rate; event + nonevent = scored |
| `weight_ess` | `W^2/sum(w_i^2)` when W>0; weight concentration diagnostic, not a serial-dependence correction |
| `coverage` | scored / total or null for empty total; also expose refusal/exclusion counts |
| `baseline`, `decomposition`, `interval` | Optional typed subrecords in sections 5–7; omitted when not requested, null with a reason when requested but unavailable |
| `reasons` | Stable reason strings, including `EMPTY_COHORT`, `ZERO_WEIGHT`, `INVALID_MEMBER`, `DUPLICATE_CASE`, `MIXED_ESTIMAND` |
| `forecast_eligible`, `can_promote`, `weight_mutation`, `phenomenal`, `ledger_id` | false, false, false, false, null |

A later schema cycle must register/version this report shape and its member records before a mode-opening cycle (constitution X). API enum membership alone is not authorization to execute a mode.

Rare events: show prevalence, class counts, settlement coverage and benchmark loss beside BS. An always-negative forecast has BS equal to event prevalence, which can be small while missing every event. Per-class or prespecified subgroup scores are diagnostics, not substitutes for the primary population score. Different cohorts or base rates must not be ranked by raw BS alone. Missing/late settlements can bias the evaluated subset; report coverage by horizon and subgroup when available.

### 5. Baselines and Brier skill score

On exactly matched cases and weights, `BSS = 1 - BS_model / BS_reference`. BSS=1 is perfect relative skill when reference loss is positive; 0 is equal loss; negative values are valid and have no universal lower bound. Record both losses, their scale, case-set hash, reference identity/version and reference training cutoff. Never average per-case ratios. BSS is a relative statistic; its finite-sample ratio bias and dependence on the reference must be disclosed. [R3]

Default benchmark is a supplied, frozen forecast available at issuance, such as climatology estimated exclusively from prior training data. Persistence is acceptable only with a declared horizon and information cutoff. Do not estimate an operational benchmark on evaluation outcomes. The evaluation prevalence baseline `q_bar` with loss `q_bar*(1-q_bar)` is allowed only under the label `in_sample_climatology_descriptive`; it is not an out-of-sample benchmark.

Reference subrecord: `reference_id:string`, `reference_version:string`, `training_cutoff:timestamp|null`, `kind:external_frozen|in_sample_climatology_descriptive`, `matched_manifest_hash:string`, `brier:number|null`, `bss:number|null`, `paired_delta:number|null`, `reason:string|null`. Here `paired_delta=BS_model-BS_reference`, lower favors the model.

Missing/misaligned reference, incompatible scale or leakage makes BSS NOT_COMPUTABLE while preserving the model's valid BS. If reference loss is exactly zero, BSS=null with `ZERO_REFERENCE_LOSS`, including when both models are perfect. Do not add epsilon. Very small positive denominators yield a valid but unstable ratio; emit `SMALL_REFERENCE_LOSS` using an explicitly recorded advisory threshold (default `1e-12`) without clipping the result. Overflow yields null with `NONFINITE_RESULT`.

### 6. Decomposition and calibration diagnostics

Current runtime: NOT_COMPUTABLE stub. All formulas below use the same validated cohort and normalized weights `a_i=w_i/W`. Terms describe the empirical cohort; their population interpretation requires inference.

#### Exact Murphy decomposition

Group by exactly equal numeric forecast probabilities (no hidden decimal rounding). Let group weight `A_g=sum(a_i)`, forecast `p_g`, group event rate `q_g=sum(a_i*y_i)/A_g`, and overall `q=sum(a_i*y_i)`.

`REL=sum(A_g*(p_g-q_g)^2)`

`RES=sum(A_g*(q_g-q)^2)`

`UNC=q*(1-q)`

`BS=REL-RES+UNC`.

Empty/zero-mass groups are absent. On unique probabilities each group may be a singleton: the identity is still correct, but REL and RES become poor population estimates. Report group counts/masses and singleton fraction. UNC is outcome variability, not a confidence interval. Small empirical REL does not prove population calibration. [R4]

#### Binned diagnostic with exact correction

Require explicit strictly increasing edges from 0 to 1. Intervals are `[left,right)` with the final interval including 1. Default display only: ten equal-width bins, recorded verbatim; callers may supply prespecified edges. Empty bins retain count 0 with null means. Use each occupied bin's weighted mean forecast `p_bar_g` and outcome `q_g` in REL/RES, and also compute within-bin weighted variance `V_g=mean_g((p_i-p_bar_g)^2)` and covariance `C_g=mean_g((p_i-p_bar_g)*(y_i-q_g))`.

`WITHIN=sum(A_g*(V_g-2*C_g))`

`BS_raw=REL_binned-RES_binned+UNC+WITHIN`.

WITHOUT this correction the three terms reconstruct the loss of the bin-mean forecasts, not generally the raw predictions. WITHIN may be negative. Include `raw_brier`, `binned_brier`, `within_correction`, `reconstruction_residual`, method, edges, bin means, counts and masses. Require absolute reconstruction residual <=1e-12; otherwise return `NUMERICAL_IDENTITY_FAILURE`. Never truncate negative correction or diagnostic components to force an identity. This correction is essential for continuous forecasts. [R4]

#### Yates moment identity

An optional later DECOMPOSE method `YATES_MOMENTS_V1` uses population-normalized weighted moments (denominator W):

`BS=(mean(p)-q)^2 + Var(p) + q*(1-q) - 2*Cov(p,y)`.

Expose bias squared, forecast variance, outcome variance and twice covariance; do not name these REL and RES. This is the elementary squared-error moment identity. More elaborate conditional Yates terms are SPECULATIVE pending an exact chosen definition. No sample n-1 correction may be mixed into an exact empirical identity.

#### CORP and ECE

Candidate method `CORP_PAV_V1`: sort probabilities, combine ties with their weights, fit a nondecreasing isotonic event-rate curve using PAV. With raw loss S, same-sample isotonic loss S_iso and constant-prevalence loss S_const, define `MCB=S-S_iso`, `DSC=S_const-S_iso`, `UNC=S_const`; then `S=MCB-DSC+UNC`. Record fitted blocks and method separately from Murphy terms. PAV fits are diagnostic projections; they do not mutate issued probabilities. In-sample improvement is not evidence that deployment recalibration improves forecasts. Evaluate any proposed recalibrator on a separate chronological holdout. The method's monotonicity assumptions and uncertainty procedure must accompany its interpretation. [R5]

If ECE is displayed, name the variant: binary event-probability L1 ECE is `sum(A_g*abs(p_bar_g-q_g))`. Record binning, norm, sample size, weights and target (event probability, classwise or top-label). ECE is neither BS nor REL; top-label calibration is weaker than calibration of the whole class vector. Finite sample bias and bin sensitivity can change rankings. Do not use ECE alone to rank forecasts or authorize promotion. [R6, R7]

#### Murphy diagrams

Optional analytical curve, distinct from Murphy's REL/RES decomposition: for threshold t in [0,1], use elementary loss `e_t(p,y)=2*t` if y=0 and p>t, `2*(1-t)` if y=1 and p<=t, and 0 otherwise. Its integral over t equals binary `(p-y)^2`. Record this factor-of-two and tie convention; other literature conventions may use a different normalization. Curves crossing imply ranking depends on the scoring rule/decision threshold. A finite grid cannot prove dominance at every threshold; exact integration must split at every unique p. Statistical dominance needs simultaneous uncertainty, not separate pointwise intervals. Keep the diagnostic informational. [R8]

### 7. Statistical uncertainty and temporal dependence

The observed cohort mean is deterministic. An interval estimates a named population quantity under a declared sampling model; it is not uncertainty about arithmetic and not the UNC decomposition component. Atomic SCORE emits no sampling interval. With unknown sampling design, keep the point score and return interval=null / `NOT_COMPUTABLE` with `SAMPLING_DESIGN_UNKNOWN`.

INFERRED default for an explicitly IID, equal-weight sample: percentile bootstrap of whole case records, 2,000 replicates, confidence level 0.95, caller-supplied seed, pinned PRNG/library version, linear quantiles at 0.025/0.975. The interval record requires `estimand`, `method`, `confidence_level`, `seed`, `rng_version`, `replicates_requested`, `replicates_valid`, `resampling_unit`, `block_length`, `lower`, `upper`, `status`, `reason`. No clock-derived seed. Bootstrap randomness is isolated in the report workflow and fully specified; atomic scoring remains deterministic. One case, constant loss, or fewer than two independent resampling units returns an unavailable interval with `DEGENERATE_SAMPLE`, never a falsely certain zero-width population interval.

For model differences/BSS, resample matching model/reference/outcome records together and recompute both numerator and denominator in each replicate. Never bootstrap model and reference independently. If any BSS replicate has zero reference loss, do not silently discard it: record the count and return BSS interval=null / `ZERO_REFERENCE_REPLICATE`; paired loss-difference intervals may still be reported. Percentile intervals are approximate, particularly with rare events or few units; validate empirical coverage in a later implementation study. [R3, R9]

For clustered events resample entire independent clusters. For serial dependence use moving-block resampling of ordered records with a declared block length, drawing contiguous blocks with replacement and truncating to original length. Preserve paired forecasts, timestamps and attached weights. Block length and the assumption of approximate stationarity must come from an evaluation design; absent evidence, the interval is NOT_COMPUTABLE. Weight ESS cannot replace a dependence model. Nonstationary drift, overlapping horizons, multiple forecasts of one event and repeated entities invalidate an automatic IID interval. [R9, R10]

Outcome-independent fixed case weights may travel with resampled cases only when a superpopulation case-sampling estimand is explicitly intended. Survey, inverse-inclusion, frequency or estimated weights require their own design-aware resampling contract; no generic weighted-bootstrap guarantee is claimed. Inference over model training requires refitting within the design; resampling frozen predictions estimates evaluation-sample variability only. Repeated rolling-window alerts or many subgroup comparisons require a separate multiplicity/sequential analysis plan before significance claims.

### 8. Generalized Brier, interval inputs and future extensions

SPECULATIVE / future schema cycle: for mutually exclusive, exhaustive K>=2 classes, `BS_multi=sum_k((p_k-1[y=k])^2)` with range [0,2]. Require explicit unique class labels, a fixed matching vector order even if a class is absent in a batch, finite nonnegative probabilities, and simplex sum within 1e-12 of 1. Reject malformed vectors; any normalization must be an explicit upstream transform with provenance. Optional half-scaling is a different declared convention. At K=2 the unscaled vector score equals twice current binary SCORE. No multiclass score may be emitted under `BRIER_BINARY_V1` or inserted into v0's binary field. Classwise one-vs-rest decompositions can be summed consistently but do not establish full-vector calibration. [R11]

A generic positive-definite quadratic form on the simplex is a possible generalized proper score, but requires an explicit matrix, scale, theoretical domain and separate formula identifier. Multilabel events require separate binary targets and explicit macro/micro aggregation; ordinal targets may warrant ranked probability score. These are not automatic extensions of the current atom.

An interval `[l,u]` for p does not determine a unique probability; do not take its midpoint silently. If an independently issued point p also exists, score that p and retain the interval only as upstream metadata. Optional future sensitivity bounds for settled y are `[l^2,u^2]` for y=0 and `[(1-u)^2,(1-l)^2]` for y=1; these are loss ranges, not confidence intervals or scores. Soft labels, unresolved outcomes, interval-censored events and survival outcomes remain NOT_COMPUTABLE for binary SCORE. In particular `(p-q)^2` for uncertain label q omits `q*(1-q)` from expected Bernoulli loss. Survival Brier scoring needs time/censoring and inverse-censoring-weight assumptions; continuous predictions/quantiles/intervals need distinct proper-score contracts. [R1, R2]

Recent research disposition: the 2026 scoring-rule review supports retaining a transparent proper-score foundation. The 2025 Cutoff Calibration Error work and 2026 Averaged Two-Bin calibration paper motivate future diagnostics addressing testability and truthfulness, with their assumptions checked before adoption. They do not imply existing ECE estimates are proper scores. March 2026 smooth-calibration research and August 2026 LLM scoring-rule experiments remain research leads; no T0 training or default metric change follows from them. [R2, R12–R15]

Inverse-Brier fusion is a SPECULATIVE heuristic, undefined at zero without a declared regularizer and not generally optimal under correlated forecast errors. ROUTER_MICRO's squared quality error is not a binary Brier score unless its target meets the binary contract. Advisory stub behavior stays as currently implemented. A low score cannot set any authority flag true.

### 9. Observability, failures and resource handling

Return stable refusal semantics; preserve the v0 packet vocabulary. More detailed reasons belong in a future report or caller diagnostic record, never unregistered v0 properties. Emit counts of invalid/VOID/unsettled cases, duplicate revisions, zero-weight members, per-mode refusal, baseline coverage and unavailable inference, tagged by formula/version and cohort hash. Avoid logging raw operator identifiers or full payloads. Operational latency can be recorded outside the deterministic packet by the caller.

Atomic processing is O(1); aggregate arithmetic is O(n), exact grouping and PAV O(n log n) including sorting. A future BATCH request defaults to a declared 100,000-member cap; bootstrap defaults to a 20-million case-resample work cap. These are advisory resource defaults, not measured capacity. Reject an over-budget request with `RESOURCE_LIMIT` before work; never silently truncate, downsample or emit a partial mean as complete. Allow explicit recorded overrides only at the caller boundary. Performance budgets beyond these limits are NOT_COMPUTABLE until benchmarks exist.

## VALIDATION

Acceptance criteria below specify subsequent implementation tests. Completing this document does not mark them passed against current runtime.

| ID | Fixture / invariant | Required result |
|---|---|---|
| A01 | (p,y)=(0,0),(1,1),(0,1),(1,0) | 0,0,1,1 |
| A02 | (0.8,1),(0.8,0),(0.7,1) with matching settlement | 0.04,0.64,0.09 within tolerance |
| A03 | p=0.5, either outcome | 0.25 |
| A04 | Complement p and y consistently | Identical loss |
| A05 | Repeat same input; inspect input after call | Same semantic output, unchanged input, frozen flags and null ledger |
| A06 | Missing settlement/payload/settled_by; whitespace-only operator; contradictory TRUE/0 | Null/refusal |
| A07 | p outside [0,1], NaN/infinity, boolean/string p; fractional/string/boolean y | Null/refusal before coercion |
| A08 | VOID, open forecast_request, other specialist atom, unsupported mode | Correct null/failure; no accidental score |
| A09 | Conflicting canonical/alias fields; malformed corpus_ref/time; non-object atom | Deterministic refusal, schema-valid packet |
| A10 | Losses 0.04,0.64 with weights 1,3 | W=4, weighted sum=1.96, BS=0.49; uniform BS=0.34 |
| A11 | Empty cohort; all VOID/unsettled; all zero weights | Null aggregate and explicit reason/counts |
| A12 | Negative/nonfinite weight, invalid settled member, duplicate case, mixed scale | Entire request refused |
| A13 | Reorder members or multiply weights by 7 | Same aggregate within tolerance and declared canonical ordering |
| A14 | BS=0.125, reference=0.25; BS=0.5, reference=0.25 | BSS=0.5 and -1 respectively |
| A15 | Both losses zero; missing reference; mismatched cases | BSS null, model BS retained |
| A16 | Reference fitted after issue cutoff | Operational comparison refused as leakage |
| A17 | p=[0.25,0.25,0.75,0.75], y=[0,1,0,1] | BS=0.3125, REL=0.0625, RES=0, UNC=0.25 |
| A18 | p=[0.1,0.4], y=[0,1], single bin | raw=0.185, binned=0.3125, WITHIN=-0.1275; reconstruction exact within tolerance |
| A19 | Empty bins, ties, endpoint 1, singleton groups, single outcome class | Defined assignments/null empty means; identity preserved and limitations reported |
| A20 | Integrate elementary Murphy loss at p=0.8 | y=1 area=0.04; y=0 area=0.64; normalized consistently |
| A21 | Fixed resampling design/seed/version | Reproducible bounds and complete method metadata |
| A22 | Paired clustered/time series comparison | Preserve case pairs and resampling units; missing design returns unavailable interval |
| A23 | Degenerate sample or zero-reference bootstrap replicate | Explicit unavailable interval; no dropped replicates or certainty claim |
| A24 | Two-class p=[0.2,0.8], y=second class | Future full-vector score=0.08, half=0.04; current SCORE refuses vector |

T01: repair strict input validation and semantic schema tests in the existing SCORE surface; preserve numeric kernel, alias compatibility only where unambiguous, and frozen packet flags. T02: in a separate schema-only cycle, translate sections 4–7 into versioned closed report/input schemas, fixtures and deterministic receipt serialization. T03: later implement BATCH and benchmark arithmetic. T04: later implement exact/binned Murphy and moment identities; CORP/diagrams can be independently reviewed within DECOMPOSE. T05: implement the explicit resampling methods and assess coverage using synthetic IID, clustered, serial and rare-event designs. T06: review multiclass and other extensions without enabling them. Each task depends on the prior relevant contract and acceptance fixtures; no schema-change cycle simultaneously opens a new mode.

For this documentation revision, validate only Markdown links, embedded examples, arithmetic fixtures, whitespace/diff scope and consistency with the unchanged v0 schema. Runtime test-suite success is not a requirement for a spec-only edit and would not establish the future modes. Runtime validation in T01 must include output-schema validation and the rejection cases above, using tolerant float comparisons instead of literal decimal equality.

## RESIDUAL RISKS

NOT_COMPUTABLE: live Spec 009/010 parity, upstream receipt authentication, production data quality/prevalence, external adapter behavior, corpus-specific baseline, dependence/block-length choice, valid confidence coverage and performance capacity. These require evidence not present in the repository. No external repository import, ledger append or runtime activation is implied.

## RECOMMENDED NEXT ADVISORY ACTION

Review this specification against the operator's live Spec 010, then implement T01 as the next bounded SCORE validation cycle. Keep later report schemas and mode openings in separate cycles as the constitution requires.

## Research sources

Sources checked 2026-09-12. Dates below are publication/submission dates, not search-index crawl dates. Recent preprints are distinguished from published work. Mathematical operational choices above are INFERRED and are not attributed as verbatim requirements of these sources.

- R1. Gneiting & Raftery (2007), [Strictly Proper Scoring Rules, Prediction, and Estimation](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf). Proper scoring and outcome-domain distinctions.
- R2. Waghmare & Ziegel (2026; online November 2025), [Proper Scoring Rules for Estimation and Forecast Evaluation](https://www.annualreviews.org/content/journals/10.1146/annurev-statistics-042424-050626). Current review; theoretical foundation.
- R3. Bradley, Schwartz & Hashino (2008), [Sampling Uncertainty and Confidence Intervals for the Brier Score and Brier Skill Score](https://journals.ametsoc.org/doi/10.1175/2007WAF2007049.1). Sampling/ratio uncertainty.
- R4. Stephenson, Coelho & Jolliffe (2008), [Two Extra Components in the Brier Score Decomposition](https://journals.ametsoc.org/doi/pdf/10.1175/2007WAF2006116.1). Exact versus binned decomposition; publisher abstract accessible, full-text fetch unavailable during review.
- R5. Dimitriadis, Gneiting & Jordan (2021; preprint 2020), [Evaluating probabilistic classifiers: Reliability diagrams and score decompositions revisited](https://arxiv.org/abs/2008.03033). CORP/PAV diagnostics.
- R6. Vaicenavicius et al. (2019), [Evaluating model calibration in classification](https://proceedings.mlr.press/v89/vaicenavicius19a.html). Calibration targets and vector versus reduced calibration.
- R7. Roelofs et al. (2022), [Mitigating Bias in Calibration Error Estimation](https://proceedings.mlr.press/v151/roelofs22a.html). Empirical binning bias.
- R8. Dimitriadis, Gneiting, Jordan & Vogel (2023 preprint), [Evaluating Probabilistic Classifiers: The Triptych](https://arxiv.org/abs/2301.10803). Murphy curves, reliability and discrimination.
- R9. Ferro (2007), [Comparing Probabilistic Forecasting Systems with the Brier Score](https://journals.ametsoc.org/view/journals/wefo/22/5/waf1034_1.xml). Paired comparison and block resampling.
- R10. Wilks (2010), [Sampling distributions of the Brier score and Brier skill score under serial dependence](https://rmets.onlinelibrary.wiley.com/doi/10.1002/qj.709). Dependence and uncertainty.
- R11. scikit-learn, [brier_score_loss documentation](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html), accessed 2026-09-12; labels and scale_by_half added in 1.7. Explicit class ordering/scaling; implementation comparison only, no new dependency.
- R12. Rossellini et al. (COLT 2025), [Can a calibration metric be both testable and actionable?](https://proceedings.mlr.press/v291/rossellini25a.html). Future cutoff-calibration diagnostic.
- R13. Hartline, Hu & Wu (COLT 2026), [A Perfectly Truthful Calibration Measure](https://proceedings.mlr.press/v336/hartline26a.html). Future ATB diagnostic; published version supersedes the 2025 preprint for this research inventory.
- R14. Gopalan et al. (March 2026 preprint), [The Importance of Being Smoothly Calibrated](https://arxiv.org/abs/2603.16015). Future smooth-calibration research, abstract-level review only.
- R15. Turtel et al., [How Proper Scoring Rules Shape LLM Forecasting](https://arxiv.org/abs/2608.28482v2) (August 28, 2026 preprint; revised September 9, 2026). Recent empirical lead, abstract-level review only; no transferable T0 training claim.

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

Provenance: scrimshawlife-ctrl/Trutina + constitution.md + specs/BIND.md (designated Spec 009/010 references; live parity unverified) + Research cutoff: 2026-09-12 + Hash: 2724c9baf6e5837441f65e569347c8e713a2a32e (observed repository baseline; not a Notion or document-content hash).
