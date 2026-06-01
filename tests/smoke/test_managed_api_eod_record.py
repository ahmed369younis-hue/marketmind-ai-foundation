from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.domain.managed_api_eod_record import (
    ManagedApiEodRecord,
    ManagedApiPriceMode,
)


CONTRACT_PATH = Path("app/domain/managed_api_eod_record.py")


def _record(**overrides: object) -> ManagedApiEodRecord:
    values = {
        "provider_name": "Example Managed API Provider",
        "symbol": "SPY",
        "date": date.today() - timedelta(days=1),
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
        "provider_record_id": "provider-row-1",
        "notes": "Future provider-returned EOD record contract test.",
    }
    values.update(overrides)
    return ManagedApiEodRecord(**values)


def test_valid_raw_record_passes_with_adjusted_close_none() -> None:
    record = _record(price_mode=ManagedApiPriceMode.RAW, adjusted_close=None)

    assert record.price_mode is ManagedApiPriceMode.RAW
    assert record.adjusted_close is None


def test_valid_raw_record_passes_with_adjusted_close_provided() -> None:
    record = _record(price_mode=ManagedApiPriceMode.RAW, adjusted_close=101.5)

    assert record.adjusted_close == 101.5


def test_valid_adjusted_record_passes() -> None:
    record = _record(
        price_mode=ManagedApiPriceMode.ADJUSTED,
        adjusted_close=101.5,
        corporate_action_adjusted=True,
    )

    assert record.price_mode is ManagedApiPriceMode.ADJUSTED
    assert record.corporate_action_adjusted is True


def test_empty_provider_name_raises_value_error() -> None:
    with pytest.raises(ValueError, match="provider_name must not be empty"):
        _record(provider_name=" ")


def test_empty_symbol_raises_value_error() -> None:
    with pytest.raises(ValueError, match="symbol must not be empty"):
        _record(symbol="")


def test_future_date_raises_value_error() -> None:
    with pytest.raises(ValueError, match="date must not be in the future"):
        _record(date=date.today() + timedelta(days=1))


@pytest.mark.parametrize(
    ("field_name", "message"),
    [
        ("open", "open must be > 0"),
        ("high", "high must be > 0"),
        ("low", "low must be > 0"),
        ("close", "close must be > 0"),
    ],
)
def test_invalid_ohlc_values_raise_value_error(
    field_name: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        _record(**{field_name: 0.0})


def test_negative_volume_raises_value_error() -> None:
    with pytest.raises(ValueError, match="volume must be >= 0"):
        _record(volume=-1.0)


def test_high_below_low_raises_value_error() -> None:
    with pytest.raises(ValueError, match="high must be >= low"):
        _record(open=9.5, high=9.0, low=10.0, close=9.5)


def test_high_below_open_raises_value_error() -> None:
    with pytest.raises(ValueError, match="high must be >= open"):
        _record(open=11.0, high=10.0, low=9.0, close=10.0)


def test_high_below_close_raises_value_error() -> None:
    with pytest.raises(ValueError, match="high must be >= close"):
        _record(open=9.5, high=10.0, low=9.0, close=11.0)


def test_low_above_open_raises_value_error() -> None:
    with pytest.raises(ValueError, match="low must be <= open"):
        _record(open=9.0, high=11.0, low=10.0, close=10.5)


def test_low_above_close_raises_value_error() -> None:
    with pytest.raises(ValueError, match="low must be <= close"):
        _record(open=10.5, high=11.0, low=10.0, close=9.0)


def test_invalid_price_mode_string_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="price_mode must be a valid ManagedApiPriceMode value",
    ):
        _record(price_mode="RAW")


def test_empty_timezone_raises_value_error() -> None:
    with pytest.raises(ValueError, match="timezone must not be empty"):
        _record(timezone=" ")


def test_adjusted_close_none_with_adjusted_mode_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="adjusted_close must be provided when price_mode is ADJUSTED",
    ):
        _record(
            price_mode=ManagedApiPriceMode.ADJUSTED,
            adjusted_close=None,
            corporate_action_adjusted=True,
        )


def test_adjusted_close_non_positive_raises_value_error() -> None:
    with pytest.raises(ValueError, match="adjusted_close must be > 0"):
        _record(adjusted_close=0.0)


def test_corporate_action_adjusted_non_bool_raises_value_error() -> None:
    with pytest.raises(ValueError, match="corporate_action_adjusted must be bool"):
        _record(corporate_action_adjusted="false")


def test_adjusted_mode_with_corporate_action_adjusted_false_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="corporate_action_adjusted must be True when price_mode is ADJUSTED",
    ):
        _record(
            price_mode=ManagedApiPriceMode.ADJUSTED,
            adjusted_close=101.5,
            corporate_action_adjusted=False,
        )


def test_source_timestamp_non_utc_timezone_aware_datetime_raises_value_error() -> None:
    non_utc = datetime(2026, 1, 2, 22, 0, tzinfo=timezone(timedelta(hours=2)))

    with pytest.raises(
        ValueError,
        match="source_timestamp_utc must be timezone-aware UTC",
    ):
        _record(source_timestamp_utc=non_utc)


def test_source_timestamp_naive_datetime_raises_value_error() -> None:
    naive = datetime(2026, 1, 2, 22, 0)

    with pytest.raises(
        ValueError,
        match="source_timestamp_utc must be timezone-aware UTC",
    ):
        _record(source_timestamp_utc=naive)


def test_empty_provider_record_id_raises_value_error_when_provided() -> None:
    with pytest.raises(ValueError, match="provider_record_id must not be empty"):
        _record(provider_record_id=" ")


def test_empty_notes_raises_value_error() -> None:
    with pytest.raises(ValueError, match="notes must not be empty"):
        _record(notes="")


def test_constructor_requires_explicit_values_and_has_no_defaults() -> None:
    with pytest.raises(TypeError):
        ManagedApiEodRecord()


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
