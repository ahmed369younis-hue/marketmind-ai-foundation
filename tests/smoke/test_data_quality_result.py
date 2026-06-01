from pathlib import Path

import pytest

from app.domain.data_quality_result import DataQualityCheck, DataQualityResult


@pytest.mark.parametrize("check", list(DataQualityCheck))
def test_valid_data_quality_result_for_each_allowed_check_passes(
    check: DataQualityCheck,
) -> None:
    result = DataQualityResult(
        check=check,
        passed=True,
        metric_value=1.0,
        details="Future quality check result.",
    )

    assert isinstance(result, DataQualityResult)


def test_invalid_check_string_raises_value_error() -> None:
    with pytest.raises(ValueError):
        DataQualityResult(
            check="RECORD_COUNT_CHECK",
            passed=True,
            metric_value=1.0,
            details="Invalid check.",
        )


def test_none_check_raises_value_error() -> None:
    with pytest.raises(ValueError):
        DataQualityResult(
            check=None,
            passed=True,
            metric_value=1.0,
            details="Missing check.",
        )


def test_non_bool_passed_raises_value_error() -> None:
    with pytest.raises(ValueError):
        DataQualityResult(
            check=DataQualityCheck.RECORD_COUNT_CHECK,
            passed="yes",
            metric_value=1.0,
            details="Invalid passed value.",
        )


def test_negative_metric_value_raises_value_error() -> None:
    with pytest.raises(ValueError):
        DataQualityResult(
            check=DataQualityCheck.RECORD_COUNT_CHECK,
            passed=False,
            metric_value=-1.0,
            details="Negative metric.",
        )


def test_empty_details_raises_value_error() -> None:
    with pytest.raises(ValueError):
        DataQualityResult(
            check=DataQualityCheck.RECORD_COUNT_CHECK,
            passed=True,
            metric_value=1.0,
            details=" ",
        )


def test_constructor_requires_explicit_values_and_has_no_defaults() -> None:
    with pytest.raises(TypeError):
        DataQualityResult()


def test_no_external_dependency_imports_are_introduced() -> None:
    source = Path("app/domain/data_quality_result.py").read_text(encoding="utf-8")

    for package_name in ["pandas", "numpy", "yfinance", "requests", "sqlalchemy"]:
        assert f"import {package_name}" not in source
        assert f"from {package_name}" not in source
