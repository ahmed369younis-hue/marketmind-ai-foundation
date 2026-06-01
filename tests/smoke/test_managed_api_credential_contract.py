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
from app.domain.managed_api_provider_contract import (
    ManagedApiProviderContract,
    ManagedApiProviderType,
)


CONTRACT_PATH = Path("app/domain/managed_api_credential_contract.py")


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
        "notes": "Metadata-only source for managed API credential contract tests.",
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


def _credential_result(**overrides: object) -> ManagedApiCredentialAccessResult:
    values = {
        "provider": _provider(),
        "status": ManagedApiCredentialStatus.AVAILABLE,
        "credential_env_var": "MARKETMIND_PROVIDER_API_KEY",
        "credential_present": True,
        "credential_fingerprint": "key-ab12",
        "message": "Future credential access result contract test.",
    }
    values.update(overrides)
    return ManagedApiCredentialAccessResult(**values)


def test_valid_available_result_passes() -> None:
    result = _credential_result(status=ManagedApiCredentialStatus.AVAILABLE)

    assert result.status is ManagedApiCredentialStatus.AVAILABLE


def test_valid_missing_result_passes() -> None:
    result = _credential_result(
        status=ManagedApiCredentialStatus.MISSING,
        credential_present=False,
        credential_fingerprint=None,
    )

    assert result.status is ManagedApiCredentialStatus.MISSING


def test_valid_invalid_result_passes() -> None:
    result = _credential_result(status=ManagedApiCredentialStatus.INVALID)

    assert result.status is ManagedApiCredentialStatus.INVALID


def test_invalid_provider_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="provider must be a ManagedApiProviderContract instance",
    ):
        _credential_result(provider="provider")


def test_invalid_status_string_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="status must be a valid ManagedApiCredentialStatus value",
    ):
        _credential_result(status="AVAILABLE")


def test_empty_credential_env_var_raises_value_error() -> None:
    with pytest.raises(ValueError, match="credential_env_var must not be empty"):
        _credential_result(credential_env_var=" ")


def test_credential_env_var_not_equal_provider_credential_env_var_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="credential_env_var must equal provider.credential_env_var",
    ):
        _credential_result(credential_env_var="OTHER_PROVIDER_API_KEY")


def test_lowercase_credential_env_var_raises_value_error() -> None:
    with pytest.raises(ValueError, match="credential_env_var must be uppercase"):
        _credential_result(credential_env_var="marketmind_provider_api_key")


def test_credential_env_var_with_spaces_raises_value_error() -> None:
    with pytest.raises(ValueError, match="credential_env_var must not contain spaces"):
        _credential_result(credential_env_var="MARKETMIND PROVIDER API KEY")


def test_non_bool_credential_present_raises_value_error() -> None:
    with pytest.raises(ValueError, match="credential_present must be bool"):
        _credential_result(credential_present="true")


def test_empty_message_raises_value_error() -> None:
    with pytest.raises(ValueError, match="message must not be empty"):
        _credential_result(message="")


def test_available_with_credential_present_false_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="credential_present must be True when status is AVAILABLE",
    ):
        _credential_result(credential_present=False)


def test_available_with_credential_fingerprint_none_raises_value_error() -> None:
    with pytest.raises(ValueError, match="credential_fingerprint must not be None"):
        _credential_result(credential_fingerprint=None)


def test_available_with_empty_credential_fingerprint_raises_value_error() -> None:
    with pytest.raises(ValueError, match="credential_fingerprint must not be empty"):
        _credential_result(credential_fingerprint=" ")


def test_available_with_credential_fingerprint_longer_than_16_chars_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="credential_fingerprint length must be <= 16",
    ):
        _credential_result(credential_fingerprint="fingerprint-too-long")


def test_missing_with_credential_present_true_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="credential_present must be False when status is MISSING",
    ):
        _credential_result(status=ManagedApiCredentialStatus.MISSING)


def test_missing_with_credential_fingerprint_not_none_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="credential_present must be False when status is MISSING",
    ):
        _credential_result(
            status=ManagedApiCredentialStatus.MISSING,
            credential_present=True,
            credential_fingerprint="key-ab12",
        )

    with pytest.raises(
        ValueError,
        match="credential_fingerprint must be None when status is MISSING",
    ):
        _credential_result(
            status=ManagedApiCredentialStatus.MISSING,
            credential_present=False,
            credential_fingerprint="key-ab12",
        )


def test_invalid_with_credential_present_false_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="credential_present must be True when status is INVALID",
    ):
        _credential_result(
            status=ManagedApiCredentialStatus.INVALID,
            credential_present=False,
        )


def test_invalid_with_credential_fingerprint_none_raises_value_error() -> None:
    with pytest.raises(ValueError, match="credential_fingerprint must not be None"):
        _credential_result(
            status=ManagedApiCredentialStatus.INVALID,
            credential_fingerprint=None,
        )


def test_invalid_with_empty_credential_fingerprint_raises_value_error() -> None:
    with pytest.raises(ValueError, match="credential_fingerprint must not be empty"):
        _credential_result(
            status=ManagedApiCredentialStatus.INVALID,
            credential_fingerprint="",
        )


def test_invalid_with_credential_fingerprint_longer_than_16_chars_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="credential_fingerprint length must be <= 16",
    ):
        _credential_result(
            status=ManagedApiCredentialStatus.INVALID,
            credential_fingerprint="fingerprint-too-long",
        )


def test_constructor_requires_explicit_values_and_has_no_defaults() -> None:
    with pytest.raises(TypeError):
        ManagedApiCredentialAccessResult()


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
