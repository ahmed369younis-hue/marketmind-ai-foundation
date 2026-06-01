from pathlib import Path

import pytest

from app.data.managed_api_credentials import read_managed_api_credential
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


UTILITY_PATH = Path("app/data/managed_api_credentials.py")


def _source() -> DataSourceContract:
    return DataSourceContract(
        name="Managed API Metadata Source",
        source_type=DataSourceType.REAL,
        granularity=DataGranularity.DAILY,
        reliability=DataSourceReliability.VERIFIED_STRUCTURE_ONLY,
        supports_ohlcv=True,
        supports_adjusted_prices=True,
        supports_corporate_actions=True,
        timezone="America/New_York",
        notes="Metadata-only source for managed API credential reader tests.",
    )


def _provider(env_var: str = "MARKETMIND_PROVIDER_API_KEY") -> ManagedApiProviderContract:
    return ManagedApiProviderContract(
        provider_name="Example Managed API Provider",
        provider_type=ManagedApiProviderType.PRIMARY_INSTITUTIONAL,
        source=_source(),
        credential_env_var=env_var,
        supports_eod_ohlcv=True,
        supports_adjusted_prices=True,
        supports_corporate_actions=True,
        supports_us_equities=True,
        supports_us_etfs=True,
        supports_fx=False,
        supports_commodities=False,
        supports_crypto=False,
        allowed_first_symbol="SPY",
        rate_limit_notes="Rate limits must be reviewed before future API use.",
        legal_access_confirmed=True,
        notes="Metadata-only provider access contract for future planning.",
    )


def test_missing_environment_variable_returns_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    provider = _provider()
    monkeypatch.delenv(provider.credential_env_var, raising=False)

    result = read_managed_api_credential(provider)

    assert result.status is ManagedApiCredentialStatus.MISSING
    assert result.credential_present is False
    assert result.credential_fingerprint is None
    assert result.message == "Managed API credential is missing"


def test_empty_environment_variable_returns_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    provider = _provider()
    monkeypatch.setenv(provider.credential_env_var, "")

    result = read_managed_api_credential(provider)

    assert result.status is ManagedApiCredentialStatus.MISSING
    assert result.credential_present is False
    assert result.credential_fingerprint is None
    assert result.message == "Managed API credential is empty"


def test_whitespace_environment_variable_returns_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    monkeypatch.setenv(provider.credential_env_var, "   ")

    result = read_managed_api_credential(provider)

    assert result.status is ManagedApiCredentialStatus.MISSING
    assert result.credential_present is False
    assert result.credential_fingerprint is None
    assert result.message == "Managed API credential is empty"


def test_non_empty_environment_variable_returns_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    credential_value = "TEST_ONLY_MANAGED_API_CREDENTIAL_VALUE"
    monkeypatch.setenv(provider.credential_env_var, credential_value)

    result = read_managed_api_credential(provider)

    assert result.status is ManagedApiCredentialStatus.AVAILABLE


