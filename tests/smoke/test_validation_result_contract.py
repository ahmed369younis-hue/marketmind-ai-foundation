import inspect
from datetime import date, timedelta

import pytest

from app.domain.validation_result_contract import (
    DailyValidationResult,
    ValidationCheckType,
)


def valid_daily_validation_result(**overrides: object) -> dict[str, object]:
    validation_result: dict[str, object] = {
        "date": date.today(),
        "symbol": "MMAI",
        "check_type": ValidationCheckType.FORWARD_VALIDATION,
        "passed": True,
        "metric_value": 0.1,
    }
    validation_result.update(overrides)
    return validation_result


def test_valid_daily_validation_result_with_forward_validation_passes() -> None:
    result = DailyValidationResult(
        **valid_daily_validation_result(
            check_type=ValidationCheckType.FORWARD_VALIDATION,
        )
    )

    assert result.check_type is ValidationCheckType.FORWARD_VALIDATION


def test_valid_daily_validation_result_with_stability_check_passes() -> None:
    result = DailyValidationResult(
        **valid_daily_validation_result(
            check_type=ValidationCheckType.STABILITY_CHECK,
        )
    )

    assert result.check_type is ValidationCheckType.STABILITY_CHECK


def test_valid_daily_validation_result_with_false_signal_detection_passes() -> None:
    result = DailyValidationResult(
        **valid_daily_validation_result(
            check_type=ValidationCheckType.FALSE_SIGNAL_DETECTION,
        )
    )

    assert result.check_type is ValidationCheckType.FALSE_SIGNAL_DETECTION


def test_future_date_raises_value_error() -> None:
    with pytest.raises(ValueError, match="date must not be in the future"):
        DailyValidationResult(
            **valid_daily_validation_result(date=date.today() + timedelta(days=1))
        )


def test_empty_symbol_raises_value_error() -> None:
    with pytest.raises(ValueError, match="symbol must not be empty"):
        DailyValidationResult(**valid_daily_validation_result(symbol=""))


def test_invalid_check_type_string_raises_value_error() -> None:
    with pytest.raises(ValueError, match="check_type must be a valid ValidationCheckType value"):
        DailyValidationResult(**valid_daily_validation_result(check_type="INVALID"))


def test_none_check_type_raises_value_error() -> None:
    with pytest.raises(ValueError, match="check_type must be a valid ValidationCheckType value"):
        DailyValidationResult(**valid_daily_validation_result(check_type=None))


def test_non_bool_passed_raises_value_error() -> None:
    with pytest.raises(ValueError, match="passed must be bool"):
        DailyValidationResult(**valid_daily_validation_result(passed=1))


def test_negative_metric_value_raises_value_error() -> None:
    with pytest.raises(ValueError, match="metric_value must be >= 0"):
        DailyValidationResult(**valid_daily_validation_result(metric_value=-0.1))


def test_daily_validation_result_constructor_requires_explicit_values() -> None:
    signature = inspect.signature(DailyValidationResult)

    assert all(
        parameter.default is inspect.Parameter.empty
        for parameter in signature.parameters.values()
    )

    with pytest.raises(TypeError):
        DailyValidationResult()
