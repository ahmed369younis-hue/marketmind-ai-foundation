"""Pure time-series utilities."""


def rolling_std(values: list[float], window: int) -> list[float | None]:
    """Return population rolling standard deviation values."""

    if window <= 1:
        raise ValueError("window must be greater than 1")

    if not values:
        return []

    results: list[float | None] = []
    for index in range(len(values)):
        if index + 1 < window:
            results.append(None)
            continue

        window_values = values[index - window + 1 : index + 1]
        if any(value is None for value in window_values):
            results.append(None)
            continue

        mean = sum(window_values) / window
        variance = sum((value - mean) ** 2 for value in window_values) / window
        results.append(float(variance**0.5))

    return results


def rolling_slope(values: list[float], window: int) -> list[float | None]:
    """Return rolling simple linear regression slope values."""

    if window <= 1:
        raise ValueError("window must be greater than 1")

    if not values:
        return []

    mean_x = (window - 1) / 2.0
    denominator = sum((x - mean_x) ** 2 for x in range(window))

    results: list[float | None] = []
    for index in range(len(values)):
        if index + 1 < window:
            results.append(None)
            continue

        window_values = values[index - window + 1 : index + 1]
        if any(value is None for value in window_values):
            results.append(None)
            continue

        mean_y = sum(window_values) / window
        numerator = sum(
            (x - mean_x) * (value - mean_y)
            for x, value in enumerate(window_values)
        )
        results.append(float(numerator / denominator))

    return results


def moving_average(values: list[float], window: int) -> list[float | None]:
    """Return simple moving average values."""

    if window <= 0:
        raise ValueError("window must be greater than 0")

    if not values:
        return []

    results: list[float | None] = []
    for index in range(len(values)):
        if index + 1 < window:
            results.append(None)
            continue

        window_values = values[index - window + 1 : index + 1]
        if any(value is None for value in window_values):
            results.append(None)
            continue

        results.append(float(sum(window_values) / window))

    return results


def period_return(values: list[float], periods: int) -> list[float | None]:
    """Return period-over-period return values."""

    if periods <= 0:
        raise ValueError("periods must be greater than 0")

    if not values:
        return []

    results: list[float | None] = []
    for index in range(len(values)):
        if index < periods:
            results.append(None)
            continue

        current_value = values[index]
        previous_value = values[index - periods]
        if current_value is None or previous_value is None:
            results.append(None)
            continue

        if previous_value == 0:
            raise ValueError("previous value must not be zero")

        results.append(float((current_value - previous_value) / previous_value))

    return results
