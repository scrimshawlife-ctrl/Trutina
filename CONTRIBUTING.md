# Contributing

## The rules that matter here

- **This library scores forecasts; it does not make them.** Adding a default confidence would defeat the
  purpose of a calibration library.
- **Never invent a confidence.** Every number returned traces to an input that was given.
- **A metric is added when a consumer needs that metric**, not because it is standard elsewhere.
