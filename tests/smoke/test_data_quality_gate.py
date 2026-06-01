from pathlib import Path

import pytest

from app.data.quality_gate import can_pass_data_quality_gate
from app.domain.data_quality_result import DataQualityCheck, DataQualityResult


REQUIRED_CHECKS = [
    DataQualityCheck.RECORD_COUNT_CHECK,
    DataQualityCheck.DATE_RANGE_COVERAGE_CHECK,
    DataQualityCheck.SYMBOL_CONSISTENCY_CHECK,
    DataQualityCheck.OHLCV_VALIDITY_CHECK,
    DataQualityCheck.DAILY_CONTINUITY_CHECK,
    DataQualityCheck.MISSING_VALUE_CHECK,
]


def _result(check: DataQualityCheck, passed: bool = True) -> DataQualityResult:
    return DataQualityResult(
        check=check,
        passed=passed,
        metric_value=1.0,
        details="Quality gate test result.",
    )


def _passing_results() -> list[DataQualityResult]:
    return [_result(check) for check in REQUIRED_CHECKS]


def test_all_six_required_checks_present_and_passed_returns_true() -> None:
    assert can_pass_data_quality_gate(_passing_results()) is True


def test_empty_results_returns_false() -> None:
    assert can_pass_data_quality_gate([]) is False


def test_missing_required_check_returns_false() -> None:
    results = _passing_results()[:-1]

    assert can_pass_data_quality_gate(results) is False


def test_duplicate_required_check_returns_false() -> None:
    results = _passing_results()[:-1] + [_result(DataQualityCheck.RECORD_COUNT_CHECK)]

    assert can_pass_data_quality_gate(results) is False


def test_any_failed_check_returns_false() -> None:
    results = _passing_results()
    results[2] = _result(DataQualityCheck.SYMBOL_CONSISTENCY_CHECK, passed=False)

    assert can_pass_data_quality_gate(results) is False


def test_non_list_results_raises_value_error() -> None:
    with pytest.raises(ValueError):
        can_pass_data_quality_gate(tuple(_passing_results()))


def test_list_containing_non_data_quality_result_raises_value_error() -> None:
    with pytest.raises(ValueError):
        can_pass_data_quality_gate(_passing_results() + ["not a result"])


def test_input_results_list_is_not_mutated() -> None:
    results = _passing_results()
    original_results = list(results)

    can_pass_data_quality_gate(results)

    assert results == original_results


def test_function_does_not_call_evaluate_daily_dataset_quality() -> None:
    source = Path("app/data/quality_gate.py").read_text(encoding="utf-8")

    assert "evaluate_daily_dataset_quality" not in source


def test_function_returns_bool_not_dict_or_summary_object() -> None:
    result = can_pass_data_quality_gate(_passing_results())

    assert type(result) is bool
    assert not isinstance(result, dict)


def test_no_external_dependency_imports_are_introduced() -> None:
    source = Path("app/data/quality_gate.py").read_text(encoding="utf-8")

    for package_name in ["pandas", "numpy", "yfinance", "requests", "sqlalchemy"]:
        assert f"import {package_name}" not in source
        assert f"from {package_name}" not in source


def test_no_engine_imports_are_introduced() -> None:
    source = Path("app/data/quality_gate.py").read_text(encoding="utf-8")

    assert "from app.engine" not in source
    assert "import app.engine" not in source
