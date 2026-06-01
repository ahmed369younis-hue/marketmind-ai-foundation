"""Pure feature computation utilities."""

from app.domain.data_contract import DailyMarketData
from app.domain.dataset_validation import validate_daily_dataset
from app.domain.feature_contract import DailyFeatures
from app.engine.normalization import min_max_normalize
from app.engine.time_series import moving_average, period_return, rolling_slope, rolling_std


def compute_range_compression(
    closes: list[float], window: int
) -> list[float | None]:
    """Compute range compression from normalized rolling standard deviation."""

    rolling_std_values = rolling_std(closes, window)
    valid_values = [value for value in rolling_std_values if value is not None]
    if not valid_values:
        return [None for _ in rolling_std_values]

    min_value = min(valid_values)
    max_value = max(valid_values)
    if min_value == max_value:
        return [None if value is None else 1.0 for value in rolling_std_values]

    results: list[float | None] = []
    for value in rolling_std_values:
        if value is None:
            results.append(None)
            continue

        normalized = min_max_normalize(value, min_value, max_value)
        range_compression = 1.0 - normalized
        results.append(float(min(max(range_compression, 0.0), 1.0)))

    return results


def compute_volume_trend(volumes: list[float], window: int) -> list[float | None]:
    """Compute volume trend from normalized rolling slope."""

    rolling_slope_values = rolling_slope(volumes, window)
    valid_values = [value for value in rolling_slope_values if value is not None]
    if not valid_values:
        return [None for _ in rolling_slope_values]

    min_value = min(valid_values)
    max_value = max(valid_values)
    if min_value == max_value:
        return [None if value is None else 0.5 for value in rolling_slope_values]

    results: list[float | None] = []
    for value in rolling_slope_values:
        if value is None:
            results.append(None)
            continue

        normalized = min_max_normalize(value, min_value, max_value)
        results.append(float(min(max(normalized, 0.0), 1.0)))

    return results


def compute_price_momentum(closes: list[float], periods: int) -> list[float | None]:
    """Compute price momentum from normalized period returns."""

    period_return_values = period_return(closes, periods)
    valid_values = [value for value in period_return_values if value is not None]
    if not valid_values:
        return [None for _ in period_return_values]

    min_value = min(valid_values)
    max_value = max(valid_values)
    if min_value == max_value:
        return [None if value is None else 0.5 for value in period_return_values]

    results: list[float | None] = []
    for value in period_return_values:
        if value is None:
            results.append(None)
            continue

        normalized = min_max_normalize(value, min_value, max_value)
        results.append(float(min(max(normalized, 0.0), 1.0)))

    return results


def compute_volume_spike(volumes: list[float], window: int) -> list[float | None]:
    """Compute volume spike as volume divided by moving average volume."""

    moving_average_values = moving_average(volumes, window)

    results: list[float | None] = []
    for volume, average in zip(volumes, moving_average_values):
        if average is None or volume is None:
            results.append(None)
            continue

        if average == 0:
            raise ValueError("moving average must not be zero")

        results.append(float(volume / average))

    return results


def compute_daily_features(
    data: list[DailyMarketData],
    range_window: int,
    volume_trend_window: int,
    momentum_periods: int,
    volume_spike_window: int,
) -> list[DailyFeatures]:
    """Aggregate complete computed features into DailyFeatures objects."""

    validate_daily_dataset(data)

    closes = [record.close for record in data]
    volumes = [record.volume for record in data]

    range_compression_values = compute_range_compression(closes, range_window)
    volume_trend_values = compute_volume_trend(volumes, volume_trend_window)
    price_momentum_values = compute_price_momentum(closes, momentum_periods)
    volume_spike_values = compute_volume_spike(volumes, volume_spike_window)

    daily_features: list[DailyFeatures] = []
    for record, range_compression, volume_trend, price_momentum, volume_spike in zip(
        data,
        range_compression_values,
        volume_trend_values,
        price_momentum_values,
        volume_spike_values,
    ):
        if any(
            value is None
            for value in (
                range_compression,
                volume_trend,
                price_momentum,
                volume_spike,
            )
        ):
            continue

        daily_features.append(
            DailyFeatures(
                date=record.date,
                symbol=record.symbol,
                range_compression=range_compression,
                volume_trend=volume_trend,
                price_momentum=price_momentum,
                volume_spike=volume_spike,
            )
        )

    return daily_features


def compute_liquidity_inflow(
    closes: list[float], volumes: list[float]
) -> list[float | None]:
    """Compute normalized liquidity inflow utility values."""

    if len(closes) != len(volumes):
        raise ValueError("closes and volumes must have the same length")

    if not closes:
        return []

    raw_values: list[float | None] = [None]
    for index in range(1, len(closes)):
        current_close = closes[index]
        previous_close = closes[index - 1]
        current_volume = volumes[index]
        previous_volume = volumes[index - 1]

        if (
            current_close is None
            or previous_close is None
            or current_volume is None
            or previous_volume is None
        ):
            raw_values.append(None)
            continue

        price_change = current_close - previous_close
        volume_change = current_volume - previous_volume
        if price_change > 0 and volume_change > 0:
            raw_values.append(float(current_volume * price_change))
        else:
            raw_values.append(0.0)

    valid_values = [value for value in raw_values if value is not None]
    if not valid_values:
        return [None for _ in raw_values]

    min_value = min(valid_values)
    max_value = max(valid_values)
    if min_value == max_value:
        return [None if value is None else 0.0 for value in raw_values]

    results: list[float | None] = []
    for value in raw_values:
        if value is None:
            results.append(None)
            continue

        normalized = min_max_normalize(value, min_value, max_value)
        results.append(float(min(max(normalized, 0.0), 1.0)))

    return results


def compute_liquidity_outflow(
    closes: list[float], volumes: list[float]
) -> list[float | None]:
    """Compute normalized liquidity outflow utility values."""

    if len(closes) != len(volumes):
        raise ValueError("closes and volumes must have the same length")

    if not closes:
        return []

    raw_values: list[float | None] = [None]
    for index in range(1, len(closes)):
        current_close = closes[index]
        previous_close = closes[index - 1]
        current_volume = volumes[index]
        previous_volume = volumes[index - 1]

        if (
            current_close is None
            or previous_close is None
            or current_volume is None
            or previous_volume is None
        ):
            raw_values.append(None)
            continue

        price_change = current_close - previous_close
        volume_change = current_volume - previous_volume
        if price_change < 0 and volume_change > 0:
            raw_values.append(float(current_volume * abs(price_change)))
        else:
            raw_values.append(0.0)

    valid_values = [value for value in raw_values if value is not None]
    if not valid_values:
        return [None for _ in raw_values]

    min_value = min(valid_values)
    max_value = max(valid_values)
    if min_value == max_value:
        return [None if value is None else 0.0 for value in raw_values]

    results: list[float | None] = []
    for value in raw_values:
        if value is None:
            results.append(None)
            continue

        normalized = min_max_normalize(value, min_value, max_value)
        results.append(float(min(max(normalized, 0.0), 1.0)))

    return results
