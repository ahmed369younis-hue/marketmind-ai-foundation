from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.domain.data_source_contract import (
    DataGranularity,
    DataSourceContract,
    DataSourceReliability,
    DataSourceType,
)
from app.domain.managed_api_eod_record import (
    ManagedApiEodRecord,
    ManagedApiPriceMode,
)
from app.domain.managed_api_fetch_result import (
    ManagedApiEodFetchResult,
    ManagedApiFetchStatus,
)
from app.domain.managed_api_provider_contract import (
    ManagedApiProviderContract,
    ManagedApiProviderType,
)


CONTRACT_PATH = Path("app/domain/managed_api_fetch_result.py")


def _source(**overrides: object) -> DataSourceContract:
    values = {
        "name": "Managed API Metadata Source",
        "source_type": DataSourceType.REAL,
        "granularity": DataGranularity.DAILY,
        "reliability": DataSourceReliability.VERIFIED_STRUCTURE_ONLY,
        "supports_ohlcv": True,
        "supports_adjusted_prices": True,
        "supports_corporate_actions": True,
        "timezone": "America/New_York",
        "notes": "Metadata-only source for managed API fetch result tests.",
    }
    values.update(overrides)
    return DataSourceContract(**values)


def _provider(**overrides: object) -> ManagedApiProviderContract:
    values = {
        "provider_name": "Example Managed API Provider",
        "provider_type": ManagedApiProviderType.PRIMARY_INSTITUTIONAL,
        "source": _source(),
        "credential_env_var": "MARKETMIND_PROVIDER_API_KEY",
        "supports_eod_ohlcv": True,
        "supports_adjusted_prices": True,
        "supports_corporate_actions": True,
        "supports_us_equities": True,
        "supports_us_etfs": True,
        "supports_fx": False,
        "supports_commodities": False,
        "supports_crypto": False,
        "allowed_first_symbol": "SPY",
        "rate_limit_notes": "Rate limits must be reviewed before future API use.",
        "legal_access_confirmed": True,
        "notes": "Metadata-only provider access contract for future planning.",
    }
    values.update(overrides)
    return ManagedApiProviderContract(**values)


def _record(record_date: date, **overrides: object) -> ManagedApiEodRecord:
    values = {
        "provider_name": "Example Managed API Provider",
        "symbol": "SPY",
        "date": record_date,
        "open": 100.0,
        "high": 105.0,
        "low": 99.0,
        "close": 102.0,
        "volume": 1000000.0,
        "price_mode": ManagedApiPriceMode.RAW,
        "timezone": "America/New_York",
        "adjusted_close": None,
        "corporate_action_adjusted": False,
        "source_timestamp_utc": datetime(2026, 1, 2, 22, 0, tzinfo=timezone.utc),
        "provider_record_id": f"provider-row-{record_date.isoformat()}",
        "notes": "Future provider-returned EOD record contract test.",
    }
    values.update(overrides)
    return ManagedApiEodRecord(**values)


def _date_range() -> tuple[date, date]:
    start_date = date.today() - timedelta(days=5)
    end_date = date.today() - timedelta(days=3)
    return start_date, end_date


def _records() -> list[ManagedApiEodRecord]:
    start_date, end_date = _date_range()
    return [
        _record(start_date),
        _record(start_date + timedelta(days=1)),
        _record(end_date),
    ]


def _success_result(**overrides: object) -> ManagedApiEodFetchResult:
    start_date, end_date = _date_range()
    records = _records()
    values = {
        "provider": _provider(),
        "status": ManagedApiFetchStatus.SUCCESS,
        "symbol": "SPY",
        "start_date": start_date,
        "end_date": end_date,
        "records": records,
        "records_count": len(records),
        "first_record_date": records[0].date,
        "last_record_date": records[-1].date,
        "message": "Managed API EOD fetch result contract test.",
    }
    values.update(overrides)
    return ManagedApiEodFetchResult(**values)


