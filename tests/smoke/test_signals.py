from datetime import date, timedelta

import pytest

from app.domain.data_contract import DailyMarketData
from app.domain.signal_contract import DailySignals
from app.domain.signal_parameters import SignalParameters
from app.engine.signals import (
    compute_accumulation_strength,
    compute_absorption_score,
    compute_daily_signals,
    compute_distribution_strength,
    compute_fake_move_score,
)


def _daily_record(
    day_offset: int,
    close: float,
    volume: float,
    symbol: str = "MM",
) -> DailyMarketData:
    return DailyMarketData(
        date=date(2024, 1, 1) + timedelta(days=day_offset),
        open=close,
        high=close + 1.0,
        low=close - 1.0,
        close=close,
        volume=volume,
        symbol=symbol,
    )


def _signal_parameters(**overrides: object) -> SignalParameters:
    values: dict[str, object] = {
        "rolling_window": 3,
        "threshold_std": 0.2,
        "support_level": 9.5,
        "breakout_level": 12.0,
        "high_volume_threshold": 200.0,
        "low_volume_threshold": 50.0,
        "low_price_movement_threshold": 0.1,
        "reversal_candles": 2,
    }
    values.update(overrides)
    return SignalParameters(**values)


def test_accumulation_true_conditions_return_one_for_valid_positions() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.1, 110.0),
        _daily_record(2, 10.2, 120.0),
        _daily_record(3, 10.3, 130.0),
    ]

    assert compute_accumulation_strength(data, _signal_parameters()) == [
        None,
        None,
        1.0,
        1.0,
    ]


def test_accumulation_high_rolling_std_returns_zero() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 12.0, 110.0),
        _daily_record(2, 20.0, 120.0),
    ]

    assert compute_accumulation_strength(data, _signal_parameters()) == [
        None,
        None,
        0.0,
    ]


def test_accumulation_non_positive_volume_slope_returns_zero() -> None:
    data = [
        _daily_record(0, 10.0, 120.0),
        _daily_record(1, 10.1, 120.0),
        _daily_record(2, 10.2, 120.0),
    ]

    assert compute_accumulation_strength(data, _signal_parameters()) == [
        None,
        None,
        0.0,
    ]


def test_accumulation_close_below_support_level_returns_zero() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.1, 110.0),
        _daily_record(2, 10.2, 120.0),
    ]

    result = compute_accumulation_strength(
        data,
        _signal_parameters(support_level=10.15),
    )

    assert result == [None, None, 0.0]


def test_accumulation_insufficient_window_positions_return_none() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.1, 110.0),
    ]

    assert compute_accumulation_strength(data, _signal_parameters()) == [None, None]


def test_accumulation_invalid_dataset_raises_value_error() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(2, 10.1, 110.0),
        _daily_record(3, 10.2, 120.0),
    ]

    with pytest.raises(ValueError, match="dataset must not skip dates"):
        compute_accumulation_strength(data, _signal_parameters())


def test_accumulation_invalid_signal_parameters_raise_value_error() -> None:
    with pytest.raises(ValueError, match="rolling_window must be > 1"):
        _signal_parameters(rolling_window=1)


def test_accumulation_input_data_list_is_not_mutated() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.1, 110.0),
        _daily_record(2, 10.2, 120.0),
    ]
    original_data = data.copy()

    compute_accumulation_strength(data, _signal_parameters())

    assert data == original_data


def test_accumulation_does_not_return_daily_signals_objects() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.1, 110.0),
        _daily_record(2, 10.2, 120.0),
    ]

    result = compute_accumulation_strength(data, _signal_parameters())

    assert not any(isinstance(value, DailySignals) for value in result)


def test_accumulation_outputs_stay_within_unit_range() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.1, 110.0),
        _daily_record(2, 10.2, 120.0),
        _daily_record(3, 14.0, 90.0),
    ]

    result = compute_accumulation_strength(data, _signal_parameters())
    valid_values = [value for value in result if value is not None]

    assert valid_values
    assert all(0.0 <= value <= 1.0 for value in valid_values)


