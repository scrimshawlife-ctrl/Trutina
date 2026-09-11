# Data model — Trutina 000

## settled_forecast atom (input)

| field | type | rule |
|---|---|---|
| payload_class | const `settled_forecast` | required |
| p | number [0,1] | required |
| y | 0 or 1 | required |
| settlement | TRUE / FALSE | VOID refused |
| settled_by | string | required |
| settled_at | ISO-8601 or null | optional |
| corpus_ref | string | optional |

## brier.score.v0 (output)

| field | type | rule |
|---|---|---|
| schema | const `brier.score.v0` | required |
| specialist | const `abx.brier` | required |
| display | const `Trutina` | required |
| mode | SCORE / BATCH / DECOMPOSE / FUSION_ADVISORY / ROUTER_MICRO / GATE_ADVISORY / PROJECT | required |
| formula | const `BRIER_BINARY_V1` | SCORE |
| brier | number [0,1] or null | null on refuse |
| honesty | OBSERVED / INFERRED / SPECULATIVE / NOT_COMPUTABLE | required |
| forecast_eligible | false | frozen |
| can_promote | false | frozen |
| weight_mutation | false | frozen |
| ledger_id | string or null | null in SHADOW |
| failure | null / NOT_COMPUTABLE / SPECIALIST_LANE_VIOLATION / REJECT_OR_SHADOW | |
