from datetime import date, timedelta

import pytest

from app.domain.data_contract import DailyMarketData
from app.domain.score_contract import DailyScore
from app.domain.validation_parameters import ValidationParameters
from app.domain.validation_result_contract import (
    DailyValidationResult,
    ValidationCheckType,
)
from app.engine.validation import (
    compute_false_signal_detection,
    compute_forward_validation,
    compute_stability_check,
    compute_validation_results,
)


def _daily_record(
    day_offset: int,
    close: float,
    symbol: str = "MM",
) -> DailyMarketData:
    return DailyMarketData(
        date=date(2024, 1, 1) + timedelta(days=day_offset),
        open=close,
        high=close + 1.0,
        low=close - 1.0,
        close=close,
        volume=100.0,
        symbol=symbol,
    )


def _daily_score(
    day_offset: int,
    smart_money_score: float,
    symbol: str = "MM",
) -> DailyScore:
    return DailyScore(
        date=date(2024, 1, 1) + timedelta(days=day_offset),
        symbol=symbol,
        smart_money_score=smart_money_score,
    )


def _validation_parameters(**overrides: object) -> ValidationParameters:
    values: dict[str, object] = {
        "high_score_threshold": 70.0,
        "forward_window": 2,
        "forward_return_threshold": 0.05,
        "stability_window": 3,
        "stability_min_persistence_ratio": 0.6,
        "false_signal_window": 2,
        "false_signal_reversal_threshold": 0.04,
    }
    values.update(overrides)
    return ValidationParameters(**values)


def _aggregation_data() -> list[DailyMarketData]:
    return [
        _daily_record(0, 100.0),
        _daily_record(1, 102.0),
        _daily_record(2, 106.0),
        _daily_record(3, 108.0),
        _daily_record(4, 112.0),
    ]


def _aggregation_scores() -> list[DailyScore]:
    return [
        _daily_score(0, 90.0),
        _daily_score(1, 80.0),
        _daily_score(2, 75.0),
    ]


def test_forward_validation_empty_scores_returns_empty_list() -> None:
    data = [_daily_record(0, 10.0), _daily_record(1, 11.0)]

    result = compute_forward_validation(data, [], _validation_parameters())

    assert result == []


def test_forward_validation_low_score_rows_are_skipped() -> None:
    data = [
        _daily_record(0, 10.0),
        _daily_record(1, 10.5),
        _daily_record(2, 11.0),
    ]
    scores = [_daily_score(0, 69.0)]

    result = compute_forward_validation(data, scores, _validation_parameters())

    assert result == []


def test_forward_validation_high_score_with_absolute_forward_return_at_threshold_passes() -> None:
    data = [
        _daily_record(0, 10.0),
        _daily_record(1, 10.2),
        _daily_record(2, 10.5),
    ]
    scores = [_daily_score(0, 70.0)]

    result = compute_forward_validation(data, scores, _validation_parameters())

    assert result[0].passed is True
    assert result[0].metric_value == pytest.approx(0.05)


def test_forward_validation_high_score_below_forward_return_threshold_fails() -> None:
    data = [
        _daily_record(0, 10.0),
        _daily_record(1, 10.1),
        _daily_record(2, 10.4),
    ]
    scores = [_daily_score(0, 90.0)]

    result = compute_forward_validation(data, scores, _validation_parameters())

    assert result[0].passed is False
    assert result[0].metric_value == pytest.approx(0.04)


def test_forward_validation_negative_forward_return_uses_absolute_metric_value() -> None:
    data = [
        _daily_record(0, 10.0),
        _daily_record(1, 9.8),
        _daily_record(2, 9.0),
    ]
    scores = [_daily_score(0, 90.0)]

    result = compute_forward_validation(data, scores, _validation_parameters())

    assert result[0].metric_value == pytest.approx(0.1)
    assert result[0].passed is True


