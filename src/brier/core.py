"""Core Brier computation logic."""

def compute_atomic_brier(expected_probability: float, observed_outcome: int) -> float:
    """
    Compute the Brier score for a single forecast.
    
    Args:
        expected_probability: Predicted probability of the event (0 to 1).
        observed_outcome: Actual outcome (0 or 1).
    
    Returns:
        Brier score: (expected_probability - observed_outcome)^2
    """
    if not 0 <= expected_probability <= 1:
        raise ValueError("expected_probability must be between 0 and 1")
    if observed_outcome not in (0, 1):
        raise ValueError("observed_outcome must be 0 or 1")
    
    return (expected_probability - observed_outcome) ** 2


def compute_series_brier(scores: list[float]) -> float | None:
    """
    Compute the mean Brier score for a series of forecasts.
    
    Args:
        scores: List of atomic Brier scores.
    
    Returns:
        Mean Brier score, or None if the list is empty.
    """
    if not scores:
        return None
    return sum(scores) / len(scores)


# Additional Brier skill scores can be added here (BSS, Murphy, Yates) if needed.
