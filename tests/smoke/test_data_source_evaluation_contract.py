import pytest

from app.domain.data_source_contract import DataSourceReliability
from app.domain.data_source_evaluation_contract import (
    DataSourceEvaluationCheck,
    DataSourceEvaluationResult,
)


def _evaluation_result(**overrides: object) -> DataSourceEvaluationResult:
    values: dict[str, object] = {
        "source_name": "Example Source",
        "check": DataSourceEvaluationCheck.SOURCE_TYPE_CHECK,
        "passed": True,
        "reliability_after_check": DataSourceReliability.UNVERIFIED,
        "details": "Metadata-only evaluation result for future source checks.",
    }
    values.update(overrides)
    return DataSourceEvaluationResult(**values)


@pytest.mark.parametrize("check", list(DataSourceEvaluationCheck))
def test_data_source_evaluation_result_valid_allowed_check_passes(
    check: DataSourceEvaluationCheck,
) -> None:
    result = _evaluation_result(check=check)

    assert result.check is check
    assert result.reliability_after_check is DataSourceReliability.UNVERIFIED


def test_data_source_evaluation_result_empty_source_name_raises_value_error() -> None:
    with pytest.raises(ValueError, match="source_name must not be empty"):
        _evaluation_result(source_name=" ")


def test_data_source_evaluation_result_invalid_check_string_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="check must be a valid DataSourceEvaluationCheck value",
    ):
        _evaluation_result(check="SOURCE_TYPE_CHECK")


def test_data_source_evaluation_result_none_check_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="check must be a valid DataSourceEvaluationCheck value",
    ):
        _evaluation_result(check=None)


def test_data_source_evaluation_result_non_bool_passed_raises_value_error() -> None:
    with pytest.raises(ValueError, match="passed must be bool"):
        _evaluation_result(passed="true")


def test_data_source_evaluation_result_invalid_reliability_string_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="reliability_after_check must be a valid DataSourceReliability value",
    ):
        _evaluation_result(reliability_after_check="UNVERIFIED")


def test_data_source_evaluation_result_none_reliability_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="reliability_after_check must be a valid DataSourceReliability value",
    ):
        _evaluation_result(reliability_after_check=None)


def test_data_source_evaluation_result_empty_details_raises_value_error() -> None:
    with pytest.raises(ValueError, match="details must not be empty"):
        _evaluation_result(details="")


def test_data_source_evaluation_result_constructor_requires_explicit_values() -> None:
    with pytest.raises(TypeError):
        DataSourceEvaluationResult()
