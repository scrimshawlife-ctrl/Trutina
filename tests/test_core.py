import pytest
from brier.core import compute_atomic_brier, compute_series_brier

def test_compute_atomic_brier():
    # Perfect forecast
    assert compute_atomic_brier(1.0, 1) == 0.0
    assert compute_atomic_brier(0.0, 0) == 0.0
    # Worst forecast
    assert compute_atomic_brier(1.0, 0) == 1.0
    assert compute_atomic_brier(0.0, 1) == 1.0
    # Example from spec
    assert compute_atomic_brier(0.7, 1) == 0.09

def test_compute_atomic_brier_invalid():
    with pytest.raises(ValueError):
        compute_atomic_brier(1.5, 0)
    with pytest.raises(ValueError):
        compute_atomic_brier(-0.5, 0)
    with pytest.raises(ValueError):
        compute_atomic_brier(0.5, 2)

def test_compute_series_brier():
    scores = [0.0, 0.0, 1.0, 1.0]
    assert compute_series_brier(scores) == 0.5
    assert compute_series_brier([]) is None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
