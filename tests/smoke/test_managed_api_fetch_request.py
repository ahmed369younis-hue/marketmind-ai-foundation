from datetime import date, timedelta
from pathlib import Path

import pytest

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
from app.domain.managed_api_provider_contract import (
    ManagedApiProviderContract,
    ManagedApiProviderType,
)


CONTRACT_PATH = Path("app/domain/managed_api_fetch_request.py")


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
        "notes": "Metadata-only source for managed API fetch request tests.",
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


def _request(**overrides: object) -> ManagedApiEodFetchRequest:
    provider = overrides.pop("provider", _provider())
    if "credential_access" in overrides:
        credential_access = overrides.pop("credential_access")
    else:
        credential_access = _credential_result(provider)
    start_date, end_date = _date_range()
    timezone = (
        provider.source.timezone
        if isinstance(provider, ManagedApiProviderContract)
        else "America/New_York"
    )
    values = {
        "provider": provider,
        "credential_access": credential_access,
        "symbol": "SPY",
        "start_date": start_date,
        "end_date": end_date,
        "price_preference": ManagedApiFetchPricePreference.RAW,
        "timezone": timezone,
        "purpose": "Future managed API EOD fetch request contract test.",
    }
    values.update(overrides)
    return ManagedApiEodFetchRequest(**values)


def test_valid_raw_request_passes() -> None:
    request = _request(price_preference=ManagedApiFetchPricePreference.RAW)

    assert request.price_preference is ManagedApiFetchPricePreference.RAW


def test_valid_adjusted_request_passes_when_provider_supports_adjusted_prices() -> None:
    request = _request(price_preference=ManagedApiFetchPricePreference.ADJUSTED)

    assert request.price_preference is ManagedApiFetchPricePreference.ADJUSTED


def test_invalid_provider_raises_value_error() -> None:
    provider = _provider()

    with pytest.raises(
        ValueError,
        match="provider must be a ManagedApiProviderContract instance",
    ):
        _request(provider="provider", credential_access=_credential_result(provider))


def test_invalid_credential_access_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="credential_access must be a ManagedApiCredentialAccessResult instance",
    ):
        _request(credential_access="credential")


def test_credential_access_for_different_provider_raises_value_error() -> None:
    provider = _provider()
    other_provider = _provider(provider_name="Other Managed API Provider")

    with pytest.raises(
        ValueError,
        match="credential_access.provider must reference provider",
    ):
        _request(
            provider=provider,
            credential_access=_credential_result(other_provider),
        )


def test_credential_access_missing_raises_value_error() -> None:
    provider = _provider()
    credential_access = _credential_result(
        provider,
        status=ManagedApiCredentialStatus.MISSING,
        credential_present=False,
        credential_fingerprint=None,
    )

    with pytest.raises(ValueError, match="credential_access.status must be AVAILABLE"):
        _request(provider=provider, credential_access=credential_access)


def test_credential_access_invalid_raises_value_error() -> None:
    provider = _provider()
    credential_access = _credential_result(
        provider,
        status=ManagedApiCredentialStatus.INVALID,
    )

    with pytest.raises(ValueError, match="credential_access.status must be AVAILABLE"):
        _request(provider=provider, credential_access=credential_access)


def test_credential_present_false_raises_value_error() -> None:
    provider = _provider()
    credential_access = _credential_result(provider)
    object.__setattr__(credential_access, "credential_present", False)

    with pytest.raises(
        ValueError,
        match="credential_access.credential_present must be True",
    ):
        _request(provider=provider, credential_access=credential_access)


def test_empty_symbol_raises_value_error() -> None:
    with pytest.raises(ValueError, match="symbol must not be empty"):
        _request(symbol=" ")


def test_symbol_other_than_provider_allowed_first_symbol_raises_value_error() -> None:
    with pytest.raises(ValueError, match="symbol must equal provider.allowed_first_symbol"):
        _request(symbol="QQQ")


def test_future_start_date_raises_value_error() -> None:
    with pytest.raises(ValueError, match="start_date must not be in the future"):
        _request(start_date=date.today() + timedelta(days=1))


def test_future_end_date_raises_value_error() -> None:
    with pytest.raises(ValueError, match="end_date must not be in the future"):
        _request(end_date=date.today() + timedelta(days=1))


def test_end_date_before_start_date_raises_value_error() -> None:
    start_date, _ = _date_range()

    with pytest.raises(
        ValueError,
        match="end_date must be greater than or equal to start_date",
    ):
        _request(start_date=start_date, end_date=start_date - timedelta(days=1))


def test_invalid_price_preference_string_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="price_preference must be a valid ManagedApiFetchPricePreference value",
    ):
        _request(price_preference="RAW")


def test_adjusted_request_when_provider_does_not_support_adjusted_prices_raises_value_error() -> None:
    provider = _provider(supports_adjusted_prices=False)

    with pytest.raises(
        ValueError,
        match="provider.supports_adjusted_prices must be True for ADJUSTED requests",
    ):
        _request(
            provider=provider,
            credential_access=_credential_result(provider),
            price_preference=ManagedApiFetchPricePreference.ADJUSTED,
        )


def test_provider_without_eod_ohlcv_support_raises_value_error() -> None:
    provider = _provider(supports_eod_ohlcv=False)

    with pytest.raises(ValueError, match="provider.supports_eod_ohlcv must be True"):
        _request(provider=provider, credential_access=_credential_result(provider))


def test_provider_source_non_daily_granularity_raises_value_error() -> None:
    provider = _provider()
    object.__setattr__(provider.source, "granularity", "INTRADAY")

    with pytest.raises(ValueError, match="provider.source.granularity must be DAILY"):
        _request(provider=provider, credential_access=_credential_result(provider))


def test_empty_timezone_raises_value_error() -> None:
    with pytest.raises(ValueError, match="timezone must not be empty"):
        _request(timezone="")


def test_timezone_mismatch_raises_value_error() -> None:
    with pytest.raises(ValueError, match="timezone must equal provider.source.timezone"):
        _request(timezone="UTC")


def test_empty_purpose_raises_value_error() -> None:
    with pytest.raises(ValueError, match="purpose must not be empty"):
        _request(purpose=" ")


def test_constructor_requires_explicit_values_and_has_no_defaults() -> None:
    with pytest.raises(TypeError):
        ManagedApiEodFetchRequest()


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
