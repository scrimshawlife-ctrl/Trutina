# brier

Brier scoring functions for the Abraxas model stack.

Provides telemetry-grade accuracy scoring (Brier score) for settled forecasts, 
integrated with Abraxas skill evolution and Hyperlex.

## Spec

See [`specs/000-brier-spine/spec.md`](specs/000-brier-spine/spec.md) for the full specification.

## Installation

```bash
pip install -e ".[dev]"
```

## Usage

```python
from brier import compute_atomic_brier

# Compute atomic Brier score
score = compute_atomic_brier(expected_probability=0.7, observed_outcome=1)
print(score)  # 0.09
```

## Development

Run tests:

```bash
pytest -q
```
