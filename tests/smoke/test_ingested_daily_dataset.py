from datetime import date
from pathlib import Path

import pytest

from app.domain.data_contract import DailyMarketData
from app.domain.data_ingestion_plan import DataIngestionPlan
from app.domain.data_ingestion_result import (
    DataIngestionResult,
    DataIngestionStatus,
)
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
        notes="Metadata-only source for ingested batch tests.",
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
        purpose="Future ingested dataset batch test.",
    )


def _record(record_date: date, symbol: str = "AAPL") -> DailyMarketData:
    return DailyMarketData(
        date=record_date,
        open=100.0,
        high=101.0,
        low=99.0,
        close=100.5,
        volume=1000.0,
        symbol=symbol,
    )


def _records(symbol: str = "AAPL") -> list[DailyMarketData]:
    return [
        _record(date(2024, 1, 1), symbol),
        _record(date(2024, 1, 2), symbol),
        _record(date(2024, 1, 3), symbol),
    ]


def _success_result(plan: DataIngestionPlan, **overrides: object) -> DataIngestionResult:
    values = {
        "plan": plan,
        "status": DataIngestionStatus.SUCCESS,
        "records_count": 3,
        "first_date": date(2024, 1, 1),
        "last_date": date(2024, 1, 3),
        "reliability_after_ingestion": DataSourceReliability.VERIFIED_STRUCTURE_ONLY,
        "message": "Future ingestion batch contract success.",
    }
    values.update(overrides)
    return DataIngestionResult(**values)


def _failed_result(plan: DataIngestionPlan) -> DataIngestionResult:
    return DataIngestionResult(
        plan=plan,
        status=DataIngestionStatus.FAILED,
        records_count=0,
        first_date=None,
        last_date=None,
        reliability_after_ingestion=DataSourceReliability.UNVERIFIED,
        message="Future ingestion batch contract failure.",
    )


def test_valid_success_batch_passes() -> None:
    plan = _plan()
    result = _success_result(plan)
    batch = IngestedDailyDataset(plan=plan, result=result, records=_records())

    assert isinstance(batch, IngestedDailyDataset)


def test_valid_failed_batch_with_empty_records_passes() -> None:
    plan = _plan()
    result = _failed_result(plan)
    batch = IngestedDailyDataset(plan=plan, result=result, records=[])

    assert isinstance(batch, IngestedDailyDataset)


def test_non_data_ingestion_plan_plan_raises_value_error() -> None:
    plan = _plan()
    result = _success_result(plan)

    with pytest.raises(ValueError):
        IngestedDailyDataset(plan="not a plan", result=result, records=_records())


def test_non_data_ingestion_result_result_raises_value_error() -> None:
    plan = _plan()

    with pytest.raises(ValueError):
        IngestedDailyDataset(plan=plan, result="not a result", records=_records())


def test_result_linked_to_different_plan_raises_value_error() -> None:
    plan = _plan()
    different_plan = _plan()
    result = _success_result(different_plan)

    with pytest.raises(ValueError):
        IngestedDailyDataset(plan=plan, result=result, records=_records())


def test_records_not_list_raises_value_error() -> None:
    plan = _plan()
    result = _success_result(plan)

    with pytest.raises(ValueError):
        IngestedDailyDataset(plan=plan, result=result, records=tuple(_records()))


def test_failed_with_non_empty_records_raises_value_error() -> None:
    plan = _plan()
    result = _failed_result(plan)

    with pytest.raises(ValueError):
        IngestedDailyDataset(plan=plan, result=result, records=_records())


def test_success_with_empty_records_raises_value_error() -> None:
    plan = _plan()
    result = _success_result(plan)

    with pytest.raises(ValueError):
        IngestedDailyDataset(plan=plan, result=result, records=[])


def test_success_with_records_count_mismatch_raises_value_error() -> None:
    plan = _plan()
    result = _success_result(plan, records_count=2)

    with pytest.raises(ValueError):
        IngestedDailyDataset(plan=plan, result=result, records=_records())


def test_success_with_invalid_dataset_raises_value_error() -> None:
    plan = _plan()
    result = _success_result(plan)
    records = [
        _record(date(2024, 1, 1)),
        _record(date(2024, 1, 3)),
        _record(date(2024, 1, 4)),
    ]

    with pytest.raises(ValueError):
        IngestedDailyDataset(plan=plan, result=result, records=records)


def test_success_with_record_symbol_mismatch_raises_value_error() -> None:
    plan = _plan(symbol="MSFT")
    result = _success_result(plan)

    with pytest.raises(ValueError):
        IngestedDailyDataset(plan=plan, result=result, records=_records("AAPL"))


def test_success_with_first_record_date_not_matching_result_raises_value_error() -> None:
    plan = _plan(start_date=date(2024, 1, 2), end_date=date(2024, 1, 4))
    result = _success_result(
        plan,
        first_date=date(2024, 1, 3),
        last_date=date(2024, 1, 4),
    )
    records = [
        _record(date(2024, 1, 2)),
        _record(date(2024, 1, 3)),
        _record(date(2024, 1, 4)),
    ]

    with pytest.raises(ValueError):
        IngestedDailyDataset(plan=plan, result=result, records=records)


def test_success_with_last_record_date_not_matching_result_raises_value_error() -> None:
    plan = _plan(start_date=date(2024, 1, 2), end_date=date(2024, 1, 4))
    result = _success_result(
        plan,
        first_date=date(2024, 1, 2),
        last_date=date(2024, 1, 3),
    )
    records = [
        _record(date(2024, 1, 2)),
        _record(date(2024, 1, 3)),
        _record(date(2024, 1, 4)),
    ]

    with pytest.raises(ValueError):
        IngestedDailyDataset(plan=plan, result=result, records=records)


def test_success_with_first_record_date_before_plan_start_raises_value_error() -> None:
    plan = _plan(start_date=date(2024, 1, 2), end_date=date(2024, 1, 4))
    result = _success_result(
        plan,
        first_date=date(2024, 1, 2),
        last_date=date(2024, 1, 4),
    )
    records = [
        _record(date(2024, 1, 1)),
        _record(date(2024, 1, 2)),
        _record(date(2024, 1, 3)),
    ]

    with pytest.raises(ValueError):
        IngestedDailyDataset(plan=plan, result=result, records=records)


def test_success_with_last_record_date_after_plan_end_raises_value_error() -> None:
    plan = _plan(start_date=date(2024, 1, 1), end_date=date(2024, 1, 2))
    result = _success_result(
        plan,
        first_date=date(2024, 1, 1),
        last_date=date(2024, 1, 2),
    )

    with pytest.raises(ValueError):
        IngestedDailyDataset(plan=plan, result=result, records=_records())


def test_constructor_requires_explicit_values_and_has_no_defaults() -> None:
    with pytest.raises(TypeError):
        IngestedDailyDataset()


def test_no_external_dependency_imports_are_introduced() -> None:
    source = Path("app/domain/ingested_daily_dataset.py").read_text(encoding="utf-8")

    for package_name in ["pandas", "numpy", "yfinance", "requests", "sqlalchemy"]:
        assert f"import {package_name}" not in source
        assert f"from {package_name}" not in source