def test_forward_validation_row_without_enough_future_data_is_skipped() -> None:
    data = [
        _daily_record(0, 10.0),
        _daily_record(1, 10.5),
        _daily_record(2, 11.0),
    ]
    scores = [_daily_score(2, 90.0)]

    result = compute_forward_validation(data, scores, _validation_parameters())

    assert result == []


def test_forward_validation_score_symbol_mismatch_raises_value_error() -> None:
    data = [_daily_record(0, 10.0), _daily_record(1, 11.0)]
    scores = [_daily_score(0, 90.0, symbol="OTHER")]

    with pytest.raises(ValueError, match="score symbol must match dataset symbol"):
        compute_forward_validation(data, scores, _validation_parameters())


def test_forward_validation_score_date_missing_from_dataset_raises_value_error() -> None:
    data = [_daily_record(0, 10.0), _daily_record(1, 11.0)]
    scores = [_daily_score(2, 90.0)]

    with pytest.raises(ValueError, match="score date must exist in dataset"):
        compute_forward_validation(data, scores, _validation_parameters())


def test_forward_validation_invalid_dataset_raises_value_error() -> None:
    data = [_daily_record(0, 10.0), _daily_record(2, 11.0)]
    scores = [_daily_score(0, 90.0)]

    with pytest.raises(ValueError, match="dataset must not skip dates"):
        compute_forward_validation(data, scores, _validation_parameters())


def test_forward_validation_output_preserves_date_and_symbol_from_daily_score() -> None:
    data = [
        _daily_record(0, 10.0, symbol="MMAI"),
        _daily_record(1, 10.2, symbol="MMAI"),
        _daily_record(2, 10.5, symbol="MMAI"),
    ]
    scores = [_daily_score(0, 90.0, symbol="MMAI")]

    result = compute_forward_validation(data, scores, _validation_parameters())

    assert result[0].date == scores[0].date
    assert result[0].symbol == scores[0].symbol


def test_forward_validation_output_check_type_is_forward_validation() -> None:
    data = [
        _daily_record(0, 10.0),
        _daily_record(1, 10.2),
        _daily_record(2, 10.5),
    ]
    scores = [_daily_score(0, 90.0)]

    result = compute_forward_validation(data, scores, _validation_parameters())

    assert result[0].check_type is ValidationCheckType.FORWARD_VALIDATION


def test_forward_validation_returns_daily_validation_result_objects_not_raw_dicts() -> None:
    data = [
        _daily_record(0, 10.0),
        _daily_record(1, 10.2),
        _daily_record(2, 10.5),
    ]
    scores = [_daily_score(0, 90.0)]

    result = compute_forward_validation(data, scores, _validation_parameters())

    assert all(isinstance(value, DailyValidationResult) for value in result)
    assert not any(isinstance(value, dict) for value in result)


def test_forward_validation_does_not_compute_stability_check() -> None:
    data = [
        _daily_record(0, 10.0),
        _daily_record(1, 10.2),
        _daily_record(2, 10.5),
    ]
    scores = [_daily_score(0, 90.0)]

    result = compute_forward_validation(data, scores, _validation_parameters())

    assert not any(
        value.check_type is ValidationCheckType.STABILITY_CHECK
        for value in result
    )


def test_forward_validation_does_not_compute_false_signal_detection() -> None:
    data = [
        _daily_record(0, 10.0),
        _daily_record(1, 10.2),
        _daily_record(2, 10.5),
    ]
    scores = [_daily_score(0, 90.0)]

    result = compute_forward_validation(data, scores, _validation_parameters())

    assert not any(
        value.check_type is ValidationCheckType.FALSE_SIGNAL_DETECTION
        for value in result
    )


def test_forward_validation_does_not_use_confidence_or_market_phase() -> None:
    data = [
        _daily_record(0, 10.0),
        _daily_record(1, 10.2),
        _daily_record(2, 10.5),
    ]
    scores = [_daily_score(0, 90.0)]

    result = compute_forward_validation(data, scores, _validation_parameters())

    assert not hasattr(result[0], "confidence")
    assert not hasattr(result[0], "phase")