def _failed_result(**overrides: object) -> ManagedApiEodFetchResult:
    start_date, end_date = _date_range()
    values = {
        "provider": _provider(),
        "status": ManagedApiFetchStatus.FAILED,
        "symbol": "SPY",
        "start_date": start_date,
        "end_date": end_date,
        "records": [],
        "records_count": 0,
        "first_record_date": None,
        "last_record_date": None,
        "message": "Managed API EOD fetch failed in a future adapter.",
    }
    values.update(overrides)
    return ManagedApiEodFetchResult(**values)


def test_valid_success_result_passes() -> None:
    result = _success_result()

    assert result.status is ManagedApiFetchStatus.SUCCESS
    assert result.records_count == len(result.records)


def test_valid_failed_result_passes() -> None:
    result = _failed_result()

    assert result.status is ManagedApiFetchStatus.FAILED
    assert result.records == []


def test_invalid_provider_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="provider must be a ManagedApiProviderContract instance",
    ):
        _success_result(provider="provider")


def test_invalid_status_string_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="status must be a valid ManagedApiFetchStatus value",
    ):
        _success_result(status="SUCCESS")


def test_empty_symbol_raises_value_error() -> None:
    with pytest.raises(ValueError, match="symbol must not be empty"):
        _success_result(symbol=" ")


def test_symbol_other_than_provider_allowed_first_symbol_raises_value_error() -> None:
    with pytest.raises(ValueError, match="symbol must equal provider.allowed_first_symbol"):
        _success_result(symbol="QQQ")


def test_future_start_date_raises_value_error() -> None:
    with pytest.raises(ValueError, match="start_date must not be in the future"):
        _success_result(start_date=date.today() + timedelta(days=1))


def test_future_end_date_raises_value_error() -> None:
    with pytest.raises(ValueError, match="end_date must not be in the future"):
        _success_result(end_date=date.today() + timedelta(days=1))


def test_end_date_before_start_date_raises_value_error() -> None:
    start_date, _ = _date_range()

    with pytest.raises(
        ValueError,
        match="end_date must be greater than or equal to start_date",
    ):
        _success_result(start_date=start_date, end_date=start_date - timedelta(days=1))


def test_non_list_records_raises_value_error() -> None:
    with pytest.raises(ValueError, match="records must be a list"):
        _success_result(records="records")


def test_non_managed_api_eod_record_item_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="all records must be ManagedApiEodRecord instances",
    ):
        _success_result(records=["record"], records_count=1)


def test_records_count_not_equal_len_records_raises_value_error() -> None:
    with pytest.raises(ValueError, match="records_count must equal len\\(records\\)"):
        _success_result(records_count=99)


def test_empty_message_raises_value_error() -> None:
    with pytest.raises(ValueError, match="message must not be empty"):
        _success_result(message="")


def test_success_with_empty_records_raises_value_error() -> None:
    with pytest.raises(ValueError, match="records must not be empty when status is SUCCESS"):
        _success_result(records=[], records_count=0)


def test_success_with_records_count_zero_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _success_result(records_count=0)


def test_success_with_first_record_date_none_raises_value_error() -> None:
    with pytest.raises(ValueError, match="first_record_date must not be None"):
        _success_result(first_record_date=None)


def test_success_with_last_record_date_none_raises_value_error() -> None:
    with pytest.raises(ValueError, match="last_record_date must not be None"):
        _success_result(last_record_date=None)


def test_success_with_first_record_date_before_start_date_raises_value_error() -> None:
    start_date, _ = _date_range()

    with pytest.raises(ValueError, match="first_record_date must be >= start_date"):
        _success_result(first_record_date=start_date - timedelta(days=1))


def test_success_with_last_record_date_after_end_date_raises_value_error() -> None:
    _, end_date = _date_range()

    with pytest.raises(ValueError, match="last_record_date must be <= end_date"):
        _success_result(last_record_date=end_date + timedelta(days=1))


def test_success_with_last_record_date_before_first_record_date_raises_value_error() -> None:
    start_date, _ = _date_range()

    with pytest.raises(
        ValueError,
        match="last_record_date must be >= first_record_date",
    ):
        _success_result(
            first_record_date=start_date + timedelta(days=1),
            last_record_date=start_date,
        )


