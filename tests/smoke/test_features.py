from datetime import date, timedelta

import pytest

from app.domain.data_contract import DailyMarketData
from app.domain.feature_contract import DailyFeatures
from app.domain.signal_contract import DailySignals
from app.engine.features import (
    compute_daily_features,
    compute_liquidity_inflow,
    compute_liquidity_outflow,
    compute_price_momentum,
    compute_range_compression,
    compute_volume_spike,
    compute_volume_trend,
)


def _daily_record(day_offset: int, close: float, volume: float, symbol: str = "MM") -> DailyMarketData:
    return DailyMarketData(
        date=date(2024, 1, 1) + timedelta(days=day_offset),
        open=close,
        high=close + 1.0,
        low=close - 1.0,
        close=close,
        volume=volume,
        symbol=symbol,
    )


def _valid_dataset() -> list[DailyMarketData]:
    return [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 11.0, 120.0),
        _daily_record(2, 13.0, 150.0),
        _daily_record(3, 16.0, 190.0),
    ]


def test_range_compression_insufficient_rolling_window_returns_none_values() -> None:
    assert compute_range_compression([1.0, 2.0], 3) == [None, None]


def test_range_compression_constant_closes_return_one_after_enough_history() -> None:
    assert compute_range_compression([1.0, 1.0, 1.0, 1.0], 3) == [
        None,
        None,
        1.0,
        1.0,
    ]


def test_range_compression_varied_closes_outputs_stay_within_unit_range() -> None:
    result = compute_range_compression([1.0, 2.0, 4.0, 8.0, 16.0], 3)
    valid_values = [value for value in result if value is not None]

    assert valid_values
    assert all(0.0 <= value <= 1.0 for value in valid_values)


def test_range_compression_none_in_rolling_window_outputs_none() -> None:
    result = compute_range_compression([1.0, None, 3.0, 4.0, 5.0], 3)

    assert result == [None, None, None, None, 1.0]


def test_range_compression_input_list_is_not_mutated() -> None:
    closes = [1.0, 2.0, 4.0]
    original_closes = closes.copy()

    compute_range_compression(closes, 3)

    assert closes == original_closes


def test_range_compression_window_less_than_or_equal_to_one_raises_error() -> None:
    with pytest.raises(ValueError, match="window must be greater than 1"):
        compute_range_compression([1.0, 2.0, 3.0], 1)


def test_range_compression_does_not_return_daily_features_objects() -> None:
    result = compute_range_compression([1.0, 2.0, 4.0], 3)

    assert not any(isinstance(value, DailyFeatures) for value in result)


def test_volume_trend_insufficient_rolling_window_returns_none_values() -> None:
    assert compute_volume_trend([1.0, 2.0], 3) == [None, None]


def test_volume_trend_equal_slopes_return_half_for_valid_positions() -> None:
    assert compute_volume_trend([1.0, 2.0, 3.0, 4.0], 3) == [
        None,
        None,
        0.5,
        0.5,
    ]


def test_volume_trend_increasing_slope_sequence_outputs_stay_within_unit_range() -> None:
    result = compute_volume_trend([1.0, 2.0, 4.0, 7.0, 11.0], 3)
    valid_values = [value for value in result if value is not None]

    assert valid_values
    assert all(0.0 <= value <= 1.0 for value in valid_values)


def test_volume_trend_none_in_rolling_window_outputs_none() -> None:
    result = compute_volume_trend([1.0, None, 3.0, 4.0, 5.0], 3)

    assert result == [None, None, None, None, 0.5]


def test_volume_trend_input_list_is_not_mutated() -> None:
    volumes = [1.0, 2.0, 4.0]
    original_volumes = volumes.copy()

    compute_volume_trend(volumes, 3)

    assert volumes == original_volumes


def test_volume_trend_window_less_than_or_equal_to_one_raises_error() -> None:
    with pytest.raises(ValueError, match="window must be greater than 1"):
        compute_volume_trend([1.0, 2.0, 3.0], 1)


def test_volume_trend_does_not_return_daily_features_objects() -> None:
    result = compute_volume_trend([1.0, 2.0, 4.0], 3)

    assert not any(isinstance(value, DailyFeatures) for value in result)


def test_price_momentum_insufficient_period_history_returns_none_values() -> None:
    assert compute_price_momentum([10.0], 1) == [None]


