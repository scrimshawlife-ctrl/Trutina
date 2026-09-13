# Spec 001 — SCORE

Mode: SCORE
Cycle: existing SCORE; proposed validation completion, SHADOW
Formula: `BRIER_BINARY_V1` = (p − y)²

## Accept

`payload_class = settled_forecast` with p in [0,1], y in {0,1}, settlement TRUE or FALSE, settled_by present.

## BOUNDARY

This is the atomic implementation contract within the [Trutina Brier specification](../000-trutina-spine/spec.md). This does not govern or activate. The output schema and live-mode set remain unchanged. Assumption: upstream supplies an immutable forecast and an operator settlement, with external authenticity assessed by its owner.

## EVIDENCE PACKET

OBSERVED at `2724c9baf6e5837441f65e569347c8e713a2a32e`: `src/brier/score.py` emits `brier.score.v0`, but accepts omitted payload/settlement and coercible numbers. It does not enforce settlement/outcome agreement. These observed behaviors are implementation gaps relative to the stricter proposed contract. Existing tests use exact decimal equality in places; expected arithmetic below uses numeric tolerances.

## TASK

Journey → Workflow → State Transition → Contract → Acceptance Test → Implementation Task:

Review settled claim → validate type, lane and settlement → eligible/scored or refused → the rules below → A01–A09 in the spine → T01, strict SCORE validation. No batch execution is introduced.

## OUTPUT EXPECTED

### Input record

The canonical input is a JSON object. The following table is an INFERRED semantic schema to implement at the wrapper; it is not a new registered schema artifact.

| Field | Type | Required behavior |
|---|---|---|
| `payload_class` | string | Required, exactly `settled_forecast` for computation |
| `mode` | string | Optional; absence defaults to SCORE; present null/empty/non-string is invalid |
| `p` | finite JSON number | Required unless valid alias supplied; 0<=p<=1; booleans and strings rejected |
| `y` | finite JSON number | Required unless valid alias supplied; exactly 0 or 1; 0.0/1.0 valid, fractional values, booleans and strings rejected |
| `settlement` | string | Required TRUE iff y=1, FALSE iff y=0; VOID never numeric |
| `settled_by` | string | Required; nonempty after whitespace check; preserve original value outside the packet |
| `settled_at` | string or null | Optional offset-qualified ISO-8601 timestamp; malformed supplied value refused; never generated locally |
| `corpus_ref` | string or null | Optional; nonempty if string; malformed value refused and never echoed into output |
| `expected_probability`, `observed_outcome` | same types as p/y | Existing compatibility aliases; accepted only when canonical field absent or equal after strict validation |

Unknown metadata keys are ignored for scoring and never echoed. Validate both canonical and alias values when both are supplied; conflict is NOT_COMPUTABLE. Do not fallback from invalid canonical fields to an alias. No int/float parsing of strings or rounding of y. Non-object input is refused without an exception escaping the public wrapper. The pure numeric kernel may raise ValueError for invalid domain inputs; the wrapper maps invalid input to a packet.

Validation order is deterministic: validate top-level object; validate mode (unsupported/stub yields NOT_COMPUTABLE); classify payload (forecast_request yields NOT_COMPUTABLE, other explicit non-settled class yields SPECIALIST_LANE_VIOLATION, missing/non-string yields NOT_COMPUTABLE); validate settlement/receipt fields, aliases and numeric domains; verify outcome agreement; compute. Sanitize corpus_ref independently so every refusal packet remains schema-valid. Invalid/unknown mode is represented as SCORE in the refusal packet; recognized stubs retain their own mode, matching current output behavior.

### Output record and conditional invariants

The existing [closed JSON Schema](../../contracts/brier.score.v0.schema.json) defines allowed fields. Emit the full current wrapper shape on both success and refusal: `schema`, `specialist`, `display`, `mode`, `formula`, `brier`, `honesty`, `forecast_eligible`, `can_promote`, `weight_mutation`, `phenomenal`, `ledger_id`, `failure`, `corpus_ref`. These semantic requirements are stronger than the schema's structural required list and must be checked in tests.

