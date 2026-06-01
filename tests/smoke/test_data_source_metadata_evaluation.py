from pathlib import Path

from app.data.source_evaluation import (
    evaluate_data_source_metadata,
    is_data_source_eligible_for_ingestion,
)
from app.domain.data_source_contract import (
    DataGranularity,
    DataSourceContract,
    DataSourceReliability,
    DataSourceType,
)
from app.domain.data_source_evaluation_contract import (
    DataSourceEvaluationCheck,
    DataSourceEvaluationResult,
)


EXPECTED_CHECK_ORDER = [
    DataSourceEvaluationCheck.SOURCE_TYPE_CHECK,
    DataSourceEvaluationCheck.GRANULARITY_CHECK,
    DataSourceEvaluationCheck.OHLCV_SUPPORT_CHECK,
    DataSourceEvaluationCheck.ADJUSTED_PRICE_SUPPORT_CHECK,
    DataSourceEvaluationCheck.CORPORATE_ACTIONS_SUPPORT_CHECK,
    DataSourceEvaluationCheck.TIMEZONE_CHECK,
    DataSourceEvaluationCheck.RELIABILITY_CLASSIFICATION_CHECK,
]

SOURCE_FILE = Path("app/data/source_evaluation.py")


def _source(**overrides: object) -> DataSourceContract:
    values = {
        "name": "Metadata Source",
        "source_type": DataSourceType.REAL,
        "granularity": DataGranularity.DAILY,
        "reliability": DataSourceReliability.VERIFIED_STRUCTURE_ONLY,
        "supports_ohlcv": True,
        "supports_adjusted_prices": True,
        "supports_corporate_actions": True,
        "timezone": "UTC",
        "notes": "Metadata contract for tests.",
    }
    values.update(overrides)
    return DataSourceContract(**values)


def _result_by_check(
    results: list[DataSourceEvaluationResult],
    check: DataSourceEvaluationCheck,
) -> DataSourceEvaluationResult:
    return next(result for result in results if result.check == check)


def test_valid_real_daily_source_with_full_support_returns_seven_results() -> None:
    results = evaluate_data_source_metadata(_source())

    assert len(results) == 7
    assert all(result.passed for result in results)
    assert all(
        result.reliability_after_check == DataSourceReliability.VERIFIED_STRUCTURE_ONLY
        for result in results
    )


def test_output_order_is_deterministic() -> None:
    results = evaluate_data_source_metadata(_source())

    assert [result.check for result in results] == EXPECTED_CHECK_ORDER


def test_mock_source_fails_source_type_check() -> None:
    results = evaluate_data_source_metadata(_source(source_type=DataSourceType.MOCK))
    source_type_result = _result_by_check(
        results, DataSourceEvaluationCheck.SOURCE_TYPE_CHECK
    )

    assert source_type_result.passed is False
    assert source_type_result.reliability_after_check == DataSourceReliability.UNVERIFIED


def test_synthetic_source_fails_source_type_check() -> None:
    results = evaluate_data_source_metadata(
        _source(source_type=DataSourceType.SYNTHETIC)
    )
    source_type_result = _result_by_check(
        results, DataSourceEvaluationCheck.SOURCE_TYPE_CHECK
    )

    assert source_type_result.passed is False
    assert source_type_result.reliability_after_check == DataSourceReliability.UNVERIFIED


def test_missing_ohlcv_support_fails_ohlcv_support_check() -> None:
    results = evaluate_data_source_metadata(_source(supports_ohlcv=False))
    ohlcv_result = _result_by_check(
        results, DataSourceEvaluationCheck.OHLCV_SUPPORT_CHECK
    )

    assert ohlcv_result.passed is False
    assert ohlcv_result.reliability_after_check == DataSourceReliability.UNVERIFIED


def test_missing_adjusted_price_support_fails_adjusted_price_check() -> None:
    results = evaluate_data_source_metadata(_source(supports_adjusted_prices=False))
    adjusted_result = _result_by_check(
        results, DataSourceEvaluationCheck.ADJUSTED_PRICE_SUPPORT_CHECK
    )

    assert adjusted_result.passed is False
    assert adjusted_result.reliability_after_check == DataSourceReliability.UNVERIFIED


def test_missing_corporate_actions_support_fails_corporate_actions_check() -> None:
    results = evaluate_data_source_metadata(_source(supports_corporate_actions=False))
    corporate_actions_result = _result_by_check(
        results, DataSourceEvaluationCheck.CORPORATE_ACTIONS_SUPPORT_CHECK
    )

    assert corporate_actions_result.passed is False
    assert (
        corporate_actions_result.reliability_after_check
        == DataSourceReliability.UNVERIFIED
    )