def test_forward_validation_input_data_and_scores_are_not_mutated() -> None:
    data = [
        _daily_record(0, 10.0),
        _daily_record(1, 10.2),
        _daily_record(2, 10.5),
    ]
    scores = [_daily_score(0, 90.0)]
    original_data = data.copy()
    original_scores = scores.copy()

    compute_forward_validation(data, scores, _validation_parameters())

    assert data == original_data
    assert scores == original_scores


def test_stability_check_empty_scores_returns_empty_list() -> None:
    result = compute_stability_check([], _validation_parameters())

    assert result == []


def test_stability_check_insufficient_score_history_returns_empty_list() -> None:
    scores = [_daily_score(0, 90.0), _daily_score(1, 90.0)]

    result = compute_stability_check(scores, _validation_parameters())

    assert result == []


def test_stability_check_persistence_ratio_at_threshold_passes() -> None:
    scores = [
        _daily_score(0, 80.0),
        _daily_score(1, 80.0),
        _daily_score(2, 40.0),
    ]

    result = compute_stability_check(scores, _validation_parameters())

    assert result[0].passed is True
    assert result[0].metric_value == pytest.approx(2 / 3)


def test_stability_check_persistence_ratio_below_threshold_fails() -> None:
    scores = [
        _daily_score(0, 80.0),
        _daily_score(1, 40.0),
        _daily_score(2, 40.0),
    ]

    result = compute_stability_check(scores, _validation_parameters())

    assert result[0].passed is False
    assert result[0].metric_value == pytest.approx(1 / 3)


def test_stability_check_metric_value_equals_high_score_count_divided_by_window() -> None:
    scores = [
        _daily_score(0, 80.0),
        _daily_score(1, 40.0),
        _daily_score(2, 80.0),
        _daily_score(3, 80.0),
    ]

    result = compute_stability_check(scores, _validation_parameters())

    assert result[0].metric_value == pytest.approx(2 / 3)
    assert result[1].metric_value == pytest.approx(2 / 3)


def test_stability_check_output_preserves_date_and_symbol_from_current_daily_score() -> None:
    scores = [
        _daily_score(0, 80.0, symbol="MMAI"),
        _daily_score(1, 80.0, symbol="MMAI"),
        _daily_score(2, 80.0, symbol="MMAI"),
    ]

    result = compute_stability_check(scores, _validation_parameters())

    assert result[0].date == scores[2].date
    assert result[0].symbol == scores[2].symbol


def test_stability_check_output_check_type_is_stability_check() -> None:
    scores = [
        _daily_score(0, 80.0),
        _daily_score(1, 80.0),
        _daily_score(2, 80.0),
    ]

    result = compute_stability_check(scores, _validation_parameters())

    assert result[0].check_type is ValidationCheckType.STABILITY_CHECK


def test_stability_check_returns_daily_validation_result_objects_not_raw_dicts() -> None:
    scores = [
        _daily_score(0, 80.0),
        _daily_score(1, 80.0),
        _daily_score(2, 80.0),
    ]

    result = compute_stability_check(scores, _validation_parameters())

    assert all(isinstance(value, DailyValidationResult) for value in result)
    assert not any(isinstance(value, dict) for value in result)


def test_stability_check_does_not_compute_forward_validation() -> None:
    scores = [
        _daily_score(0, 80.0),
        _daily_score(1, 80.0),
        _daily_score(2, 80.0),
    ]

    result = compute_stability_check(scores, _validation_parameters())

    assert not any(
        value.check_type is ValidationCheckType.FORWARD_VALIDATION
        for value in result
    )


def test_stability_check_does_not_compute_false_signal_detection() -> None:
    scores = [
        _daily_score(0, 80.0),
        _daily_score(1, 80.0),
        _daily_score(2, 80.0),
    ]

    result = compute_stability_check(scores, _validation_parameters())

    assert not any(
        value.check_type is ValidationCheckType.FALSE_SIGNAL_DETECTION
        for value in result
    )


