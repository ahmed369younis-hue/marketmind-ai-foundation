import pytest

from app.engine.time_series import (
    moving_average,
    period_return,
    rolling_slope,
    rolling_std,
)


def test_empty_values_returns_empty_list() -> None:
    assert rolling_std([], 3) == []


def test_insufficient_history_returns_none_values() -> None:
    assert rolling_std([1.0, 2.0], 3) == [None, None]


def test_constant_window_returns_zero() -> None:
    assert rolling_std([1.0, 1.0, 1.0], 3) == [None, None, 0.0]


def test_known_population_std_case_is_correct() -> None:
    result = rolling_std([1.0, 2.0, 3.0], 3)

    assert result == [None, None, pytest.approx((2.0 / 3.0) ** 0.5)]


def test_none_inside_window_returns_none_for_affected_window() -> None:
    result = rolling_std([1.0, None, 3.0, 4.0, 5.0], 3)

    assert result == [None, None, None, None, pytest.approx((2.0 / 3.0) ** 0.5)]


def test_input_list_is_not_mutated() -> None:
    values = [1.0, 2.0, 3.0]
    original_values = values.copy()

    rolling_std(values, 3)

    assert values == original_values


def test_window_equal_to_one_raises_explicit_error() -> None:
    with pytest.raises(ValueError, match="window must be greater than 1"):
        rolling_std([1.0, 2.0], 1)


def test_window_less_than_one_raises_explicit_error() -> None:
    with pytest.raises(ValueError, match="window must be greater than 1"):
        rolling_std([1.0, 2.0], 0)


def test_slope_empty_values_returns_empty_list() -> None:
    assert rolling_slope([], 3) == []


def test_slope_insufficient_history_returns_none_values() -> None:
    assert rolling_slope([1.0, 2.0], 3) == [None, None]


def test_slope_constant_window_returns_zero() -> None:
    assert rolling_slope([1.0, 1.0, 1.0], 3) == [None, None, 0.0]


def test_slope_increasing_linear_sequence_returns_one() -> None:
    assert rolling_slope([1.0, 2.0, 3.0], 3) == [None, None, 1.0]


def test_slope_decreasing_linear_sequence_returns_negative_one() -> None:
    assert rolling_slope([3.0, 2.0, 1.0], 3) == [None, None, -1.0]


def test_slope_none_inside_window_returns_none_for_affected_window() -> None:
    result = rolling_slope([1.0, None, 3.0, 4.0, 5.0], 3)

    assert result == [None, None, None, None, 1.0]


def test_slope_input_list_is_not_mutated() -> None:
    values = [1.0, 2.0, 3.0]
    original_values = values.copy()

    rolling_slope(values, 3)

    assert values == original_values


def test_slope_window_equal_to_one_raises_explicit_error() -> None:
    with pytest.raises(ValueError, match="window must be greater than 1"):
        rolling_slope([1.0, 2.0], 1)


def test_slope_window_less_than_one_raises_explicit_error() -> None:
    with pytest.raises(ValueError, match="window must be greater than 1"):
        rolling_slope([1.0, 2.0], 0)


def test_moving_average_empty_values_returns_empty_list() -> None:
    assert moving_average([], 3) == []


def test_moving_average_insufficient_history_returns_none_values() -> None:
    assert moving_average([1.0, 2.0], 3) == [None, None]


def test_moving_average_known_average_with_window_three_is_correct() -> None:
    assert moving_average([1.0, 2.0, 3.0], 3) == [None, None, 2.0]


def test_moving_average_rolling_average_with_window_two_is_correct() -> None:
    assert moving_average([2.0, 4.0, 6.0, 8.0], 2) == [None, 3.0, 5.0, 7.0]


def test_moving_average_none_inside_window_returns_none_for_affected_window() -> None:
    result = moving_average([1.0, None, 3.0, 4.0, 5.0], 3)

    assert result == [None, None, None, None, 4.0]


def test_moving_average_input_list_is_not_mutated() -> None:
    values = [1.0, 2.0, 3.0]
    original_values = values.copy()

    moving_average(values, 3)

    assert values == original_values


def test_moving_average_window_equal_to_zero_raises_explicit_error() -> None:
    with pytest.raises(ValueError, match="window must be greater than 0"):
        moving_average([1.0, 2.0], 0)


def test_moving_average_window_less_than_zero_raises_explicit_error() -> None:
    with pytest.raises(ValueError, match="window must be greater than 0"):
        moving_average([1.0, 2.0], -1)


def test_period_return_empty_values_returns_empty_list() -> None:
    assert period_return([], 1) == []


def test_period_return_insufficient_history_returns_none_values() -> None:
    assert period_return([10.0], 1) == [None]


def test_period_return_one_period_positive_return_is_correct() -> None:
    result = period_return([10.0, 11.0], 1)

    assert result == [None, pytest.approx(0.1)]


def test_period_return_multi_period_return_is_correct() -> None:
    assert period_return([10.0, 12.0, 15.0], 2) == [None, None, 0.5]


def test_period_return_none_current_value_returns_none() -> None:
    assert period_return([10.0, None], 1) == [None, None]


def test_period_return_none_previous_value_returns_none() -> None:
    assert period_return([None, 11.0], 1) == [None, None]


def test_period_return_input_list_is_not_mutated() -> None:
    values = [10.0, 11.0]
    original_values = values.copy()

    period_return(values, 1)

    assert values == original_values


def test_period_return_previous_value_zero_raises_explicit_error() -> None:
    with pytest.raises(ValueError, match="previous value must not be zero"):
        period_return([0.0, 1.0], 1)


def test_period_return_periods_equal_to_zero_raises_explicit_error() -> None:
    with pytest.raises(ValueError, match="periods must be greater than 0"):
        period_return([10.0, 11.0], 0)


def test_period_return_periods_less_than_zero_raises_explicit_error() -> None:
    with pytest.raises(ValueError, match="periods must be greater than 0"):
        period_return([10.0, 11.0], -1)
