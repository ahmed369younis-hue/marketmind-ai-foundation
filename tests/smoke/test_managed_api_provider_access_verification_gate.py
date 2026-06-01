from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.data.managed_api_provider_access_verification_gate import (
    can_use_provider_access_verification_for_fetch_planning,
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
from app.domain.managed_api_provider_access_verification import (
    ManagedApiProviderAccessVerificationResult,
    ManagedApiProviderAccessVerificationStatus,
)
from app.domain.managed_api_provider_contract import (
    ManagedApiProviderContract,
    ManagedApiProviderType,
)


GATE_PATH = Path("app/data/managed_api_provider_access_verification_gate.py")


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
        "notes": "Metadata-only source for provider access gate tests.",
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


def _timestamp() -> datetime:
    return datetime.now(timezone.utc) - timedelta(minutes=1)


def _verification_result(
    *,
    provider: ManagedApiProviderContract | None = None,
    credential_access: ManagedApiCredentialAccessResult | None = None,
    **overrides: object,
) -> ManagedApiProviderAccessVerificationResult:
    selected_provider = provider or _provider()
    selected_credential_access = credential_access or _credential_result(
        selected_provider
    )
    values = {
        "provider": selected_provider,
        "credential_access": selected_credential_access,
        "status": ManagedApiProviderAccessVerificationStatus.VERIFIED,
        "provider_name": selected_provider.provider_name,
        "credential_env_var": selected_provider.credential_env_var,
        "access_checked": True,
        "verification_timestamp_utc": _timestamp(),
        "message": "Future provider-side access verification result gate test.",
    }
    values.update(overrides)
    return ManagedApiProviderAccessVerificationResult(**values)


def _snapshot(
    result: ManagedApiProviderAccessVerificationResult,
) -> tuple[object, ...]:
    return (
        result.provider,
        result.credential_access,
        result.status,
        result.provider_name,
        result.credential_env_var,
        result.access_checked,
        result.verification_timestamp_utc,
        result.message,
    )


def test_verified_available_present_checked_with_timestamp_returns_true() -> None:
    result = _verification_result()

    assert can_use_provider_access_verification_for_fetch_planning(result) is True


def test_failed_result_returns_false() -> None:
    result = _verification_result(
        status=ManagedApiProviderAccessVerificationStatus.FAILED,
    )

    assert can_use_provider_access_verification_for_fetch_planning(result) is False


def test_not_verified_result_returns_false() -> None:
    result = _verification_result(
        status=ManagedApiProviderAccessVerificationStatus.NOT_VERIFIED,
        access_checked=False,
        verification_timestamp_utc=None,
    )

    assert can_use_provider_access_verification_for_fetch_planning(result) is False


def test_invalid_input_type_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "verification_result must be a "
            "ManagedApiProviderAccessVerificationResult instance"
        ),
    ):
        can_use_provider_access_verification_for_fetch_planning(
            "verification_result"
        )


def test_function_returns_bool_for_all_valid_statuses() -> None:
    results = [
        _verification_result(),
        _verification_result(
            status=ManagedApiProviderAccessVerificationStatus.FAILED,
        ),
        _verification_result(
            status=ManagedApiProviderAccessVerificationStatus.NOT_VERIFIED,
            access_checked=False,
            verification_timestamp_utc=None,
        ),
    ]

    for result in results:
        gate_result = can_use_provider_access_verification_for_fetch_planning(
            result
        )
        assert type(gate_result) is bool


def test_gate_does_not_mutate_verification_result_object() -> None:
    result = _verification_result()
    before = _snapshot(result)

    can_use_provider_access_verification_for_fetch_planning(result)

    assert _snapshot(result) == before


def test_verified_with_missing_credential_access_is_rejected_by_contract() -> None:
    provider = _provider()
    credential_access = _credential_result(
        provider,
        status=ManagedApiCredentialStatus.MISSING,
        credential_present=False,
        credential_fingerprint=None,
    )

    with pytest.raises(ValueError):
        _verification_result(
            provider=provider,
            credential_access=credential_access,
        )


def test_verified_with_credential_present_false_has_no_successful_gate_path() -> None:
    result = _verification_result()
    object.__setattr__(result.credential_access, "credential_present", False)

    assert can_use_provider_access_verification_for_fetch_planning(result) is False


def test_gate_file_does_not_contain_forbidden_imports() -> None:
    source = GATE_PATH.read_text(encoding="utf-8")

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
    ]:
        assert import_text not in source


def test_gate_file_does_not_import_blocked_internal_boundaries() -> None:
    source = GATE_PATH.read_text(encoding="utf-8")

    for blocked_text in [
        "app.engine",
        "DailyMarketData",
        "ManagedApiProviderAdapterPort",
        "ManagedApiEodFetchRequest",
        "ManagedApiEodFetchResult",
        "ManagedApiEodRecord",
    ]:
        assert blocked_text not in source


def test_gate_file_does_not_contain_forbidden_behavior() -> None:
    source = GATE_PATH.read_text(encoding="utf-8")

    for forbidden_text in [
        "os.environ",
        ".env",
        "load_credential",
        "credential_value",
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
        "provider_response",
        "parse_response",
        "financial conclusion",
        "buy/sell",
    ]:
        assert forbidden_text not in source
