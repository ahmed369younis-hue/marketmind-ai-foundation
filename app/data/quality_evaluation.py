"""Daily dataset quality evaluation utilities."""

from datetime import timedelta

from app.domain.data_ingestion_result import DataIngestionStatus
from app.domain.data_quality_result import DataQualityCheck, DataQualityResult
from app.domain.ingested_daily_dataset import IngestedDailyDataset


def evaluate_daily_dataset_quality(
    batch: IngestedDailyDataset,
) -> list[DataQualityResult]:
    """Return audit-only quality results for an already constructed batch."""

    if not isinstance(batch, IngestedDailyDataset):
        raise ValueError("batch must be an IngestedDailyDataset instance")

    if batch.result.status == DataIngestionStatus.FAILED:
        return _failed_ingestion_quality_results()

    records = batch.records
    return [
        _record_count_result(batch),
        _date_range_coverage_result(batch),
        _symbol_consistency_result(batch),
        _ohlcv_validity_result(batch),
        _daily_continuity_result(batch),
        _missing_value_result(records),
    ]


def _failed_ingestion_quality_results() -> list[DataQualityResult]:
    details = "Quality cannot pass for a failed ingestion result."
    return [
        DataQualityResult(
            check=DataQualityCheck.RECORD_COUNT_CHECK,
            passed=False,
            metric_value=0.0,
            details=details,
        ),
        DataQualityResult(
            check=DataQualityCheck.DATE_RANGE_COVERAGE_CHECK,
            passed=False,
            metric_value=0.0,
            details=details,
        ),
        DataQualityResult(
            check=DataQualityCheck.SYMBOL_CONSISTENCY_CHECK,
            passed=False,
            metric_value=0.0,
            details=details,
        ),
        DataQualityResult(
            check=DataQualityCheck.OHLCV_VALIDITY_CHECK,
            passed=False,
            metric_value=0.0,
            details=details,
        ),
        DataQualityResult(
            check=DataQualityCheck.DAILY_CONTINUITY_CHECK,
            passed=False,
            metric_value=0.0,
            details=details,
        ),
        DataQualityResult(
            check=DataQualityCheck.MISSING_VALUE_CHECK,
            passed=False,
            metric_value=0.0,
            details=details,
        ),
    ]


def _record_count_result(batch: IngestedDailyDataset) -> DataQualityResult:
    actual_count = len(batch.records)
    expected_count = batch.result.records_count
    return DataQualityResult(
        check=DataQualityCheck.RECORD_COUNT_CHECK,
        passed=actual_count == expected_count,
        metric_value=float(actual_count),
        details=f"Actual record count is {actual_count}; expected record count is {expected_count}.",
    )


def _date_range_coverage_result(batch: IngestedDailyDataset) -> DataQualityResult:
    first_record_date = batch.records[0].date
    last_record_date = batch.records[-1].date
    return DataQualityResult(
        check=DataQualityCheck.DATE_RANGE_COVERAGE_CHECK,
        passed=(
            first_record_date == batch.result.first_date
            and last_record_date == batch.result.last_date
        ),
        metric_value=float(len(batch.records)),
        details=f"First record date is {first_record_date}; last record date is {last_record_date}.",
    )


def _symbol_consistency_result(batch: IngestedDailyDataset) -> DataQualityResult:
    matching_count = sum(
        1 for record in batch.records if record.symbol == batch.plan.symbol
    )
    return DataQualityResult(
        check=DataQualityCheck.SYMBOL_CONSISTENCY_CHECK,
        passed=matching_count == len(batch.records),
        metric_value=float(matching_count),
        details=f"Expected symbol is {batch.plan.symbol}.",
    )


def _ohlcv_validity_result(batch: IngestedDailyDataset) -> DataQualityResult:
    valid_count = sum(1 for record in batch.records if _has_valid_ohlcv(record))
    return DataQualityResult(
        check=DataQualityCheck.OHLCV_VALIDITY_CHECK,
        passed=valid_count == len(batch.records),
        metric_value=float(valid_count),
        details=f"Valid OHLCV record count is {valid_count}.",
    )


def _has_valid_ohlcv(record: object) -> bool:
    return (
        record.open > 0
        and record.high > 0
        and record.low > 0
        and record.close > 0
        and record.volume >= 0
        and record.high >= record.low
        and record.high >= record.open
        and record.high >= record.close
        and record.low <= record.open
        and record.low <= record.close
    )


def _daily_continuity_result(batch: IngestedDailyDataset) -> DataQualityResult:
    transitions_checked = max(len(batch.records) - 1, 0)
    passed = all(
        current_record.date == previous_record.date + timedelta(days=1)
        for previous_record, current_record in zip(batch.records, batch.records[1:])
    )
    return DataQualityResult(
        check=DataQualityCheck.DAILY_CONTINUITY_CHECK,
        passed=passed,
        metric_value=float(transitions_checked),
        details=f"Continuity transitions checked: {transitions_checked}.",
    )


def _missing_value_result(records: list[object]) -> DataQualityResult:
    non_missing_count = sum(1 for record in records if _has_no_missing_values(record))
    return DataQualityResult(
        check=DataQualityCheck.MISSING_VALUE_CHECK,
        passed=non_missing_count == len(records),
        metric_value=float(non_missing_count),
        details=f"Non-missing record count is {non_missing_count}.",
    )


def _has_no_missing_values(record: object) -> bool:
    return all(
        getattr(record, field_name) is not None
        for field_name in ("date", "open", "high", "low", "close", "volume", "symbol")
    )