def test_stability_check_does_not_use_confidence_or_market_phase() -> None:
    scores = [
        _daily_score(0, 80.0),
        _daily_score(1, 80.0),
        _daily_score(2, 80.0),
    ]

    result = compute_stability_check(scores, _validation_parameters())

    assert not hasattr(result[0], "confidence")
    assert not hasattr(result[0], "phase")


def test_stability_check_input_scores_are_not_mutated() -> None:
    scores = [
        _daily_score(0, 80.0),
        _daily_score(1, 80.0),
        _daily_score(2, 80.0),
    ]
    original_scores = scores.copy()

    compute_stability_check(scores, _validation_parameters())

    assert scores == original_scores


def test_false_signal_detection_empty_scores_returns_empty_list() -> None:
    data = [_daily_record(0, 100.0), _daily_record(1, 101.0)]

    result = compute_false_signal_detection(data, [], _validation_parameters())

    assert result == []


def test_false_signal_detection_low_score_rows_are_skipped() -> None:
    data = [_daily_record(0, 100.0), _daily_record(1, 105.0)]
    scores = [_daily_score(0, 69.0)]

    result = compute_false_signal_detection(data, scores, _validation_parameters())

    assert result == []


def test_false_signal_detection_high_score_below_future_threshold_passes() -> None:
    data = [
        _daily_record(0, 100.0),
        _daily_record(1, 101.0),
        _daily_record(2, 102.0),
    ]
    scores = [_daily_score(0, 90.0)]

    result = compute_false_signal_detection(data, scores, _validation_parameters())

    assert result[0].passed is True
    assert result[0].metric_value == pytest.approx(0.02)


def test_false_signal_detection_high_score_equal_future_threshold_fails() -> None:
    data = [
        _daily_record(0, 100.0),
        _daily_record(1, 104.0),
        _daily_record(2, 102.0),
    ]
    scores = [_daily_score(0, 90.0)]

    result = compute_false_signal_detection(data, scores, _validation_parameters())

    assert result[0].passed is False
    assert result[0].metric_value == pytest.approx(0.04)


def test_false_signal_detection_high_score_above_future_threshold_fails() -> None:
    data = [
        _daily_record(0, 100.0),
        _daily_record(1, 103.0),
        _daily_record(2, 105.0),
    ]
    scores = [_daily_score(0, 90.0)]

    result = compute_false_signal_detection(data, scores, _validation_parameters())

    assert result[0].passed is False
    assert result[0].metric_value == pytest.approx(0.05)


def test_false_signal_detection_negative_future_return_uses_absolute_metric_value() -> None:
    data = [
        _daily_record(0, 100.0),
        _daily_record(1, 99.0),
        _daily_record(2, 95.0),
    ]
    scores = [_daily_score(0, 90.0)]

    result = compute_false_signal_detection(data, scores, _validation_parameters())

    assert result[0].metric_value == pytest.approx(0.05)
    assert result[0].passed is False


def test_false_signal_detection_row_without_future_data_is_skipped() -> None:
    data = [_daily_record(0, 100.0), _daily_record(1, 101.0)]
    scores = [_daily_score(1, 90.0)]

    result = compute_false_signal_detection(data, scores, _validation_parameters())

    assert result == []


def test_false_signal_detection_score_symbol_mismatch_raises_value_error() -> None:
    data = [_daily_record(0, 100.0), _daily_record(1, 101.0)]
    scores = [_daily_score(0, 90.0, symbol="OTHER")]

    with pytest.raises(ValueError, match="score symbol must match dataset symbol"):
        compute_false_signal_detection(data, scores, _validation_parameters())


def test_false_signal_detection_score_date_missing_from_dataset_raises_value_error() -> None:
    data = [_daily_record(0, 100.0), _daily_record(1, 101.0)]
    scores = [_daily_score(2, 90.0)]

    with pytest.raises(ValueError, match="score date must exist in dataset"):
        compute_false_signal_detection(data, scores, _validation_parameters())


