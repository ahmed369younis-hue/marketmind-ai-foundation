from datetime import date, timedelta
from pathlib import Path

import pytest

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
        notes="Metadata-only source for ingestion result tests.",
    )


def _plan() -> DataIngestionPlan:
    return DataIngestionPlan(
        source=_source(),
        symbol="AAPL",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 10),
        use_adjusted_prices=True,
        include_corporate_actions=True,
        purpose="Future ingestion result test.",
    )


def _success_result(**overrides: object) -> DataIngestionResult:
    values = {
        "plan": _plan(),
        "status": DataIngestionStatus.SUCCESS,
        "records_count": 10,
        "first_date": date(2024, 1, 1),
        "last_date": date(2024, 1, 10),
        "reliability_after_ingestion": DataSourceReliability.VERIFIED_STRUCTURE_ONLY,
        "message": "Future ingestion result contract success.",
    }
    values.update(overrides)
    return DataIngestionResult(**values)


def _failed_result(**overrides: object) -> DataIngestionResult:
    values = {
        "plan": _plan(),
        "status": DataIngestionStatus.FAILED,
        "records_count": 0,
        "first_date": None,
        "last_date": None,
        "reliability_after_ingestion": DataSourceReliability.UNVERIFIED,
        "message": "Future ingestion result contract failure.",
    }
    values.update(overrides)
    return DataIngestionResult(**values)


def test_valid_success_result_passes() -> None:
    result = _success_result()

    assert isinstance(result, DataIngestionResult)


def test_valid_failed_result_passes() -> None:
    result = _failed_result()

    assert isinstance(result, DataIngestionResult)


def test_non_data_ingestion_plan_plan_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _success_result(plan="not a plan")


def test_invalid_status_string_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _success_result(status="SUCCESS")


def test_records_count_below_zero_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _success_result(records_count=-1)


def test_success_with_zero_records_count_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _success_result(records_count=0)


def test_success_with_first_date_none_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _success_result(first_date=None)


def test_success_with_last_date_none_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _success_result(last_date=None)


def test_success_with_future_first_date_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _success_result(first_date=date.today() + timedelta(days=1))


def test_success_with_future_last_date_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _success_result(last_date=date.today() + timedelta(days=1))


def test_success_with_last_date_before_first_date_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _success_result(first_date=date(2024, 1, 5), last_date=date(2024, 1, 4))


def test_success_with_first_date_before_plan_start_date_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _success_result(first_date=date(2023, 12, 31), last_date=date(2024, 1, 4))


def test_success_with_last_date_after_plan_end_date_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _success_result(last_date=date(2024, 1, 11))


def test_failed_with_records_count_above_zero_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _failed_result(records_count=1)


def test_failed_with_first_date_not_none_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _failed_result(first_date=date(2024, 1, 1))


def test_failed_with_last_date_not_none_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _failed_result(last_date=date(2024, 1, 1))


def test_invalid_reliability_after_ingestion_string_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _success_result(reliability_after_ingestion="VERIFIED_STRUCTURE_ONLY")


def test_verified_historical_reliability_after_ingestion_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _success_result(
            reliability_after_ingestion=DataSourceReliability.VERIFIED_HISTORICAL
        )


def test_empty_message_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _success_result(message=" ")


def test_constructor_requires_explicit_values_and_has_no_defaults() -> None:
    with pytest.raises(TypeError):
        DataIngestionResult()


def test_no_external_dependency_imports_are_introduced() -> None:
    source = Path("app/domain/data_ingestion_result.py").read_text(encoding="utf-8")

    for package_name in ["pandas", "numpy", "yfinance", "requests", "sqlalchemy"]:
        assert f"import {package_name}" not in source
        assert f"from {package_name}" not in source
