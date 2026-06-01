from pathlib import Path

import pytest

from app.domain.data_source_contract import (
    DataGranularity,
    DataSourceContract,
    DataSourceReliability,
    DataSourceType,
)
from app.domain.managed_api_fetch_result import ManagedApiEodFetchResult
from app.domain.managed_api_provider_adapter_port import (
    ManagedApiProviderAdapterCapability,
    ManagedApiProviderAdapterPort,
)
from app.domain.managed_api_provider_contract import (
    ManagedApiProviderContract,
    ManagedApiProviderType,
)


CONTRACT_PATH = Path("app/domain/managed_api_provider_adapter_port.py")


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
        "notes": "Metadata-only source for managed API adapter port tests.",
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


def _capability(**overrides: object) -> ManagedApiProviderAdapterCapability:
    values = {
        "provider": _provider(),
        "adapter_name": "Example Managed API Adapter Port",
        "supports_fetch_eod": True,
        "supports_raw_prices": True,
        "supports_adjusted_prices": True,
        "supports_single_symbol_fetch": True,
        "supports_bulk_fetch": False,
        "notes": "Provider-neutral adapter port capability contract test.",
    }
    values.update(overrides)
    return ManagedApiProviderAdapterCapability(**values)


def test_valid_capability_passes() -> None:
    capability = _capability()

    assert capability.supports_fetch_eod is True
    assert capability.supports_bulk_fetch is False


def test_empty_adapter_name_raises_value_error() -> None:
    with pytest.raises(ValueError, match="adapter_name must not be empty"):
        _capability(adapter_name=" ")


def test_invalid_provider_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="provider must be a ManagedApiProviderContract instance",
    ):
        _capability(provider="provider")


def test_non_bool_supports_fetch_eod_raises_value_error() -> None:
    with pytest.raises(ValueError, match="supports_fetch_eod must be bool"):
        _capability(supports_fetch_eod="true")


def test_non_bool_supports_raw_prices_raises_value_error() -> None:
    with pytest.raises(ValueError, match="supports_raw_prices must be bool"):
        _capability(supports_raw_prices="true")


def test_non_bool_supports_adjusted_prices_raises_value_error() -> None:
    with pytest.raises(ValueError, match="supports_adjusted_prices must be bool"):
        _capability(supports_adjusted_prices="true")


def test_non_bool_supports_single_symbol_fetch_raises_value_error() -> None:
    with pytest.raises(ValueError, match="supports_single_symbol_fetch must be bool"):
        _capability(supports_single_symbol_fetch="true")


def test_non_bool_supports_bulk_fetch_raises_value_error() -> None:
    with pytest.raises(ValueError, match="supports_bulk_fetch must be bool"):
        _capability(supports_bulk_fetch="false")


def test_supports_fetch_eod_false_raises_value_error() -> None:
    with pytest.raises(ValueError, match="supports_fetch_eod must be True"):
        _capability(supports_fetch_eod=False)


def test_supports_single_symbol_fetch_false_raises_value_error() -> None:
    with pytest.raises(ValueError, match="supports_single_symbol_fetch must be True"):
        _capability(supports_single_symbol_fetch=False)


def test_supports_bulk_fetch_true_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="supports_bulk_fetch must be False for the first implementation policy",
    ):
        _capability(supports_bulk_fetch=True)


def test_supports_raw_prices_false_raises_value_error() -> None:
    with pytest.raises(ValueError, match="supports_raw_prices must be True"):
        _capability(supports_raw_prices=False)


def test_supports_adjusted_prices_true_when_provider_does_not_support_adjusted_prices_raises_value_error() -> None:
    provider = _provider(supports_adjusted_prices=False)

    with pytest.raises(
        ValueError,
        match=(
            "provider.supports_adjusted_prices must be True when "
            "supports_adjusted_prices is True"
        ),
    ):
        _capability(provider=provider, supports_adjusted_prices=True)


def test_empty_notes_raises_value_error() -> None:
    with pytest.raises(ValueError, match="notes must not be empty"):
        _capability(notes="")


def test_constructor_requires_explicit_values_and_has_no_defaults() -> None:
    with pytest.raises(TypeError):
        ManagedApiProviderAdapterCapability()


def test_managed_api_provider_adapter_port_is_a_protocol() -> None:
    assert getattr(ManagedApiProviderAdapterPort, "_is_protocol", False) is True


def test_protocol_declares_fetch_eod() -> None:
    assert "fetch_eod" in ManagedApiProviderAdapterPort.__dict__


def test_fetch_eod_return_annotation_is_managed_api_eod_fetch_result() -> None:
    annotation = ManagedApiProviderAdapterPort.fetch_eod.__annotations__["return"]

    assert annotation is ManagedApiEodFetchResult


def test_no_os_import_is_introduced() -> None:
    source = CONTRACT_PATH.read_text(encoding="utf-8")

    assert "import os" not in source
    assert "from os" not in source


def test_no_dotenv_or_python_dotenv_import_is_introduced() -> None:
    source = CONTRACT_PATH.read_text(encoding="utf-8")

    assert "dotenv" not in source
    assert "python-dotenv" not in source


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