def test_distribution_true_conditions_return_one_for_valid_positions() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.1, 110.0),
        _daily_record(2, 10.2, 120.0),
        _daily_record(3, 10.3, 130.0),
    ]

    assert compute_distribution_strength(data, _signal_parameters()) == [
        None,
        None,
        1.0,
        1.0,
    ]


def test_distribution_high_rolling_std_returns_zero() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 12.0, 110.0),
        _daily_record(2, 20.0, 120.0),
    ]

    assert compute_distribution_strength(data, _signal_parameters()) == [
        None,
        None,
        0.0,
    ]


def test_distribution_non_positive_volume_slope_returns_zero() -> None:
    data = [
        _daily_record(0, 10.0, 120.0),
        _daily_record(1, 10.1, 120.0),
        _daily_record(2, 10.2, 120.0),
    ]

    assert compute_distribution_strength(data, _signal_parameters()) == [
        None,
        None,
        0.0,
    ]


def test_distribution_price_reaches_breakout_level_returns_zero() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.1, 110.0),
        _daily_record(2, 12.0, 120.0),
    ]

    result = compute_distribution_strength(
        data,
        _signal_parameters(threshold_std=5.0, breakout_level=12.0),
    )

    assert result == [None, None, 0.0]


def test_distribution_insufficient_window_positions_return_none() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.1, 110.0),
    ]

    assert compute_distribution_strength(data, _signal_parameters()) == [None, None]


def test_distribution_invalid_dataset_raises_value_error() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(2, 10.1, 110.0),
        _daily_record(3, 10.2, 120.0),
    ]

    with pytest.raises(ValueError, match="dataset must not skip dates"):
        compute_distribution_strength(data, _signal_parameters())


def test_distribution_invalid_signal_parameters_raise_value_error() -> None:
    with pytest.raises(ValueError, match="breakout_level must be > 0"):
        _signal_parameters(breakout_level=0.0)


def test_distribution_input_data_list_is_not_mutated() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.1, 110.0),
        _daily_record(2, 10.2, 120.0),
    ]
    original_data = data.copy()

    compute_distribution_strength(data, _signal_parameters())

    assert data == original_data


def test_distribution_does_not_return_daily_signals_objects() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.1, 110.0),
        _daily_record(2, 10.2, 120.0),
    ]

    result = compute_distribution_strength(data, _signal_parameters())

    assert not any(isinstance(value, DailySignals) for value in result)


def test_distribution_outputs_stay_within_unit_range() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.1, 110.0),
        _daily_record(2, 10.2, 120.0),
        _daily_record(3, 14.0, 90.0),
    ]

    result = compute_distribution_strength(data, _signal_parameters())
    valid_values = [value for value in result if value is not None]

    assert valid_values
    assert all(0.0 <= value <= 1.0 for value in valid_values)


def test_absorption_true_conditions_return_one_for_valid_rows() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.5, 200.0),
        _daily_record(2, 11.0, 250.0),
    ]

    assert compute_absorption_score(data, _signal_parameters()) == [
        None,
        1.0,
        1.0,
    ]


def test_absorption_first_position_returns_none() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.5, 200.0),
    ]

    assert compute_absorption_score(data, _signal_parameters())[0] is None


def test_absorption_high_volume_with_price_movement_above_threshold_returns_zero() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 12.0, 200.0),
    ]

    assert compute_absorption_score(data, _signal_parameters()) == [None, 0.0]


def test_absorption_low_movement_with_volume_below_threshold_returns_zero() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.5, 199.0),
    ]

    assert compute_absorption_score(data, _signal_parameters()) == [None, 0.0]


def test_absorption_both_conditions_false_returns_zero() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 12.0, 199.0),
    ]

    assert compute_absorption_score(data, _signal_parameters()) == [None, 0.0]


def test_absorption_invalid_dataset_raises_value_error() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(2, 10.5, 200.0),
    ]

    with pytest.raises(ValueError, match="dataset must not skip dates"):
        compute_absorption_score(data, _signal_parameters())