def test_false_signal_detection_invalid_dataset_raises_value_error() -> None:
    data = [_daily_record(0, 100.0), _daily_record(2, 101.0)]
    scores = [_daily_score(0, 90.0)]

    with pytest.raises(ValueError, match="dataset must not skip dates"):
        compute_false_signal_detection(data, scores, _validation_parameters())


def test_false_signal_detection_output_preserves_date_and_symbol_from_daily_score() -> None:
    data = [
        _daily_record(0, 100.0, symbol="MMAI"),
        _daily_record(1, 101.0, symbol="MMAI"),
    ]
    scores = [_daily_score(0, 90.0, symbol="MMAI")]

    result = compute_false_signal_detection(data, scores, _validation_parameters())

    assert result[0].date == scores[0].date
    assert result[0].symbol == scores[0].symbol


def test_false_signal_detection_output_check_type_is_false_signal_detection() -> None:
    data = [_daily_record(0, 100.0), _daily_record(1, 101.0)]
    scores = [_daily_score(0, 90.0)]

    result = compute_false_signal_detection(data, scores, _validation_parameters())

    assert result[0].check_type is ValidationCheckType.FALSE_SIGNAL_DETECTION


def test_false_signal_detection_returns_daily_validation_result_objects_not_raw_dicts() -> None:
    data = [_daily_record(0, 100.0), _daily_record(1, 101.0)]
    scores = [_daily_score(0, 90.0)]

    result = compute_false_signal_detection(data, scores, _validation_parameters())

    assert all(isinstance(value, DailyValidationResult) for value in result)
    assert not any(isinstance(value, dict) for value in result)


def test_false_signal_detection_does_not_compute_forward_validation() -> None:
    data = [_daily_record(0, 100.0), _daily_record(1, 101.0)]
    scores = [_daily_score(0, 90.0)]

    result = compute_false_signal_detection(data, scores, _validation_parameters())

    assert not any(
        value.check_type is ValidationCheckType.FORWARD_VALIDATION
        for value in result
    )


def test_false_signal_detection_does_not_compute_stability_check() -> None:
    data = [_daily_record(0, 100.0), _daily_record(1, 101.0)]
    scores = [_daily_score(0, 90.0)]

    result = compute_false_signal_detection(data, scores, _validation_parameters())

    assert not any(
        value.check_type is ValidationCheckType.STABILITY_CHECK
        for value in result
    )


def test_false_signal_detection_does_not_use_confidence_or_market_phase() -> None:
    data = [_daily_record(0, 100.0), _daily_record(1, 101.0)]
    scores = [_daily_score(0, 90.0)]

    result = compute_false_signal_detection(data, scores, _validation_parameters())

    assert not hasattr(result[0], "confidence")
    assert not hasattr(result[0], "phase")


def test_false_signal_detection_input_data_and_scores_are_not_mutated() -> None:
    data = [_daily_record(0, 100.0), _daily_record(1, 101.0)]
    scores = [_daily_score(0, 90.0)]
    original_data = data.copy()
    original_scores = scores.copy()

    compute_false_signal_detection(data, scores, _validation_parameters())

    assert data == original_data
    assert scores == original_scores


def test_validation_results_empty_scores_returns_empty_list() -> None:
    data = [_daily_record(0, 100.0), _daily_record(1, 101.0)]

    result = compute_validation_results(data, [], _validation_parameters())

    assert result == []


def test_validation_results_combined_output_includes_forward_validation_results() -> None:
    result = compute_validation_results(
        _aggregation_data(),
        _aggregation_scores(),
        _validation_parameters(),
    )

    assert any(
        value.check_type is ValidationCheckType.FORWARD_VALIDATION
        for value in result
    )


