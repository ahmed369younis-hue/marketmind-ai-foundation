"""Pure normalization utilities."""


def min_max_normalize(value: float, min_value: float, max_value: float) -> float:
    """Normalize a value into [0,1] using min-max normalization."""

    if max_value <= min_value:
        raise ValueError("max_value must be greater than min_value")

    normalized = (value - min_value) / (max_value - min_value)
    return float(min(max(normalized, 0.0), 1.0))
