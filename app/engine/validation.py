"""Validation framework utilities."""

from app.domain.data_contract import DailyMarketData
from app.domain.dataset_validation import validate_daily_dataset
from app.domain.score_contract import DailyScore
from app.domain.validation_parameters import ValidationParameters
from app.domain.validation_result_contract import (
    DailyValidationResult,
    ValidationCheckType,
)


def compute_forward_validation(
    data: list[DailyMarketData],
    scores: list[DailyScore],
    parameters: ValidationParameters,
) -> list[DailyValidationResult]:
    """Compute forward validation results for high-score rows only."""

    validate_daily_dataset(data)

    if not scores:
        return []

    date_to_close = {record.date: record.close for record in data}
    date_to_index = {record.date: index for index, record in enumerate(data)}
    dataset_symbol = data[0].symbol

    validation_results: list[DailyValidationResult] = []
    for score in scores:
        if score.symbol != dataset_symbol:
            raise ValueError("score symbol must match dataset symbol")

        if score.date not in date_to_close:
            raise ValueError("score date must exist in dataset")

        if score.smart_money_score < parameters.high_score_threshold:
            continue

        current_index = date_to_index[score.date]
        future_index = current_index + parameters.forward_window
        if future_index >= len(data):
            continue

        current_close = date_to_close[score.date]
        future_close = data[future_index].close
        forward_return = (future_close - current_close) / current_close
        metric_value = abs(forward_return)
        passed = metric_value >= parameters.forward_return_threshold

        validation_results.append(
            DailyValidationResult(
                date=score.date,
                symbol=score.symbol,
                check_type=ValidationCheckType.FORWARD_VALIDATION,
                passed=passed,
                metric_value=float(metric_value),
            )
        )

    return validation_results


def compute_stability_check(
    scores: list[DailyScore],
    parameters: ValidationParameters,
) -> list[DailyValidationResult]:
    """Compute high-score persistence across rolling score windows."""

    if not scores:
        return []

    validation_results: list[DailyValidationResult] = []
    window_size = parameters.stability_window

    for index, score in enumerate(scores):
        if index + 1 < window_size:
            continue

        window_scores = scores[index - window_size + 1 : index + 1]
        high_score_count = sum(
            1
            for window_score in window_scores
            if window_score.smart_money_score >= parameters.high_score_threshold
        )
        persistence_ratio = high_score_count / window_size
        passed = persistence_ratio >= parameters.stability_min_persistence_ratio

        validation_results.append(
            DailyValidationResult(
                date=score.date,
                symbol=score.symbol,
                check_type=ValidationCheckType.STABILITY_CHECK,
                passed=passed,
                metric_value=float(persistence_ratio),
            )
        )

    return validation_results


def compute_false_signal_detection(
    data: list[DailyMarketData],
    scores: list[DailyScore],
    parameters: ValidationParameters,
) -> list[DailyValidationResult]:
    """Detect high-score rows followed by large absolute future movement."""

    validate_daily_dataset(data)

    if not scores:
        return []

    date_to_close = {record.date: record.close for record in data}
    date_to_index = {record.date: index for index, record in enumerate(data)}
    dataset_symbol = data[0].symbol

    validation_results: list[DailyValidationResult] = []
    for score in scores:
        if score.symbol != dataset_symbol:
            raise ValueError("score symbol must match dataset symbol")

        if score.date not in date_to_close:
            raise ValueError("score date must exist in dataset")

        if score.smart_money_score < parameters.high_score_threshold:
            continue

        current_index = date_to_index[score.date]
        future_window = data[
            current_index + 1 : current_index + 1 + parameters.false_signal_window
        ]
        if not future_window:
            continue

        current_close = date_to_close[score.date]
        metric_value = max(
            abs((future.close - current_close) / current_close)
            for future in future_window
        )
        passed = metric_value < parameters.false_signal_reversal_threshold

        validation_results.append(
            DailyValidationResult(
                date=score.date,
                symbol=score.symbol,
                check_type=ValidationCheckType.FALSE_SIGNAL_DETECTION,
                passed=passed,
                metric_value=float(metric_value),
            )
        )

    return validation_results


def compute_validation_results(
    data: list[DailyMarketData],
    scores: list[DailyScore],
    parameters: ValidationParameters,
) -> list[DailyValidationResult]:
    """Aggregate existing validation checks in deterministic order."""

    if not scores:
        return []

    return [
        *compute_forward_validation(data, scores, parameters),
        *compute_stability_check(scores, parameters),
        *compute_false_signal_detection(data, scores, parameters),
    ]