def test_price_momentum_equal_returns_return_half_for_valid_positions() -> None:
    assert compute_price_momentum([1.0, 2.0, 4.0, 8.0], 1) == [
        None,
        0.5,
        0.5,
        0.5,
    ]


def test_price_momentum_varied_returns_outputs_stay_within_unit_range() -> None:
    result = compute_price_momentum([10.0, 11.0, 13.0, 18.0], 1)
    valid_values = [value for value in result if value is not None]

    assert valid_values
    assert all(0.0 <= value <= 1.0 for value in valid_values)


def test_price_momentum_none_current_or_previous_values_output_none() -> None:
    assert compute_price_momentum([10.0, None, 12.0], 1) == [None, None, None]


def test_price_momentum_input_list_is_not_mutated() -> None:
    closes = [10.0, 11.0]
    original_closes = closes.copy()

    compute_price_momentum(closes, 1)

    assert closes == original_closes


def test_price_momentum_periods_less_than_or_equal_to_zero_raises_error() -> None:
    with pytest.raises(ValueError, match="periods must be greater than 0"):
        compute_price_momentum([10.0, 11.0], 0)


def test_price_momentum_previous_zero_value_raises_error() -> None:
    with pytest.raises(ValueError, match="previous value must not be zero"):
        compute_price_momentum([0.0, 1.0], 1)


def test_price_momentum_does_not_return_daily_features_objects() -> None:
    result = compute_price_momentum([10.0, 11.0], 1)

    assert not any(isinstance(value, DailyFeatures) for value in result)


def test_volume_spike_insufficient_moving_average_window_returns_none_values() -> None:
    assert compute_volume_spike([10.0], 2) == [None]


def test_volume_spike_known_values_are_correct() -> None:
    result = compute_volume_spike([2.0, 4.0, 8.0], 2)

    assert result == [None, pytest.approx(4.0 / 3.0), pytest.approx(8.0 / 6.0)]


def test_volume_spike_current_volume_none_returns_none() -> None:
    assert compute_volume_spike([2.0, None], 1) == [1.0, None]


def test_volume_spike_moving_average_window_containing_none_returns_none() -> None:
    result = compute_volume_spike([2.0, None, 6.0, 8.0], 2)

    assert result == [None, None, None, pytest.approx(8.0 / 7.0)]


def test_volume_spike_moving_average_zero_raises_error() -> None:
    with pytest.raises(ValueError, match="moving average must not be zero"):
        compute_volume_spike([0.0, 0.0], 2)


def test_volume_spike_input_list_is_not_mutated() -> None:
    volumes = [2.0, 4.0]
    original_volumes = volumes.copy()

    compute_volume_spike(volumes, 2)

    assert volumes == original_volumes


def test_volume_spike_window_less_than_or_equal_to_zero_raises_error() -> None:
    for invalid_window in (0, -1):
        with pytest.raises(ValueError, match="window must be greater than 0"):
            compute_volume_spike([2.0, 4.0], invalid_window)


def test_volume_spike_does_not_return_daily_features_objects() -> None:
    result = compute_volume_spike([2.0, 4.0], 2)

    assert not any(isinstance(value, DailyFeatures) for value in result)


def test_daily_features_valid_dataset_returns_daily_features_objects() -> None:
    result = compute_daily_features(_valid_dataset(), 2, 2, 1, 2)

    assert result
    assert all(isinstance(feature, DailyFeatures) for feature in result)


def test_daily_features_output_preserves_date_and_symbol() -> None:
    data = _valid_dataset()
    result = compute_daily_features(data, 2, 2, 1, 2)

    assert result[0].date == data[1].date
    assert result[0].symbol == data[1].symbol


def test_daily_features_incomplete_early_rows_are_skipped() -> None:
    data = _valid_dataset()
    result = compute_daily_features(data, 3, 3, 2, 3)

    assert [feature.date for feature in result] == [data[2].date, data[3].date]


def test_daily_features_invalid_dataset_raises_value_error() -> None:
    data = [_daily_record(0, 10.0, 100.0), _daily_record(2, 12.0, 120.0)]

    with pytest.raises(ValueError, match="dataset must not skip dates"):
        compute_daily_features(data, 2, 2, 1, 2)


def test_daily_features_no_complete_rows_returns_empty_list() -> None:
    assert compute_daily_features(_valid_dataset(), 5, 5, 5, 5) == []


