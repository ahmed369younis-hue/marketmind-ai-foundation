from pathlib import Path

import pytest

from app.data.managed_api_runtime_credentials import (
    use_managed_api_runtime_credential,
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
from app.domain.managed_api_provider_contract import (
    ManagedApiProviderContract,
    ManagedApiProviderType,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_CREDENTIAL_PATH = Path("app/data/managed_api_runtime_credentials.py")


def _source(**overrides: object) -> DataSourceContract:
    values = {
        "name": "Managed API Runtime Credential Source",
        "source_type": DataSourceType.REAL,
        "granularity": DataGranularity.DAILY,
        "reliability": DataSourceReliability.VERIFIED_STRUCTURE_ONLY,
        "supports_ohlcv": True,
        "supports_adjusted_prices": True,
        "supports_corporate_actions": True,
        "timezone": "America/New_York",
        "notes": "Metadata source for runtime credential boundary tests.",
    }
    values.update(overrides)
    return DataSourceContract(**values)


def _provider(**overrides: object) -> ManagedApiProviderContract:
    values = {
        "provider_name": "Runtime Credential Test Provider",
        "provider_type": ManagedApiProviderType.SECONDARY_CROSS_CHECK,
        "source": _source(),
        "credential_env_var": "MARKETMIND_RUNTIME_TEST_KEY",
        "supports_eod_ohlcv": True,
        "supports_adjusted_prices": True,
        "supports_corporate_actions": True,
        "supports_us_equities": True,
        "supports_us_etfs": True,
        "supports_fx": False,
        "supports_commodities": False,
        "supports_crypto": False,
        "allowed_first_symbol": "SPY",
        "rate_limit_notes": "Runtime credential tests do not call providers.",
        "legal_access_confirmed": True,
        "notes": "Metadata-only provider for runtime credential tests.",
    }
    values.update(overrides)
    return ManagedApiProviderContract(**values)


def _credential_access(
    provider: ManagedApiProviderContract,
    **overrides: object,
) -> ManagedApiCredentialAccessResult:
    values = {
        "provider": provider,
        "status": ManagedApiCredentialStatus.AVAILABLE,
        "credential_env_var": provider.credential_env_var,
        "credential_present": True,
        "credential_fingerprint": "dummy-fp",
        "message": "Runtime credential boundary test access result.",
    }
    values.update(overrides)
    return ManagedApiCredentialAccessResult(**values)


def _provider_snapshot(provider: ManagedApiProviderContract) -> tuple[object, ...]:
    return (
        provider.provider_name,
        provider.provider_type,
        provider.source,
        provider.credential_env_var,
        provider.supports_eod_ohlcv,
        provider.supports_adjusted_prices,
        provider.supports_corporate_actions,
        provider.supports_us_equities,
        provider.supports_us_etfs,
        provider.supports_fx,
        provider.supports_commodities,
        provider.supports_crypto,
        provider.allowed_first_symbol,
        provider.rate_limit_notes,
        provider.legal_access_confirmed,
        provider.notes,
    )


def _credential_access_snapshot(
    credential_access: ManagedApiCredentialAccessResult,
) -> tuple[object, ...]:
    return (
        credential_access.provider,
        credential_access.status,
        credential_access.credential_env_var,
        credential_access.credential_present,
        credential_access.credential_fingerprint,
        credential_access.message,
    )


def test_valid_inputs_invoke_callback_and_return_non_secret_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    credential_access = _credential_access(provider)
    monkeypatch.setenv(provider.credential_env_var, "DUMMY_RUNTIME_VALUE")

    result = use_managed_api_runtime_credential(
        provider,
        credential_access,
        lambda credential: f"credential-length:{len(credential)}",
    )

    assert result == "credential-length:19"


def test_callback_receives_dummy_credential_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    credential_access = _credential_access(provider)
    dummy_value = "DUMMY_RUNTIME_CALLBACK_VALUE"
    received: list[str] = []
    monkeypatch.setenv(provider.credential_env_var, dummy_value)

    result = use_managed_api_runtime_credential(
        provider,
        credential_access,
        lambda credential: received.append(credential) or "callback-complete",
    )

    assert result == "callback-complete"
    assert received == [dummy_value]


def test_missing_environment_variable_raises_value_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    monkeypatch.delenv(provider.credential_env_var, raising=False)

    with pytest.raises(ValueError, match="runtime credential is unavailable"):
        use_managed_api_runtime_credential(
            provider,
            _credential_access(provider),
            lambda credential: "unused",
        )


def test_empty_environment_variable_raises_value_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    monkeypatch.setenv(provider.credential_env_var, "")

    with pytest.raises(ValueError, match="runtime credential is unavailable"):
        use_managed_api_runtime_credential(
            provider,
            _credential_access(provider),
            lambda credential: "unused",
        )


def test_whitespace_environment_variable_raises_value_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    monkeypatch.setenv(provider.credential_env_var, "   ")

    with pytest.raises(ValueError, match="runtime credential is unavailable"):
        use_managed_api_runtime_credential(
            provider,
            _credential_access(provider),
            lambda credential: "unused",
        )


def test_missing_credential_access_status_raises_value_error() -> None:
    provider = _provider()
    credential_access = _credential_access(
        provider,
        status=ManagedApiCredentialStatus.MISSING,
        credential_present=False,
        credential_fingerprint=None,
    )

    with pytest.raises(ValueError, match="status must be AVAILABLE"):
        use_managed_api_runtime_credential(
            provider,
            credential_access,
            lambda credential: "unused",
        )


def test_invalid_credential_access_status_raises_value_error() -> None:
    provider = _provider()
    credential_access = _credential_access(
        provider,
        status=ManagedApiCredentialStatus.INVALID,
    )

    with pytest.raises(ValueError, match="status must be AVAILABLE"):
        use_managed_api_runtime_credential(
            provider,
            credential_access,
            lambda credential: "unused",
        )


def test_credential_present_false_raises_value_error() -> None:
    provider = _provider()
    credential_access = _credential_access(provider)
    object.__setattr__(credential_access, "credential_present", False)

    with pytest.raises(ValueError, match="credential_present must be True"):
        use_managed_api_runtime_credential(
            provider,
            credential_access,
            lambda credential: "unused",
        )


def test_provider_mismatch_raises_value_error() -> None:
    provider = _provider(provider_name="Runtime Provider")
    other_provider = _provider(
        provider_name="Other Runtime Provider",
        credential_env_var="OTHER_RUNTIME_TEST_KEY",
    )

    with pytest.raises(ValueError, match="credential_access.provider"):
        use_managed_api_runtime_credential(
            provider,
            _credential_access(other_provider),
            lambda credential: "unused",
        )


def test_invalid_provider_input_raises_value_error() -> None:
    provider = _provider()

    with pytest.raises(
        ValueError,
        match="provider must be a ManagedApiProviderContract instance",
    ):
        use_managed_api_runtime_credential(
            "provider",
            _credential_access(provider),
            lambda credential: "unused",
        )


def test_invalid_credential_access_input_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="credential_access must be a ManagedApiCredentialAccessResult instance",
    ):
        use_managed_api_runtime_credential(
            _provider(),
            "credential_access",
            lambda credential: "unused",
        )


def test_non_callable_consumer_raises_value_error() -> None:
    provider = _provider()

    with pytest.raises(ValueError, match="consumer must be callable"):
        use_managed_api_runtime_credential(
            provider,
            _credential_access(provider),
            "consumer",
        )


def test_consumer_returning_raw_credential_exactly_raises_value_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    credential_access = _credential_access(provider)
    monkeypatch.setenv(provider.credential_env_var, "DUMMY_RUNTIME_EXACT_RETURN")

    with pytest.raises(ValueError, match="must not be the raw credential"):
        use_managed_api_runtime_credential(
            provider,
            credential_access,
            lambda credential: credential,
        )


def test_runtime_credential_function_does_not_mutate_inputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    credential_access = _credential_access(provider)
    provider_before = _provider_snapshot(provider)
    credential_access_before = _credential_access_snapshot(credential_access)
    monkeypatch.setenv(provider.credential_env_var, "DUMMY_RUNTIME_NO_MUTATION")

    use_managed_api_runtime_credential(
        provider,
        credential_access,
        lambda credential: "non-secret-result",
    )

    assert _provider_snapshot(provider) == provider_before
    assert _credential_access_snapshot(credential_access) == credential_access_before


def test_runtime_credential_file_does_not_contain_forbidden_imports() -> None:
    source = RUNTIME_CREDENTIAL_PATH.read_text(encoding="utf-8")

    forbidden_imports = [
        "import pathlib",
        "from pathlib",
        "import csv",
        "from csv",
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
        "app.engine",
        "DailyMarketData",
        "ManagedApiProviderAdapterPort",
        "ManagedApiEodFetchRequest",
        "ManagedApiEodFetchResult",
        "ManagedApiEodRecord",
    ]

    for forbidden_import in forbidden_imports:
        assert forbidden_import not in source


def test_runtime_credential_file_does_not_contain_print_calls() -> None:
    source = RUNTIME_CREDENTIAL_PATH.read_text(encoding="utf-8")

    assert "print(" not in source


def test_runtime_credential_file_does_not_contain_forbidden_behavior() -> None:
    source = RUNTIME_CREDENTIAL_PATH.read_text(encoding="utf-8")

    forbidden_terms = [
        "write_text",
        "open(",
        "with open",
        ".write(",
        "API client",
        "requests.",
        "httpx.",
        "aiohttp.",
        "response",
        "parse",
        "ingest",
        "persist",
        "can_pass_data_quality_gate",
        "Data Quality Gate",
        "app.engine",
        "engine execution",
        "frontend",
        "financial conclusion",
    ]

    for forbidden_term in forbidden_terms:
        assert forbidden_term not in source


def test_public_docs_contain_runtime_credential_access_boundary() -> None:
    roadmap = (REPO_ROOT / "docs" / "PUBLIC_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    security = (REPO_ROOT / "SECURITY.md").read_text(encoding="utf-8")
    public_docs = f"{roadmap}\n{security}"

    required_phrases = [
        "runtime credential-use boundary",
        "Credential handling must remain secret-safe",
        "must not read `.env`",
        "print raw credentials",
        "store raw credentials",
        "verify provider access",
        "verify credential correctness",
        "ingest API data",
        "persist data",
        "run engine logic",
        "produce market conclusions",
        "Keys must not be printed, logged, stored in fixtures",
    ]

    for phrase in required_phrases:
        assert phrase in public_docs
