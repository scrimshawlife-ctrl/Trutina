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

## In progress

- Nothing pending.

## Next

- Additional calibration metrics **only** where a consumer needs a specific one.

## Not planned

- **A CI badge.** This repository has no workflow, so a build badge would be decorative. Adding the workflow
  comes first.
- **Inventing confidence.** Trutina scores what it is given; a default confidence would defeat its purpose.
