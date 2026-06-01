from datetime import date
from pathlib import Path

import pytest

from app.data.quality_evaluation import evaluate_daily_dataset_quality
from app.domain.data_contract import DailyMarketData
from app.domain.data_ingestion_plan import DataIngestionPlan
from app.domain.data_ingestion_result import (
    DataIngestionResult,
    DataIngestionStatus,
)
from app.domain.data_quality_result import DataQualityCheck, DataQualityResult
from app.domain.data_source_contract import (
    DataGranularity,
    DataSourceContract,
    DataSourceReliability,
    DataSourceType,
)
from app.domain.ingested_daily_dataset import IngestedDailyDataset


def _source() -> DataSourceContract:
    return DataSourceContract(
        name="Eligible Metadata Source",
        source_type=DataSourceType.REAL,
        granularity=DataGranularity.DAILY,
        reliability=DataSourceReliability.VERIFIED_STRUCTURE_ONLY,
        supports_ohlcv=True,
        supports_adjusted_prices=True,
        supports_corporate_actions=True,
        timezone="UTC",
        notes="Metadata-only source for quality evaluation tests.",
    )


def _plan(
    *,
    symbol: str = "AAPL",
    start_date: date = date(2024, 1, 1),
    end_date: date = date(2024, 1, 3),
) -> DataIngestionPlan:
    return DataIngestionPlan(
        source=_source(),
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        use_adjusted_prices=True,
        include_corporate_actions=True,
        purpose="Future daily dataset quality evaluation test.",
    )


def _record(record_date: date, symbol: str = "AAPL") -> DailyMarketData:
    return DailyMarketData(
        date=record_date,
        open=100.0,
        high=102.0,
        low=99.0,
        close=101.0,
        volume=1000.0,
        symbol=symbol,
    )


def _records(symbol: str = "AAPL") -> list[DailyMarketData]:
    return [
        _record(date(2024, 1, 1), symbol),
        _record(date(2024, 1, 2), symbol),
        _record(date(2024, 1, 3), symbol),
    ]


def _success_result(
    plan: DataIngestionPlan,
    *,
    records_count: int = 3,
    first_date: date = date(2024, 1, 1),
    last_date: date = date(2024, 1, 3),
) -> DataIngestionResult:
    return DataIngestionResult(
        plan=plan,
        status=DataIngestionStatus.SUCCESS,
        records_count=records_count,
        first_date=first_date,
        last_date=last_date,
        reliability_after_ingestion=DataSourceReliability.VERIFIED_STRUCTURE_ONLY,
        message="Future ingestion result for quality evaluation tests.",
    )


def _failed_result(plan: DataIngestionPlan) -> DataIngestionResult:
    return DataIngestionResult(
        plan=plan,
        status=DataIngestionStatus.FAILED,
        records_count=0,
        first_date=None,
        last_date=None,
        reliability_after_ingestion=DataSourceReliability.UNVERIFIED,
        message="Future failed ingestion result for quality evaluation tests.",
    )


def _success_batch() -> IngestedDailyDataset:
    plan = _plan()
    return IngestedDailyDataset(
        plan=plan,
        result=_success_result(plan),
        records=_records(),
    )


def _failed_batch() -> IngestedDailyDataset:
    plan = _plan()
    return IngestedDailyDataset(
        plan=plan,
        result=_failed_result(plan),
        records=[],
    )


def _result_for(
    results: list[DataQualityResult],
    check: DataQualityCheck,
) -> DataQualityResult:
    return next(result for result in results if result.check == check)


def test_valid_success_batch_returns_six_results() -> None:
    results = evaluate_daily_dataset_quality(_success_batch())

    assert len(results) == 6


def test_output_order_is_deterministic() -> None:
    results = evaluate_daily_dataset_quality(_success_batch())

    assert [result.check for result in results] == [
        DataQualityCheck.RECORD_COUNT_CHECK,
        DataQualityCheck.DATE_RANGE_COVERAGE_CHECK,
        DataQualityCheck.SYMBOL_CONSISTENCY_CHECK,
        DataQualityCheck.OHLCV_VALIDITY_CHECK,
        DataQualityCheck.DAILY_CONTINUITY_CHECK,
        DataQualityCheck.MISSING_VALUE_CHECK,
    ]