def test_success_with_unsorted_records_raises_value_error() -> None:
    records = _records()

    with pytest.raises(ValueError, match="records must be strictly increasing by date"):
        _success_result(records=[records[1], records[0], records[2]])


def test_success_with_duplicate_dates_raises_value_error() -> None:
    records = _records()
    duplicate = _record(records[0].date)

    with pytest.raises(ValueError, match="duplicate record dates are not allowed"):
        _success_result(records=[records[0], duplicate, records[2]])


def test_success_with_record_symbol_mismatch_raises_value_error() -> None:
    records = _records()
    bad_record = _record(records[1].date, symbol="QQQ")

    with pytest.raises(ValueError, match="record symbol must match fetch result symbol"):
        _success_result(records=[records[0], bad_record, records[2]])


def test_success_with_provider_name_mismatch_raises_value_error() -> None:
    records = _records()
    bad_record = _record(records[1].date, provider_name="Other Provider")

    with pytest.raises(
        ValueError,
        match="record provider_name must match provider.provider_name",
    ):
        _success_result(records=[records[0], bad_record, records[2]])


def test_success_with_record_date_outside_requested_range_raises_value_error() -> None:
    start_date, end_date = _date_range()
    records = [
        _record(start_date - timedelta(days=1)),
        _record(start_date + timedelta(days=1)),
        _record(end_date),
    ]

    with pytest.raises(ValueError, match="record date must be within requested date range"):
        _success_result(records=records)


def test_failed_with_non_empty_records_raises_value_error() -> None:
    records = _records()

    with pytest.raises(ValueError, match="records must be empty when status is FAILED"):
        _failed_result(records=records, records_count=len(records))


def test_failed_with_records_count_greater_than_zero_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _failed_result(records_count=1)


def test_failed_with_first_record_date_not_none_raises_value_error() -> None:
    start_date, _ = _date_range()

    with pytest.raises(
        ValueError,
        match="first_record_date must be None when status is FAILED",
    ):
        _failed_result(first_record_date=start_date)


def test_failed_with_last_record_date_not_none_raises_value_error() -> None:
    _, end_date = _date_range()

    with pytest.raises(
        ValueError,
        match="last_record_date must be None when status is FAILED",
    ):
        _failed_result(last_record_date=end_date)


def test_constructor_requires_explicit_values_and_has_no_defaults() -> None:
    with pytest.raises(TypeError):
        ManagedApiEodFetchResult()


def test_no_os_import_is_introduced() -> None:
    source = CONTRACT_PATH.read_text(encoding="utf-8")

    assert "import os" not in source
    assert "from os" not in source


def test_no_requests_httpx_or_aiohttp_import_is_introduced() -> None:
    source = CONTRACT_PATH.read_text(encoding="utf-8")

    for package_name in ["requests", "httpx", "aiohttp"]:
        assert f"import {package_name}" not in source
        assert f"from {package_name}" not in source


def test_no_forbidden_external_dependency_import_is_introduced() -> None:
    source = CONTRACT_PATH.read_text(encoding="utf-8")

    for package_name in ["pandas", "numpy", "yfinance", "sqlalchemy"]:
        assert f"import {package_name}" not in source
        assert f"from {package_name}" not in source


def test_no_engine_imports_are_introduced() -> None:
    source = CONTRACT_PATH.read_text(encoding="utf-8")

    assert "app.engine" not in source
    assert "from app.engine" not in source
    assert "import app.engine" not in source


def test_no_daily_market_data_import_is_introduced() -> None:
    source = CONTRACT_PATH.read_text(encoding="utf-8")

    assert "DailyMarketData" not in source
    assert "data_contract" not in source


def test_no_app_data_imports_are_introduced() -> None:
    source = CONTRACT_PATH.read_text(encoding="utf-8")

    assert "app.data" not in source
    assert "from app.data" not in source
    assert "import app.data" not in source
