# Model card — Trutina T0

| Field | Value |
|---|---|
| Name | Trutina |
| Artifact | `trutina-score-t0` (formula, not weights) |
| Task | Score settled (p, y) with `BRIER_BINARY_V1` |
| Input | `settled_forecast` atom (`p` in [0,1], `y` in {0,1}, settlement receipt) |
| Output | `brier.score.v0` |
| Forecast | never |
| Promotion | never |
| Phenomenal | never |
| Weight mutation | never |
| Training data | none at T0 |
| Eval | `tests/test_core.py` plus SCORE fixtures when opened |
| Intended use | Abraxas calibration specialist |
| Out of scope | chat, mind claims, unsettled forecast_request, Hyperlex/Athanor numeric Brier, ledger finalization |