def test_reliability_classification_passes_only_when_all_prior_checks_pass() -> None:
    passing_results = evaluate_data_source_metadata(_source())
    failing_results = evaluate_data_source_metadata(_source(supports_ohlcv=False))

    passing_reliability = _result_by_check(
        passing_results, DataSourceEvaluationCheck.RELIABILITY_CLASSIFICATION_CHECK
    )
    failing_reliability = _result_by_check(
        failing_results, DataSourceEvaluationCheck.RELIABILITY_CLASSIFICATION_CHECK
    )

    assert passing_reliability.passed is True
    assert failing_reliability.passed is False


def test_reliability_classification_fails_for_verified_historical_source() -> None:
    results = evaluate_data_source_metadata(
        _source(reliability=DataSourceReliability.VERIFIED_HISTORICAL)
    )
    reliability_result = _result_by_check(
        results, DataSourceEvaluationCheck.RELIABILITY_CLASSIFICATION_CHECK
    )

    assert reliability_result.passed is False
    assert (
        reliability_result.reliability_after_check == DataSourceReliability.UNVERIFIED
    )


def test_utility_never_returns_verified_historical() -> None:
    results = evaluate_data_source_metadata(
        _source(reliability=DataSourceReliability.VERIFIED_HISTORICAL)
    )

    assert all(
        result.reliability_after_check != DataSourceReliability.VERIFIED_HISTORICAL
        for result in results
    )


def test_output_returns_data_source_evaluation_result_objects_not_dicts() -> None:
    results = evaluate_data_source_metadata(_source())

    assert all(isinstance(result, DataSourceEvaluationResult) for result in results)
    assert not any(isinstance(result, dict) for result in results)


def test_input_source_is_not_mutated() -> None:
    source = _source()
    original_source = _source()

    evaluate_data_source_metadata(source)

    assert source == original_source


def test_no_external_dependency_imports_are_introduced() -> None:
    content = SOURCE_FILE.read_text(encoding="utf-8")

    for package_name in ["pandas", "numpy", "yfinance", "requests", "sqlalchemy"]:
        assert f"import {package_name}" not in content
        assert f"from {package_name}" not in content


def test_valid_real_daily_source_is_eligible_for_future_ingestion_planning() -> None:
    assert is_data_source_eligible_for_ingestion(_source()) is True


def test_mock_source_is_not_eligible_for_future_ingestion_planning() -> None:
    assert (
        is_data_source_eligible_for_ingestion(
            _source(source_type=DataSourceType.MOCK)
        )
        is False
    )


def test_synthetic_source_is_not_eligible_for_future_ingestion_planning() -> None:
    assert (
        is_data_source_eligible_for_ingestion(
            _source(source_type=DataSourceType.SYNTHETIC)
        )
        is False
    )


def test_missing_ohlcv_support_is_not_eligible_for_future_ingestion_planning() -> None:
    assert is_data_source_eligible_for_ingestion(_source(supports_ohlcv=False)) is False


def test_missing_adjusted_price_support_is_not_eligible_for_planning() -> None:
    assert (
        is_data_source_eligible_for_ingestion(
            _source(supports_adjusted_prices=False)
        )
        is False
    )


def test_missing_corporate_actions_support_is_not_eligible_for_planning() -> None:
    assert (
        is_data_source_eligible_for_ingestion(
            _source(supports_corporate_actions=False)
        )
        is False
    )


def test_verified_historical_source_is_not_eligible_at_metadata_stage() -> None:
    assert (
        is_data_source_eligible_for_ingestion(
            _source(reliability=DataSourceReliability.VERIFIED_HISTORICAL)
        )
        is False
    )


def test_unverified_source_is_not_eligible_for_future_ingestion_planning() -> None:
    assert (
        is_data_source_eligible_for_ingestion(
            _source(reliability=DataSourceReliability.UNVERIFIED)
        )
        is False
    )


def test_eligibility_gate_does_not_mutate_input_source() -> None:
    source = _source()
    original_source = _source()

    is_data_source_eligible_for_ingestion(source)

    assert source == original_source


def test_eligibility_gate_adds_no_external_dependency_imports() -> None:
    content = SOURCE_FILE.read_text(encoding="utf-8")

    for package_name in ["pandas", "numpy", "yfinance", "requests", "sqlalchemy"]:
        assert f"import {package_name}" not in content
        assert f"from {package_name}" not in content
