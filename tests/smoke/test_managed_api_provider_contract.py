from pathlib import Path

import pytest

from app.domain.data_source_contract import (
    DataGranularity,
    DataSourceContract,
    DataSourceReliability,
    DataSourceType,
)
from app.domain.managed_api_provider_contract import (
    ManagedApiProviderContract,
    ManagedApiProviderType,
)


CONTRACT_PATH = Path("app/domain/managed_api_provider_contract.py")


def _source(**overrides: object) -> DataSourceContract:
    values = {
        "name": "Managed API Metadata Source",
        "source_type": DataSourceType.REAL,
        "granularity": DataGranularity.DAILY,
        "reliability": DataSourceReliability.VERIFIED_STRUCTURE_ONLY,
        "supports_ohlcv": True,
        "supports_adjusted_prices": True,
        "supports_corporate_actions": True,
        "timezone": "UTC",
        "notes": "Metadata-only source for managed API provider contract tests.",
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


def test_primary_institutional_provider_contract_passes() -> None:
    contract = _provider(provider_type=ManagedApiProviderType.PRIMARY_INSTITUTIONAL)

    assert contract.provider_type is ManagedApiProviderType.PRIMARY_INSTITUTIONAL


def test_secondary_cross_check_provider_contract_passes() -> None:
    contract = _provider(provider_type=ManagedApiProviderType.SECONDARY_CROSS_CHECK)

    assert contract.provider_type is ManagedApiProviderType.SECONDARY_CROSS_CHECK


def test_broker_sourced_provider_contract_passes() -> None:
    contract = _provider(provider_type=ManagedApiProviderType.BROKER_SOURCED)

    assert contract.provider_type is ManagedApiProviderType.BROKER_SOURCED


def test_empty_provider_name_raises_value_error() -> None:
    with pytest.raises(ValueError, match="provider_name must not be empty"):
        _provider(provider_name=" ")


def test_invalid_provider_type_string_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="provider_type must be a valid ManagedApiProviderType value",
    ):
        _provider(provider_type="PRIMARY_INSTITUTIONAL")


def test_non_data_source_contract_source_raises_value_error() -> None:
    with pytest.raises(ValueError, match="source must be a DataSourceContract instance"):
        _provider(source="not a source")


def test_non_real_source_raises_value_error() -> None:
    with pytest.raises(ValueError, match="source.source_type must be REAL"):
        _provider(source=_source(source_type=DataSourceType.MOCK))


def test_non_daily_source_raises_value_error() -> None:
    source = _source()
    object.__setattr__(source, "granularity", "INTRADAY")

    with pytest.raises(ValueError, match="source.granularity must be DAILY"):
        _provider(source=source)


def test_source_without_ohlcv_support_raises_value_error() -> None:
    with pytest.raises(ValueError, match="source.supports_ohlcv must be True"):
        _provider(source=_source(supports_ohlcv=False))


def test_source_reliability_verified_historical_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="source.reliability must not be VERIFIED_HISTORICAL",
    ):
        _provider(source=_source(reliability=DataSourceReliability.VERIFIED_HISTORICAL))


def test_empty_credential_env_var_raises_value_error() -> None:
    with pytest.raises(ValueError, match="credential_env_var must not be empty"):
        _provider(credential_env_var=" ")


def test_lowercase_credential_env_var_raises_value_error() -> None:
    with pytest.raises(ValueError, match="credential_env_var must be uppercase"):
        _provider(credential_env_var="marketmind_api_key")


def test_credential_env_var_with_spaces_raises_value_error() -> None:
    with pytest.raises(ValueError, match="credential_env_var must not contain spaces"):
        _provider(credential_env_var="MARKETMIND API KEY")


def test_non_bool_supports_field_raises_value_error() -> None:
    with pytest.raises(ValueError, match="supports_fx must be bool"):
        _provider(supports_fx="false")


def test_empty_allowed_first_symbol_raises_value_error() -> None:
    with pytest.raises(ValueError, match="allowed_first_symbol must not be empty"):
        _provider(allowed_first_symbol=" ")


def test_allowed_first_symbol_other_than_spy_raises_value_error() -> None:
    with pytest.raises(ValueError, match="allowed_first_symbol must be SPY"):
        _provider(allowed_first_symbol="QQQ")


def test_empty_rate_limit_notes_raises_value_error() -> None:
    with pytest.raises(ValueError, match="rate_limit_notes must not be empty"):
        _provider(rate_limit_notes="")


def test_legal_access_confirmed_false_raises_value_error() -> None:
    with pytest.raises(ValueError, match="legal_access_confirmed must be True"):
        _provider(legal_access_confirmed=False)


def test_non_bool_legal_access_confirmed_raises_value_error() -> None:
    with pytest.raises(ValueError, match="legal_access_confirmed must be bool"):
        _provider(legal_access_confirmed="true")


def test_empty_notes_raises_value_error() -> None:
    with pytest.raises(ValueError, match="notes must not be empty"):
        _provider(notes=" ")


def test_constructor_requires_explicit_values_and_has_no_defaults() -> None:
    with pytest.raises(TypeError):
        ManagedApiProviderContract()


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