def test_absorption_invalid_signal_parameters_raise_value_error() -> None:
    with pytest.raises(ValueError, match="low_price_movement_threshold must be >= 0"):
        _signal_parameters(low_price_movement_threshold=-0.1)


def test_absorption_input_data_list_is_not_mutated() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.5, 200.0),
    ]
    original_data = data.copy()

    compute_absorption_score(data, _signal_parameters())

    assert data == original_data


def test_absorption_does_not_return_daily_signals_objects() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.5, 200.0),
    ]

    result = compute_absorption_score(data, _signal_parameters())

    assert not any(isinstance(value, DailySignals) for value in result)


def test_absorption_outputs_stay_within_unit_range() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.5, 200.0),
        _daily_record(2, 12.0, 199.0),
    ]

    result = compute_absorption_score(data, _signal_parameters())
    valid_values = [value for value in result if value is not None]

    assert valid_values
    assert all(0.0 <= value <= 1.0 for value in valid_values)


def test_fake_move_non_breakout_row_returns_zero() -> None:
    data = [_daily_record(0, 11.0, 100.0)]

    assert compute_fake_move_score(data, _signal_parameters()) == [0.0]


def test_fake_move_breakout_with_low_volume_returns_one() -> None:
    data = [_daily_record(0, 13.0, 50.0)]

    assert compute_fake_move_score(data, _signal_parameters()) == [1.0]


def test_fake_move_breakout_normal_volume_with_reversal_within_m_returns_one() -> None:
    data = [
        _daily_record(0, 13.0, 100.0),
        _daily_record(1, 12.0, 100.0),
    ]

    result = compute_fake_move_score(
        data,
        _signal_parameters(reversal_candles=1),
    )

    assert result == [1.0, 0.0]


def test_fake_move_breakout_normal_volume_with_no_reversal_within_m_returns_zero() -> None:
    data = [
        _daily_record(0, 13.0, 100.0),
        _daily_record(1, 13.5, 100.0),
    ]

    result = compute_fake_move_score(
        data,
        _signal_parameters(reversal_candles=1),
    )

    assert result == [0.0, None]


def test_fake_move_breakout_normal_volume_with_insufficient_future_candles_returns_none() -> None:
    data = [
        _daily_record(0, 13.0, 100.0),
        _daily_record(1, 13.5, 100.0),
    ]

    result = compute_fake_move_score(data, _signal_parameters())

    assert result == [None, None]


def test_fake_move_invalid_dataset_raises_value_error() -> None:
    data = [
        _daily_record(0, 13.0, 100.0),
        _daily_record(2, 12.0, 100.0),
    ]

    with pytest.raises(ValueError, match="dataset must not skip dates"):
        compute_fake_move_score(data, _signal_parameters())


def test_fake_move_invalid_signal_parameters_raise_value_error() -> None:
    with pytest.raises(ValueError, match="reversal_candles must be > 0"):
        _signal_parameters(reversal_candles=0)


def test_fake_move_input_data_list_is_not_mutated() -> None:
    data = [
        _daily_record(0, 13.0, 100.0),
        _daily_record(1, 12.0, 100.0),
    ]
    original_data = data.copy()

    compute_fake_move_score(data, _signal_parameters(reversal_candles=1))

    assert data == original_data


def test_fake_move_does_not_return_daily_signals_objects() -> None:
    data = [
        _daily_record(0, 13.0, 100.0),
        _daily_record(1, 12.0, 100.0),
    ]

    result = compute_fake_move_score(data, _signal_parameters(reversal_candles=1))

    assert not any(isinstance(value, DailySignals) for value in result)


def test_fake_move_fully_evaluable_outputs_stay_within_unit_range() -> None:
    data = [
        _daily_record(0, 11.0, 100.0),
        _daily_record(1, 13.0, 50.0),
        _daily_record(2, 13.5, 100.0),
        _daily_record(3, 13.6, 100.0),
    ]

    result = compute_fake_move_score(
        data,
        _signal_parameters(reversal_candles=1),
    )
    fully_evaluable_values = [value for value in result if value is not None]

    assert fully_evaluable_values
    assert all(0.0 <= value <= 1.0 for value in fully_evaluable_values)