On success: schema `brier.score.v0`, specialist `abx.brier`, display `Trutina`, mode SCORE, formula `BRIER_BINARY_V1`, finite brier in [0,1], honesty OBSERVED, failure null. On refusal: brier null, honesty NOT_COMPUTABLE, failure NOT_COMPUTABLE or SPECIALIST_LANE_VIOLATION. In every case forecast_eligible, can_promote, weight_mutation and phenomenal are false; ledger_id is null. JSON must contain no NaN/Infinity. OBSERVED means arithmetic on the supplied settled pair, not independent authentication of its provenance.

Illustrative success packet (numeric brier is compared with tolerance; serialization may expose binary64 representation):

```json
{
  "schema": "brier.score.v0",
  "specialist": "abx.brier",
  "display": "Trutina",
  "mode": "SCORE",
  "formula": "BRIER_BINARY_V1",
  "brier": 0.04,
  "honesty": "OBSERVED",
  "forecast_eligible": false,
  "can_promote": false,
  "weight_mutation": false,
  "phenomenal": false,
  "ledger_id": null,
  "failure": null,
  "corpus_ref": null
}
```

## Refuse

| input | failure |
|---|---|
| forecast_request | NOT_COMPUTABLE (R004) |
| VOID | NOT_COMPUTABLE |
| slang_atom, tradition_atom, sign_atom, route_atom | SPECIALIST_LANE_VIOLATION |
| p outside [0,1] | NOT_COMPUTABLE |
| y not in {0,1} | NOT_COMPUTABLE |
| missing settled_by | NOT_COMPUTABLE |
| missing payload_class or settlement | NOT_COMPUTABLE |
| TRUE with y=0, FALSE with y=1 | NOT_COMPUTABLE |
| fractional y, strings/booleans as p/y, NaN/infinity | NOT_COMPUTABLE |
| conflicting aliases or invalid supplied metadata | NOT_COMPUTABLE |

Failure reasons more specific than existing failure strings may be logged by the caller as diagnostics; no new fields are added to v0. Invalid input must not be logged verbatim. No scoring refusal changes upstream settlement state.

## Fixtures (from Spec 010 E-B0)

- compute(0.8, 1.0) = 0.04
- compute(0.8, 0.0) = 0.64
- GATE_ADVISORY promotion stays false
- SHADOW computes score, ledger_id stays null

## Later modes (not this cycle)

BATCH mean over settled members.
DECOMPOSE follows the spine's exact/binned identity, including within-bin correction where needed.
FUSION_ADVISORY inverse-Brier mix remains a speculative heuristic with unresolved zero-loss/correlation handling.
ROUTER_MICRO (predicted_quality − observed_quality)² requires a separate target definition if non-binary.
GATE_ADVISORY informs review, cannot promote.
PROJECT AAL-Viz only.

## VALIDATION

Acceptance is A01–A09 plus A24 in the spine. Check successful and refused packets against the unchanged output schema and semantic invariants; check malformed input, aliases, endpoint behavior, input immutability and deterministic repetition. Use `abs_tol=1e-12`, `rel_tol=1e-12` for decimal expectations. No runtime repair or pass claim is made by this documentation change.

## RESIDUAL RISKS

NOT_COMPUTABLE: external receipt authenticity and live Notion parity. Current wrapper gaps are OBSERVED, pending T01. Missing timestamp remains permitted by the existing data model and cannot establish issuance/settlement chronology on its own.

## RECOMMENDED NEXT ADVISORY ACTION

Implement T01 against these fixtures in the existing SCORE cycle, without opening new modes or changing packet schema.

Provenance: Notion Sprint 001 Hub (live alignment NOT_COMPUTABLE) + Loop 805 Slice NOT_COMPUTABLE + Hash: 2724c9baf6e5837441f65e569347c8e713a2a32e (observed repository baseline).