def test_validation_results_combined_output_includes_stability_check_results() -> None:
    result = compute_validation_results(
        _aggregation_data(),
        _aggregation_scores(),
        _validation_parameters(),
    )

    assert any(
        value.check_type is ValidationCheckType.STABILITY_CHECK
        for value in result
    )


def test_validation_results_combined_output_includes_false_signal_detection_results() -> None:
    result = compute_validation_results(
        _aggregation_data(),
        _aggregation_scores(),
        _validation_parameters(),
    )

    assert any(
        value.check_type is ValidationCheckType.FALSE_SIGNAL_DETECTION
        for value in result
    )


def test_validation_results_combined_output_order_is_deterministic() -> None:
    result = compute_validation_results(
        _aggregation_data(),
        _aggregation_scores(),
        _validation_parameters(),
    )

    assert [value.check_type for value in result] == [
        ValidationCheckType.FORWARD_VALIDATION,
        ValidationCheckType.FORWARD_VALIDATION,
        ValidationCheckType.FORWARD_VALIDATION,
        ValidationCheckType.STABILITY_CHECK,
        ValidationCheckType.FALSE_SIGNAL_DETECTION,
        ValidationCheckType.FALSE_SIGNAL_DETECTION,
        ValidationCheckType.FALSE_SIGNAL_DETECTION,
    ]


def test_validation_results_invalid_dataset_raises_value_error() -> None:
    data = [_daily_record(0, 100.0), _daily_record(2, 101.0)]
    scores = [_daily_score(0, 90.0)]

    with pytest.raises(ValueError, match="dataset must not skip dates"):
        compute_validation_results(data, scores, _validation_parameters())


def test_validation_results_score_symbol_mismatch_raises_value_error() -> None:
    scores = [_daily_score(0, 90.0, symbol="OTHER")]

    with pytest.raises(ValueError, match="score symbol must match dataset symbol"):
        compute_validation_results(
            _aggregation_data(),
            scores,
            _validation_parameters(),
        )


def test_validation_results_score_date_missing_from_dataset_raises_value_error() -> None:
    scores = [_daily_score(9, 90.0)]

    with pytest.raises(ValueError, match="score date must exist in dataset"):
        compute_validation_results(
            _aggregation_data(),
            scores,
            _validation_parameters(),
        )


def test_validation_results_returns_daily_validation_result_objects_not_raw_dicts() -> None:
    result = compute_validation_results(
        _aggregation_data(),
        _aggregation_scores(),
        _validation_parameters(),
    )

    assert all(isinstance(value, DailyValidationResult) for value in result)
    assert not any(isinstance(value, dict) for value in result)


def test_validation_results_does_not_compute_unsupported_check_types() -> None:
    result = compute_validation_results(
        _aggregation_data(),
        _aggregation_scores(),
        _validation_parameters(),
    )
    supported_types = {
        ValidationCheckType.FORWARD_VALIDATION,
        ValidationCheckType.STABILITY_CHECK,
        ValidationCheckType.FALSE_SIGNAL_DETECTION,
    }

    assert {value.check_type for value in result} <= supported_types


def test_validation_results_does_not_compute_pass_fail_summary() -> None:
    result = compute_validation_results(
        _aggregation_data(),
        _aggregation_scores(),
        _validation_parameters(),
    )

    assert isinstance(result, list)
    assert not hasattr(result, "pass_rate")
    assert not hasattr(result, "passed_count")
    assert not hasattr(result, "failed_count")


def test_validation_results_does_not_use_confidence_or_market_phase() -> None:
    result = compute_validation_results(
        _aggregation_data(),
        _aggregation_scores(),
        _validation_parameters(),
    )

    assert not any(hasattr(value, "confidence") for value in result)
    assert not any(hasattr(value, "phase") for value in result)


def test_validation_results_input_data_and_scores_are_not_mutated() -> None:
    data = _aggregation_data()
    scores = _aggregation_scores()
    original_data = data.copy()
    original_scores = scores.copy()

    compute_validation_results(data, scores, _validation_parameters())

    assert data == original_data
    assert scores == original_scores