def test_daily_signals_valid_dataset_returns_daily_signals_objects() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.1, 110.0),
        _daily_record(2, 10.2, 120.0),
        _daily_record(3, 10.3, 130.0),
    ]

    result = compute_daily_signals(data, _signal_parameters())

    assert result
    assert all(isinstance(value, DailySignals) for value in result)


def test_daily_signals_output_preserves_date_and_symbol() -> None:
    data = [
        _daily_record(0, 10.0, 100.0, symbol="MM"),
        _daily_record(1, 10.1, 110.0, symbol="MM"),
        _daily_record(2, 10.2, 120.0, symbol="MM"),
    ]

    result = compute_daily_signals(data, _signal_parameters())

    assert result[0].date == data[2].date
    assert result[0].symbol == "MM"


def test_daily_signals_output_includes_all_signal_fields() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.1, 110.0),
        _daily_record(2, 10.2, 120.0),
    ]

    result = compute_daily_signals(data, _signal_parameters())
    signal = result[0]

    assert isinstance(signal.accumulation_strength, float)
    assert isinstance(signal.distribution_strength, float)
    assert isinstance(signal.liquidity_inflow, float)
    assert isinstance(signal.liquidity_outflow, float)
    assert isinstance(signal.absorption_score, float)
    assert isinstance(signal.fake_move_score, float)


def test_daily_signals_incomplete_early_and_lookahead_rows_are_skipped() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.1, 110.0),
        _daily_record(2, 10.2, 120.0),
        _daily_record(3, 13.0, 130.0),
        _daily_record(4, 13.5, 140.0),
    ]

    result = compute_daily_signals(data, _signal_parameters())

    assert [signal.date for signal in result] == [data[2].date]


def test_daily_signals_invalid_dataset_raises_value_error() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(2, 10.1, 110.0),
        _daily_record(3, 10.2, 120.0),
    ]

    with pytest.raises(ValueError, match="dataset must not skip dates"):
        compute_daily_signals(data, _signal_parameters())


def test_daily_signals_invalid_signal_parameters_raise_value_error() -> None:
    with pytest.raises(ValueError, match="rolling_window must be > 1"):
        _signal_parameters(rolling_window=1)


def test_daily_signals_no_complete_signal_rows_returns_empty_list() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.1, 110.0),
    ]

    assert compute_daily_signals(data, _signal_parameters()) == []


def test_daily_signals_input_data_list_is_not_mutated() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.1, 110.0),
        _daily_record(2, 10.2, 120.0),
    ]
    original_data = data.copy()

    compute_daily_signals(data, _signal_parameters())

    assert data == original_data


def test_daily_signals_does_not_return_raw_dicts() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.1, 110.0),
        _daily_record(2, 10.2, 120.0),
    ]

    result = compute_daily_signals(data, _signal_parameters())

    assert not any(isinstance(value, dict) for value in result)


def test_daily_signals_does_not_compute_score_confidence_or_market_phase() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.1, 110.0),
        _daily_record(2, 10.2, 120.0),
    ]

    result = compute_daily_signals(data, _signal_parameters())
    signal = result[0]

    assert not hasattr(signal, "smart_money_score")
    assert not hasattr(signal, "confidence")
    assert not hasattr(signal, "phase")


def test_daily_signals_numeric_fields_stay_within_unit_range() -> None:
    data = [
        _daily_record(0, 10.0, 100.0),
        _daily_record(1, 10.1, 110.0),
        _daily_record(2, 10.2, 120.0),
        _daily_record(3, 10.3, 130.0),
    ]

    result = compute_daily_signals(data, _signal_parameters())

    for signal in result:
        assert 0.0 <= signal.accumulation_strength <= 1.0
        assert 0.0 <= signal.distribution_strength <= 1.0
        assert 0.0 <= signal.liquidity_inflow <= 1.0
        assert 0.0 <= signal.liquidity_outflow <= 1.0
        assert 0.0 <= signal.absorption_score <= 1.0
        assert 0.0 <= signal.fake_move_score <= 1.0
