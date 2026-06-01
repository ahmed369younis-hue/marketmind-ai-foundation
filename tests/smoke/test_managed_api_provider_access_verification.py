from datetime import datetime, timedelta, timezone
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
from app.domain.managed_api_provider_access_verification import (
    ManagedApiProviderAccessVerificationResult,
    ManagedApiProviderAccessVerificationStatus,
)
from app.domain.managed_api_provider_contract import (
    ManagedApiProviderContract,
    ManagedApiProviderType,
)


CONTRACT_PATH = Path("app/domain/managed_api_provider_access_verification.py")


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
        "notes": "Metadata-only source for provider access verification tests.",
    }
    values.update(overrides)
    return DataSourceContract(**values)


def _provider(**overrides: object) -> ManagedApiProviderContract:
    values = {
        "provider_name": "Example Managed API Provider",
        "provider_type": ManagedApiProviderType.SECONDARY_CROSS_CHECK,
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
    provider: ManagedApiProviderContract | None = None,
    **overrides: object,
) -> ManagedApiCredentialAccessResult:
    provider_value = provider if provider is not None else _provider()
    values = {
        "provider": provider_value,
        "status": ManagedApiCredentialStatus.AVAILABLE,
        "credential_env_var": provider_value.credential_env_var,
        "credential_present": True,
        "credential_fingerprint": "key-ab12",
        "message": "Future credential access result contract test.",
    }
    values.update(overrides)
    return ManagedApiCredentialAccessResult(**values)


def _timestamp() -> datetime:
    return datetime.now(timezone.utc) - timedelta(minutes=1)


def _verification_result(
    *,
    provider: ManagedApiProviderContract | None = None,
    credential_access: ManagedApiCredentialAccessResult | None = None,
    **overrides: object,
) -> ManagedApiProviderAccessVerificationResult:
    provider_value = provider if provider is not None else _provider()
    default_provider = provider_value
    if not isinstance(default_provider, ManagedApiProviderContract):
        default_provider = _provider()

    credential_access_value = (
        credential_access
        if credential_access is not None
        else _credential_result(provider=default_provider)
    )
    values = {
        "provider": provider_value,
        "credential_access": credential_access_value,
        "status": ManagedApiProviderAccessVerificationStatus.VERIFIED,
        "provider_name": default_provider.provider_name,
        "credential_env_var": default_provider.credential_env_var,
        "access_checked": True,
        "verification_timestamp_utc": _timestamp(),
        "message": "Future provider-side access verification result contract test.",
    }
    values.update(overrides)
    return ManagedApiProviderAccessVerificationResult(**values)


def test_verified_result_valid_only_with_available_credential_access_and_utc_timestamp() -> None:
    result = _verification_result()

    assert result.status is ManagedApiProviderAccessVerificationStatus.VERIFIED
    assert result.credential_access.status is ManagedApiCredentialStatus.AVAILABLE
    assert result.credential_access.credential_present is True
    assert result.access_checked is True
    assert result.verification_timestamp_utc is not None
    assert result.verification_timestamp_utc.utcoffset() == timedelta(0)


def test_failed_result_valid_with_access_checked_true_and_utc_timestamp() -> None:
    result = _verification_result(
        status=ManagedApiProviderAccessVerificationStatus.FAILED,
    )

    assert result.status is ManagedApiProviderAccessVerificationStatus.FAILED
    assert result.access_checked is True
    assert result.verification_timestamp_utc is not None
    assert result.verification_timestamp_utc.utcoffset() == timedelta(0)


def test_not_verified_result_valid_only_with_access_checked_false_and_no_timestamp() -> None:
    result = _verification_result(
        status=ManagedApiProviderAccessVerificationStatus.NOT_VERIFIED,
        access_checked=False,
        verification_timestamp_utc=None,
    )

    assert result.status is ManagedApiProviderAccessVerificationStatus.NOT_VERIFIED
    assert result.access_checked is False
    assert result.verification_timestamp_utc is None


def test_verified_with_missing_credential_access_raises_value_error() -> None:
    provider = _provider()
    credential_access = _credential_result(
        provider=provider,
        status=ManagedApiCredentialStatus.MISSING,
        credential_present=False,
        credential_fingerprint=None,
    )

    with pytest.raises(
        ValueError,
        match="credential_access.status must be AVAILABLE when status is VERIFIED",
    ):
        _verification_result(
            provider=provider,
            credential_access=credential_access,
        )


def test_verified_with_credential_present_false_raises_value_error() -> None:
    provider = _provider()
    credential_access = _credential_result(provider=provider)
    object.__setattr__(credential_access, "credential_present", False)

    with pytest.raises(
        ValueError,
        match=(
            "credential_access.credential_present must be True "
            "when status is VERIFIED"
        ),
    ):
        _verification_result(
            provider=provider,
            credential_access=credential_access,
        )


