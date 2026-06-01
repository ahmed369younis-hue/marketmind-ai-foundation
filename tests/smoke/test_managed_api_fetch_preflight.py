from datetime import date, timedelta
from pathlib import Path

import pytest

from app.data.managed_api_fetch_preflight import (
    can_execute_managed_api_fetch_preflight,
)
from app.domain.data_source_contract import (
    DataGranularity,
    DataSourceContract,
    DataSourceReliability,
    DataSourceType,
)
from app.domain.managed_api_credential_contract import (
    ManagedApiCredentialAccessResult,
    ManagedApiCredentialStatus,
)
from app.domain.managed_api_fetch_request import (
    ManagedApiEodFetchRequest,
    ManagedApiFetchPricePreference,
)
from app.domain.managed_api_provider_adapter_port import (
    ManagedApiProviderAdapterCapability,
)
from app.domain.managed_api_provider_contract import (
    ManagedApiProviderContract,
    ManagedApiProviderType,
)


PREFLIGHT_PATH = Path("app/data/managed_api_fetch_preflight.py")


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
        "notes": "Metadata-only source for managed API preflight tests.",
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


def _credential_result(
    provider: ManagedApiProviderContract,
    **overrides: object,
) -> ManagedApiCredentialAccessResult:
    values = {
        "provider": provider,
        "status": ManagedApiCredentialStatus.AVAILABLE,
        "credential_env_var": provider.credential_env_var,
        "credential_present": True,
        "credential_fingerprint": "key-ab12",
        "message": "Future credential access result contract test.",
    }
    values.update(overrides)
    return ManagedApiCredentialAccessResult(**values)


def _date_range() -> tuple[date, date]:
    start_date = date.today() - timedelta(days=5)
    end_date = date.today() - timedelta(days=1)
    return start_date, end_date


def _request(
    provider: ManagedApiProviderContract | None = None,
    **overrides: object,
) -> ManagedApiEodFetchRequest:
    selected_provider = provider or _provider()
    credential_access = overrides.pop(
        "credential_access",
        _credential_result(selected_provider),
    )
    start_date, end_date = _date_range()
    values = {
        "provider": selected_provider,
        "credential_access": credential_access,
        "symbol": selected_provider.allowed_first_symbol,
        "start_date": start_date,
        "end_date": end_date,
        "price_preference": ManagedApiFetchPricePreference.RAW,
        "timezone": selected_provider.source.timezone,
        "purpose": "Future managed API EOD fetch request preflight test.",
    }
    values.update(overrides)
    return ManagedApiEodFetchRequest(**values)


def _capability(
    provider: ManagedApiProviderContract | None = None,
    **overrides: object,
) -> ManagedApiProviderAdapterCapability:
    selected_provider = provider or _provider()
    values = {
        "provider": selected_provider,
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


def _request_snapshot(request: ManagedApiEodFetchRequest) -> tuple[object, ...]:
    return (
        request.provider,
        request.credential_access,
        request.symbol,
        request.start_date,
        request.end_date,
        request.price_preference,
        request.timezone,
        request.purpose,
    )


def _capability_snapshot(
    capability: ManagedApiProviderAdapterCapability,
) -> tuple[object, ...]:
    return (
        capability.provider,
        capability.adapter_name,
        capability.supports_fetch_eod,
        capability.supports_raw_prices,
        capability.supports_adjusted_prices,
        capability.supports_single_symbol_fetch,
        capability.supports_bulk_fetch,
        capability.notes,
    )


def test_valid_raw_request_and_compatible_capability_returns_true() -> None:
    provider = _provider()
    request = _request(provider=provider)
    capability = _capability(provider=provider)

    assert can_execute_managed_api_fetch_preflight(request, capability) is True


def test_valid_adjusted_request_and_compatible_capability_returns_true() -> None:
    provider = _provider()
    request = _request(
        provider=provider,
        price_preference=ManagedApiFetchPricePreference.ADJUSTED,
    )
    capability = _capability(provider=provider)

    assert can_execute_managed_api_fetch_preflight(request, capability) is True


def test_invalid_request_type_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="request must be a ManagedApiEodFetchRequest instance",
    ):
        can_execute_managed_api_fetch_preflight("request", _capability())


def test_invalid_capability_type_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="capability must be a ManagedApiProviderAdapterCapability instance",
    ):
        can_execute_managed_api_fetch_preflight(_request(), "capability")


def test_provider_object_mismatch_returns_false() -> None:
    request = _request(provider=_provider(provider_name="Request Provider"))
    capability = _capability(provider=_provider(provider_name="Capability Provider"))

    assert can_execute_managed_api_fetch_preflight(request, capability) is False


def test_supports_fetch_eod_false_returns_false() -> None:
    provider = _provider()
    request = _request(provider=provider)
    capability = _capability(provider=provider)
    object.__setattr__(capability, "supports_fetch_eod", False)

    assert can_execute_managed_api_fetch_preflight(request, capability) is False


def test_supports_single_symbol_fetch_false_returns_false() -> None:
    provider = _provider()
    request = _request(provider=provider)
    capability = _capability(provider=provider)
    object.__setattr__(capability, "supports_single_symbol_fetch", False)

    assert can_execute_managed_api_fetch_preflight(request, capability) is False


def test_supports_bulk_fetch_true_returns_false() -> None:
    provider = _provider()
    request = _request(provider=provider)
    capability = _capability(provider=provider)
    object.__setattr__(capability, "supports_bulk_fetch", True)

    assert can_execute_managed_api_fetch_preflight(request, capability) is False