def test_daily_features_input_data_list_is_not_mutated() -> None:
    data = _valid_dataset()
    original_data = data.copy()

    compute_daily_features(data, 2, 2, 1, 2)

    assert data == original_data


def test_daily_features_does_not_return_raw_dicts() -> None:
    result = compute_daily_features(_valid_dataset(), 2, 2, 1, 2)

    assert not any(isinstance(feature, dict) for feature in result)


def test_daily_features_does_not_compute_signals_or_scores() -> None:
    result = compute_daily_features(_valid_dataset(), 2, 2, 1, 2)

    assert result
    assert not any(hasattr(feature, "accumulation_strength") for feature in result)
    assert not any(hasattr(feature, "smart_money_score") for feature in result)


def test_liquidity_flow_length_mismatch_raises_value_error() -> None:
    for compute_liquidity in (compute_liquidity_inflow, compute_liquidity_outflow):
        with pytest.raises(ValueError, match="closes and volumes must have the same length"):
            compute_liquidity([10.0, 11.0], [100.0])


def test_liquidity_flow_empty_inputs_return_empty_lists() -> None:
    assert compute_liquidity_inflow([], []) == []
    assert compute_liquidity_outflow([], []) == []


def test_liquidity_flow_first_position_returns_none() -> None:
    assert compute_liquidity_inflow([10.0, 11.0], [100.0, 110.0])[0] is None
    assert compute_liquidity_outflow([10.0, 9.0], [100.0, 110.0])[0] is None


def test_liquidity_inflow_triggers_only_when_price_and_volume_increase() -> None:
    result = compute_liquidity_inflow(
        [10.0, 11.0, 12.0, 11.0, 13.0],
        [100.0, 110.0, 105.0, 120.0, 130.0],
    )

    assert result == [None, pytest.approx(110.0 / 260.0), 0.0, 0.0, 1.0]


def test_liquidity_outflow_triggers_only_when_price_decreases_and_volume_increases() -> None:
    result = compute_liquidity_outflow(
        [10.0, 9.0, 8.0, 9.0, 7.0],
        [100.0, 110.0, 105.0, 120.0, 130.0],
    )

    assert result == [None, pytest.approx(110.0 / 260.0), 0.0, 0.0, 1.0]


def test_liquidity_flow_non_trigger_positions_normalize_to_zero_when_valid() -> None:
    closes = [10.0, 9.0, 8.0]
    volumes = [100.0, 90.0, 80.0]

    assert compute_liquidity_inflow(closes, volumes) == [None, 0.0, 0.0]
    assert compute_liquidity_outflow(closes, volumes) == [None, 0.0, 0.0]


def test_liquidity_flow_none_current_or_previous_values_return_none() -> None:
    closes = [10.0, None, 11.0, 12.0, 13.0]
    volumes = [100.0, 110.0, 120.0, None, 140.0]

    assert compute_liquidity_inflow(closes, volumes) == [None, None, None, None, None]
    assert compute_liquidity_outflow(closes, volumes) == [None, None, None, None, None]


def test_liquidity_flow_outputs_stay_within_unit_range() -> None:
    closes = [10.0, 11.0, 9.0, 12.0]
    volumes = [100.0, 120.0, 140.0, 160.0]

    for result in (
        compute_liquidity_inflow(closes, volumes),
        compute_liquidity_outflow(closes, volumes),
    ):
        valid_values = [value for value in result if value is not None]
        assert valid_values
        assert all(0.0 <= value <= 1.0 for value in valid_values)


def test_liquidity_flow_input_lists_are_not_mutated() -> None:
    closes = [10.0, 11.0, 9.0]
    volumes = [100.0, 120.0, 140.0]
    original_closes = closes.copy()
    original_volumes = volumes.copy()

    compute_liquidity_inflow(closes, volumes)
    compute_liquidity_outflow(closes, volumes)

    assert closes == original_closes
    assert volumes == original_volumes


def test_liquidity_flow_functions_do_not_return_daily_signals_objects() -> None:
    closes = [10.0, 11.0, 9.0]
    volumes = [100.0, 120.0, 140.0]

    for result in (
        compute_liquidity_inflow(closes, volumes),
        compute_liquidity_outflow(closes, volumes),
    ):
        assert not any(isinstance(value, DailySignals) for value in result)
