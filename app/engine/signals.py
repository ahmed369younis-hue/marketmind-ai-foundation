"""Pure signal computation utilities."""

from app.domain.data_contract import DailyMarketData
from app.domain.dataset_validation import validate_daily_dataset
from app.domain.signal_contract import DailySignals
from app.domain.signal_parameters import SignalParameters
from app.engine.features import compute_liquidity_inflow, compute_liquidity_outflow
from app.engine.time_series import rolling_slope, rolling_std


def compute_accumulation_strength(
    data: list[DailyMarketData],
    parameters: SignalParameters,
) -> list[float | None]:
    """Compute binary accumulation strength from explicit parameter conditions."""

    validate_daily_dataset(data)

    window = parameters.rolling_window
    closes = [record.close for record in data]
    volumes = [record.volume for record in data]

    rolling_std_values = rolling_std(closes, window)
    rolling_slope_values = rolling_slope(volumes, window)

    results: list[float | None] = []
    for index, (std_value, slope_value) in enumerate(
        zip(rolling_std_values, rolling_slope_values)
    ):
        if std_value is None or slope_value is None:
            results.append(None)
            continue

        window_closes = closes[index - window + 1 : index + 1]
        condition_std = std_value < parameters.threshold_std
        condition_volume = slope_value > 0
        condition_support = min(window_closes) >= parameters.support_level

        if condition_std and condition_volume and condition_support:
            results.append(1.0)
        else:
            results.append(0.0)

    return results


def compute_distribution_strength(
    data: list[DailyMarketData],
    parameters: SignalParameters,
) -> list[float | None]:
    """Compute binary distribution strength from explicit parameter conditions."""

    validate_daily_dataset(data)

    window = parameters.rolling_window
    closes = [record.close for record in data]
    volumes = [record.volume for record in data]

    rolling_std_values = rolling_std(closes, window)
    rolling_slope_values = rolling_slope(volumes, window)

    results: list[float | None] = []
    for index, (std_value, slope_value) in enumerate(
        zip(rolling_std_values, rolling_slope_values)
    ):
        if std_value is None or slope_value is None:
            results.append(None)
            continue

        window_closes = closes[index - window + 1 : index + 1]
        condition_std = std_value < parameters.threshold_std
        condition_volume = slope_value > 0
        condition_failed_breakout = max(window_closes) < parameters.breakout_level

        if condition_std and condition_volume and condition_failed_breakout:
            results.append(1.0)
        else:
            results.append(0.0)

    return results


def compute_absorption_score(
    data: list[DailyMarketData],
    parameters: SignalParameters,
) -> list[float | None]:
    """Compute binary absorption score from explicit parameter conditions."""

    validate_daily_dataset(data)

    results: list[float | None] = [None]
    for index in range(1, len(data)):
        previous_close = data[index - 1].close
        current_close = data[index].close
        current_volume = data[index].volume

        price_movement = abs(current_close - previous_close) / previous_close
        condition_high_volume = current_volume >= parameters.high_volume_threshold
        condition_low_movement = (
            price_movement <= parameters.low_price_movement_threshold
        )

        if condition_high_volume and condition_low_movement:
            results.append(1.0)
        else:
            results.append(0.0)

    return results


def compute_fake_move_score(
    data: list[DailyMarketData],
    parameters: SignalParameters,
) -> list[float | None]:
    """Compute binary fake move score from explicit parameter conditions."""

    validate_daily_dataset(data)

    reversal_candles = parameters.reversal_candles
    results: list[float | None] = []
    for index, record in enumerate(data):
        breakout = record.close > parameters.breakout_level
        low_volume = record.volume <= parameters.low_volume_threshold

        if not breakout:
            results.append(0.0)
            continue

        if low_volume:
            results.append(1.0)
            continue

        future_window = data[index + 1 : index + 1 + reversal_candles]
        if len(future_window) < reversal_candles:
            results.append(None)
            continue

        reversal = any(
            future.close <= parameters.breakout_level for future in future_window
        )
        if reversal:
            results.append(1.0)
        else:
            results.append(0.0)

    return results


def compute_daily_signals(
    data: list[DailyMarketData],
    parameters: SignalParameters,
) -> list[DailySignals]:
    """Aggregate complete computed signal values into DailySignals objects."""

    validate_daily_dataset(data)

    closes = [record.close for record in data]
    volumes = [record.volume for record in data]

    accumulation_strength_values = compute_accumulation_strength(data, parameters)
    distribution_strength_values = compute_distribution_strength(data, parameters)
    liquidity_inflow_values = compute_liquidity_inflow(closes, volumes)
    liquidity_outflow_values = compute_liquidity_outflow(closes, volumes)
    absorption_score_values = compute_absorption_score(data, parameters)
    fake_move_score_values = compute_fake_move_score(data, parameters)

    daily_signals: list[DailySignals] = []
    for (
        record,
        accumulation_strength,
        distribution_strength,
        liquidity_inflow,
        liquidity_outflow,
        absorption_score,
        fake_move_score,
    ) in zip(
        data,
        accumulation_strength_values,
        distribution_strength_values,
        liquidity_inflow_values,
        liquidity_outflow_values,
        absorption_score_values,
        fake_move_score_values,
    ):
        if any(
            value is None
            for value in (
                accumulation_strength,
                distribution_strength,
                liquidity_inflow,
                liquidity_outflow,
                absorption_score,
                fake_move_score,
            )
        ):
            continue

        daily_signals.append(
            DailySignals(
                date=record.date,
                symbol=record.symbol,
                accumulation_strength=accumulation_strength,
                distribution_strength=distribution_strength,
                liquidity_inflow=liquidity_inflow,
                liquidity_outflow=liquidity_outflow,
                absorption_score=absorption_score,
                fake_move_score=fake_move_score,
            )
        )

    return daily_signals
