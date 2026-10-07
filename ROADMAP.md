# Roadmap — Trutina

Brier scoring functions for the Abraxas model stack. It measures calibration in forecasts it is
given — it does not produce forecasts.

Three words are used in one sense each, and they are not interchangeable:

- **shipped** — merged, and something runs it.
- **in progress** — being worked on now.
- **not planned** — deliberately not being built, with the reason given.

Anything that would require a claim this repository cannot evidence is listed as not planned rather than
deferred, because a roadmap that quietly carries an unmet promise is worse than a short one.

_Last reviewed: 2026-10-07._

## Shipped

- Brier scoring with honest uncertainty output.
- A count of ten tests over the scoring surface.
- **CI on every push** (3.10 / 3.11 / 3.12). The workflow was the prerequisite the badge column could not
  paper over; adding it immediately surfaced a drift nothing had caught (see below).

## In progress

- Nothing pending.

## Next

- **Reconcile `tests/test_score_contract.py` with the current spec.** It asserts the pre-2026-09-15 contract
  and fails against the current code (see KANBAN.md). The spec `specs/001-score/` documents the newer
  behaviour, so the test is the stale side -- but that call belongs to the author, not to a passer-by.
- Additional calibration metrics **only** where a consumer needs a specific one.

## Not planned

- **Inventing confidence.** Trutina scores what it is given; a default confidence would defeat its purpose.