def test_valid_success_batch_returns_all_checks_passed_true() -> None:
    results = evaluate_daily_dataset_quality(_success_batch())

    assert all(result.passed is True for result in results)


def test_valid_failed_batch_returns_six_failed_checks() -> None:
    results = evaluate_daily_dataset_quality(_failed_batch())

    assert len(results) == 6
    assert all(result.passed is False for result in results)
    assert all(result.metric_value == 0.0 for result in results)


def test_non_ingested_daily_dataset_batch_raises_value_error() -> None:
    with pytest.raises(ValueError):
        evaluate_daily_dataset_quality("not a batch")


def test_record_count_metric_value_equals_record_count() -> None:
    results = evaluate_daily_dataset_quality(_success_batch())

    result = _result_for(results, DataQualityCheck.RECORD_COUNT_CHECK)

    assert result.metric_value == 3.0


def test_date_range_coverage_passes_for_matching_first_and_last_dates() -> None:
    results = evaluate_daily_dataset_quality(_success_batch())

    result = _result_for(results, DataQualityCheck.DATE_RANGE_COVERAGE_CHECK)

    assert result.passed is True


def test_symbol_consistency_metric_value_equals_matching_symbol_count() -> None:
    results = evaluate_daily_dataset_quality(_success_batch())

    result = _result_for(results, DataQualityCheck.SYMBOL_CONSISTENCY_CHECK)

    assert result.metric_value == 3.0


def test_ohlcv_validity_metric_value_equals_valid_record_count() -> None:
    results = evaluate_daily_dataset_quality(_success_batch())

    result = _result_for(results, DataQualityCheck.OHLCV_VALIDITY_CHECK)

    assert result.metric_value == 3.0


def test_daily_continuity_metric_value_equals_transitions_checked() -> None:
    results = evaluate_daily_dataset_quality(_success_batch())

    result = _result_for(results, DataQualityCheck.DAILY_CONTINUITY_CHECK)

    assert result.metric_value == 2.0


def test_one_record_success_batch_passes_daily_continuity_with_zero_metric() -> None:
    plan = _plan(end_date=date(2024, 1, 1))
    batch = IngestedDailyDataset(
        plan=plan,
        result=_success_result(
            plan,
            records_count=1,
            first_date=date(2024, 1, 1),
            last_date=date(2024, 1, 1),
        ),
        records=[_record(date(2024, 1, 1))],
    )

    results = evaluate_daily_dataset_quality(batch)
    result = _result_for(results, DataQualityCheck.DAILY_CONTINUITY_CHECK)

    assert result.passed is True
    assert result.metric_value == 0.0


def test_missing_value_metric_value_equals_non_missing_record_count() -> None:
    results = evaluate_daily_dataset_quality(_success_batch())

    result = _result_for(results, DataQualityCheck.MISSING_VALUE_CHECK)

    assert result.metric_value == 3.0


def test_output_returns_data_quality_result_objects_not_raw_dicts() -> None:
    results = evaluate_daily_dataset_quality(_success_batch())

    assert all(isinstance(result, DataQualityResult) for result in results)
    assert all(not isinstance(result, dict) for result in results)


def test_input_batch_and_records_are_not_mutated() -> None:
    batch = _success_batch()
    original_records = list(batch.records)
    original_plan = batch.plan
    original_result = batch.result

    evaluate_daily_dataset_quality(batch)

    assert batch.records == original_records
    assert batch.plan is original_plan
    assert batch.result is original_result


def test_no_external_dependency_imports_are_introduced() -> None:
    source = Path("app/data/quality_evaluation.py").read_text(encoding="utf-8")

    for package_name in ["pandas", "numpy", "yfinance", "requests", "sqlalchemy"]:
        assert f"import {package_name}" not in source
        assert f"from {package_name}" not in source