def test_supports_raw_prices_false_returns_false() -> None:
    provider = _provider()
    request = _request(provider=provider)
    capability = _capability(provider=provider)
    object.__setattr__(capability, "supports_raw_prices", False)

    assert can_execute_managed_api_fetch_preflight(request, capability) is False


def test_raw_request_with_raw_unsupported_returns_false() -> None:
    provider = _provider()
    request = _request(
        provider=provider,
        price_preference=ManagedApiFetchPricePreference.RAW,
    )
    capability = _capability(provider=provider)
    object.__setattr__(capability, "supports_raw_prices", False)

    assert can_execute_managed_api_fetch_preflight(request, capability) is False


def test_adjusted_request_with_adjusted_unsupported_in_capability_returns_false() -> None:
    provider = _provider()
    request = _request(
        provider=provider,
        price_preference=ManagedApiFetchPricePreference.ADJUSTED,
    )
    capability = _capability(provider=provider)
    object.__setattr__(capability, "supports_adjusted_prices", False)

    assert can_execute_managed_api_fetch_preflight(request, capability) is False


def test_adjusted_request_with_adjusted_unsupported_in_provider_returns_false() -> None:
    provider = _provider()
    request = _request(
        provider=provider,
        price_preference=ManagedApiFetchPricePreference.ADJUSTED,
    )
    capability = _capability(provider=provider)
    object.__setattr__(provider, "supports_adjusted_prices", False)

    assert can_execute_managed_api_fetch_preflight(request, capability) is False


def test_credential_access_missing_returns_false() -> None:
    provider = _provider()
    request = _request(provider=provider)
    credential_access = _credential_result(
        provider,
        status=ManagedApiCredentialStatus.MISSING,
        credential_present=False,
        credential_fingerprint=None,
    )
    object.__setattr__(request, "credential_access", credential_access)

    assert can_execute_managed_api_fetch_preflight(
        request,
        _capability(provider=provider),
    ) is False


def test_credential_access_invalid_returns_false() -> None:
    provider = _provider()
    request = _request(provider=provider)
    credential_access = _credential_result(
        provider,
        status=ManagedApiCredentialStatus.INVALID,
    )
    object.__setattr__(request, "credential_access", credential_access)

    assert can_execute_managed_api_fetch_preflight(
        request,
        _capability(provider=provider),
    ) is False


def test_credential_present_false_returns_false() -> None:
    provider = _provider()
    request = _request(provider=provider)
    credential_access = _credential_result(provider)
    object.__setattr__(credential_access, "credential_present", False)
    object.__setattr__(request, "credential_access", credential_access)

    assert can_execute_managed_api_fetch_preflight(
        request,
        _capability(provider=provider),
    ) is False


def test_symbol_other_than_provider_allowed_first_symbol_returns_false() -> None:
    provider = _provider()
    request = _request(provider=provider)
    object.__setattr__(request, "symbol", "QQQ")

    assert can_execute_managed_api_fetch_preflight(
        request,
        _capability(provider=provider),
    ) is False


def test_function_does_not_mutate_request() -> None:
    provider = _provider()
    request = _request(provider=provider)
    capability = _capability(provider=provider)
    before = _request_snapshot(request)

    can_execute_managed_api_fetch_preflight(request, capability)

    assert _request_snapshot(request) == before


def test_function_does_not_mutate_capability() -> None:
    provider = _provider()
    request = _request(provider=provider)
    capability = _capability(provider=provider)
    before = _capability_snapshot(capability)

    can_execute_managed_api_fetch_preflight(request, capability)

    assert _capability_snapshot(capability) == before


def test_no_os_import_is_introduced() -> None:
    source = PREFLIGHT_PATH.read_text(encoding="utf-8")

    assert "import os" not in source
    assert "from os" not in source


def test_no_dotenv_or_python_dotenv_import_is_introduced() -> None:
    source = PREFLIGHT_PATH.read_text(encoding="utf-8")

    assert "dotenv" not in source
    assert "python-dotenv" not in source


def test_no_requests_httpx_or_aiohttp_import_is_introduced() -> None:
    source = PREFLIGHT_PATH.read_text(encoding="utf-8")

    for package_name in ["requests", "httpx", "aiohttp"]:
        assert f"import {package_name}" not in source
        assert f"from {package_name}" not in source


def test_no_forbidden_external_dependency_import_is_introduced() -> None:
    source = PREFLIGHT_PATH.read_text(encoding="utf-8")

    for package_name in ["pandas", "numpy", "yfinance", "sqlalchemy"]:
        assert f"import {package_name}" not in source
        assert f"from {package_name}" not in source


def test_no_engine_imports_are_introduced() -> None:
    source = PREFLIGHT_PATH.read_text(encoding="utf-8")

    assert "app.engine" not in source
    assert "from app.engine" not in source
    assert "import app.engine" not in source


def test_no_daily_market_data_import_is_introduced() -> None:
    source = PREFLIGHT_PATH.read_text(encoding="utf-8")

    assert "DailyMarketData" not in source
    assert "data_contract" not in source


def test_no_managed_api_credentials_import_is_introduced() -> None:
    source = PREFLIGHT_PATH.read_text(encoding="utf-8")

    assert "app.data.managed_api_credentials" not in source
    assert "managed_api_credentials" not in source


def test_no_managed_api_provider_adapter_port_import_is_introduced() -> None:
    source = PREFLIGHT_PATH.read_text(encoding="utf-8")

    assert "ManagedApiProviderAdapterPort" not in source