def test_verified_with_missing_timestamp_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="verification_timestamp_utc must not be None",
    ):
        _verification_result(verification_timestamp_utc=None)


def test_failed_with_missing_timestamp_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="verification_timestamp_utc must not be None",
    ):
        _verification_result(
            status=ManagedApiProviderAccessVerificationStatus.FAILED,
            verification_timestamp_utc=None,
        )


def test_not_verified_with_timestamp_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="verification_timestamp_utc must be None when status is NOT_VERIFIED",
    ):
        _verification_result(
            status=ManagedApiProviderAccessVerificationStatus.NOT_VERIFIED,
            access_checked=False,
            verification_timestamp_utc=_timestamp(),
        )


def test_not_verified_with_access_checked_true_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="access_checked must be False when status is NOT_VERIFIED",
    ):
        _verification_result(
            status=ManagedApiProviderAccessVerificationStatus.NOT_VERIFIED,
            access_checked=True,
            verification_timestamp_utc=None,
        )


def test_future_timestamp_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="verification_timestamp_utc must not be in the future",
    ):
        _verification_result(
            verification_timestamp_utc=datetime.now(timezone.utc) + timedelta(days=1),
        )


def test_naive_timestamp_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="verification_timestamp_utc must be timezone-aware UTC",
    ):
        _verification_result(
            verification_timestamp_utc=datetime(2026, 1, 2, 12, 0),
        )


def test_provider_mismatch_raises_value_error() -> None:
    provider = _provider(provider_name="Provider A")
    other_provider = _provider(
        provider_name="Provider B",
        credential_env_var="OTHER_PROVIDER_API_KEY",
    )
    credential_access = _credential_result(provider=other_provider)

    with pytest.raises(
        ValueError,
        match="credential_access.provider must reference provider",
    ):
        _verification_result(
            provider=provider,
            credential_access=credential_access,
        )


def test_provider_name_mismatch_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="provider_name must equal provider.provider_name",
    ):
        _verification_result(provider_name="Other Provider")


def test_credential_env_var_mismatch_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="credential_env_var must equal provider.credential_env_var",
    ):
        _verification_result(credential_env_var="OTHER_PROVIDER_API_KEY")


def test_invalid_provider_input_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="provider must be a ManagedApiProviderContract instance",
    ):
        _verification_result(provider="provider")


def test_invalid_credential_access_input_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="credential_access must be a ManagedApiCredentialAccessResult instance",
    ):
        _verification_result(credential_access="credential_access")


def test_invalid_status_input_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "status must be a valid "
            "ManagedApiProviderAccessVerificationStatus value"
        ),
    ):
        _verification_result(status="VERIFIED")


def test_empty_message_raises_value_error() -> None:
    with pytest.raises(ValueError, match="message must not be empty"):
        _verification_result(message=" ")


def test_constructor_requires_explicit_values_and_has_no_defaults() -> None:
    with pytest.raises(TypeError):
        ManagedApiProviderAccessVerificationResult()


def test_contract_file_does_not_contain_forbidden_imports() -> None:
    source = CONTRACT_PATH.read_text(encoding="utf-8")

    for import_text in [
        "import os",
        "from os",
        "import csv",
        "from csv",
        "import pathlib",
        "from pathlib",
        "import requests",
        "from requests",
        "import httpx",
        "from httpx",
        "import aiohttp",
        "from aiohttp",
        "import pandas",
        "from pandas",
        "import numpy",
        "from numpy",
        "import yfinance",
        "from yfinance",
        "import sqlalchemy",
        "from sqlalchemy",
        "import dotenv",
        "from dotenv",
        "python-dotenv",
        "app.data",
        "app.engine",
        "DailyMarketData",
        "ManagedApiProviderAdapterPort",
        "ManagedApiEodFetchRequest",
        "ManagedApiEodFetchResult",
        "ManagedApiEodRecord",
    ]:
        assert import_text not in source


def test_contract_file_does_not_contain_forbidden_behavior() -> None:
    source = CONTRACT_PATH.read_text(encoding="utf-8")

    for forbidden_text in [
        "os.environ",
        ".env",
        "load_credential",
        "print(",
        "requests.",
        "httpx.",
        "aiohttp.",
        "fetch_eod",
        "DictReader",
        "open(",
        "read_text",
        "write_text",
        "to_csv",
        "to_sql",
        "can_pass_data_quality_gate",
        "compute_daily_features",
        "compute_daily_signals",
        "compute_daily_scores",
        "financial conclusion",
        "buy/sell",
    ]:
        assert forbidden_text not in source