def test_available_result_has_credential_present_true(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    monkeypatch.setenv(provider.credential_env_var, "TEST_ONLY_CREDENTIAL_PRESENT")

    result = read_managed_api_credential(provider)

    assert result.credential_present is True


def test_available_result_has_fingerprint_not_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    monkeypatch.setenv(provider.credential_env_var, "TEST_ONLY_FINGERPRINT_PRESENT")

    result = read_managed_api_credential(provider)

    assert result.credential_fingerprint is not None


def test_fingerprint_length_is_at_most_16(monkeypatch: pytest.MonkeyPatch) -> None:
    provider = _provider()
    monkeypatch.setenv(provider.credential_env_var, "TEST_ONLY_LENGTH_CHECK")

    result = read_managed_api_credential(provider)

    assert result.credential_fingerprint is not None
    assert len(result.credential_fingerprint) <= 16


def test_fingerprint_is_deterministic_for_same_credential(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    monkeypatch.setenv(provider.credential_env_var, "TEST_ONLY_DETERMINISTIC")

    first_result = read_managed_api_credential(provider)
    second_result = read_managed_api_credential(provider)

    assert first_result.credential_fingerprint == second_result.credential_fingerprint


def test_fingerprint_differs_for_different_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    monkeypatch.setenv(provider.credential_env_var, "TEST_ONLY_FIRST_VALUE")
    first_result = read_managed_api_credential(provider)

    monkeypatch.setenv(provider.credential_env_var, "TEST_ONLY_SECOND_VALUE")
    second_result = read_managed_api_credential(provider)

    assert first_result.credential_fingerprint != second_result.credential_fingerprint


def test_fingerprint_does_not_contain_raw_credential(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    credential_value = "TEST_ONLY_RAW_VALUE_MARKER"
    monkeypatch.setenv(provider.credential_env_var, credential_value)

    result = read_managed_api_credential(provider)

    assert result.credential_fingerprint is not None
    assert credential_value not in result.credential_fingerprint


def test_returned_message_does_not_contain_raw_credential(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    credential_value = "TEST_ONLY_MESSAGE_MARKER"
    monkeypatch.setenv(provider.credential_env_var, credential_value)

    result = read_managed_api_credential(provider)

    assert credential_value not in result.message


def test_raw_credential_is_not_printed_to_stdout_or_stderr(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    provider = _provider()
    credential_value = "TEST_ONLY_CAPTURE_MARKER"
    monkeypatch.setenv(provider.credential_env_var, credential_value)

    read_managed_api_credential(provider)
    captured = capsys.readouterr()

    assert credential_value not in captured.out
    assert credential_value not in captured.err


def test_provider_not_managed_api_provider_contract_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="provider must be a ManagedApiProviderContract instance",
    ):
        read_managed_api_credential("provider")


def test_reader_reads_only_provider_credential_env_var_and_ignores_unrelated_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider(env_var="MARKETMIND_SELECTED_PROVIDER_API_KEY")
    monkeypatch.delenv(provider.credential_env_var, raising=False)
    monkeypatch.setenv("UNRELATED_PROVIDER_API_KEY", "TEST_ONLY_UNRELATED")

    result = read_managed_api_credential(provider)

    assert result.status is ManagedApiCredentialStatus.MISSING
    assert result.credential_env_var == provider.credential_env_var


def test_reader_does_not_return_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    provider = _provider()
    monkeypatch.setenv(provider.credential_env_var, "TEST_ONLY_NO_INVALID_STATUS")

    result = read_managed_api_credential(provider)

    assert result.status is not ManagedApiCredentialStatus.INVALID


def test_reader_returns_contract_object(monkeypatch: pytest.MonkeyPatch) -> None:
    provider = _provider()
    monkeypatch.setenv(provider.credential_env_var, "TEST_ONLY_CONTRACT_OBJECT")

    result = read_managed_api_credential(provider)

    assert isinstance(result, ManagedApiCredentialAccessResult)


def test_reader_does_not_import_requests_httpx_or_aiohttp() -> None:
    source = UTILITY_PATH.read_text(encoding="utf-8")

    for package_name in ["requests", "httpx", "aiohttp"]:
        assert f"import {package_name}" not in source
        assert f"from {package_name}" not in source


def test_reader_does_not_import_forbidden_external_dependencies() -> None:
    source = UTILITY_PATH.read_text(encoding="utf-8")

    for package_name in ["pandas", "numpy", "yfinance", "sqlalchemy"]:
        assert f"import {package_name}" not in source
        assert f"from {package_name}" not in source


def test_reader_does_not_import_dotenv_or_python_dotenv() -> None:
    source = UTILITY_PATH.read_text(encoding="utf-8")

    assert "dotenv" not in source
    assert "python-dotenv" not in source


def test_reader_does_not_import_app_engine_modules() -> None:
    source = UTILITY_PATH.read_text(encoding="utf-8")

    assert "app.engine" not in source
    assert "from app.engine" not in source
    assert "import app.engine" not in source


def test_reader_does_not_import_daily_market_data() -> None:
    source = UTILITY_PATH.read_text(encoding="utf-8")

    assert "DailyMarketData" not in source
    assert "data_contract" not in source


def test_reader_does_not_import_provider_adapter_modules() -> None:
    source = UTILITY_PATH.read_text(encoding="utf-8")

    assert "adapter" not in source
    assert "adapters" not in source


def test_reader_does_not_read_dotenv_files() -> None:
    source = UTILITY_PATH.read_text(encoding="utf-8")

    assert '".env"' not in source
    assert "'.env'" not in source
    assert "open(" not in source
    assert "Path(" not in source
    assert "read_text" not in source


def test_reader_does_not_persist_files() -> None:
    source = UTILITY_PATH.read_text(encoding="utf-8")

    assert "write_text" not in source
    assert "open(" not in source
    assert "with open" not in source
