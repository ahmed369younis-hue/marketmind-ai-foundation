import ast
import json
from datetime import date
from pathlib import Path

import pytest

from app.data.tiingo_eod_adapter import TiingoEodAdapter
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
from app.domain.managed_api_eod_record import ManagedApiEodRecord
from app.domain.managed_api_fetch_request import (
    ManagedApiEodFetchRequest,
    ManagedApiFetchPricePreference,
)
from app.domain.managed_api_fetch_result import (
    ManagedApiEodFetchResult,
    ManagedApiFetchStatus,
)
from app.domain.managed_api_provider_adapter_port import (
    ManagedApiProviderAdapterCapability,
)
from app.domain.managed_api_provider_contract import (
    ManagedApiProviderContract,
    ManagedApiProviderType,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
ADAPTER_PATH = REPO_ROOT / "app" / "data" / "tiingo_eod_adapter.py"
DUMMY_CREDENTIAL = "dummy-tiingo-test-credential"


def _provider() -> ManagedApiProviderContract:
    source = DataSourceContract(
        name="Tiingo",
        source_type=DataSourceType.REAL,
        granularity=DataGranularity.DAILY,
        reliability=DataSourceReliability.VERIFIED_STRUCTURE_ONLY,
        supports_ohlcv=True,
        supports_adjusted_prices=True,
        supports_corporate_actions=True,
        timezone="America/New_York",
        notes="Injected-transport adapter test metadata only.",
    )
    return ManagedApiProviderContract(
        provider_name="Tiingo",
        provider_type=ManagedApiProviderType.SECONDARY_CROSS_CHECK,
        source=source,
        credential_env_var="TIINGO_API_KEY",
        supports_eod_ohlcv=True,
        supports_adjusted_prices=True,
        supports_corporate_actions=True,
        supports_us_equities=True,
        supports_us_etfs=True,
        supports_fx=False,
        supports_commodities=False,
        supports_crypto=False,
        allowed_first_symbol="SPY",
        rate_limit_notes="Injected-transport adapter tests only.",
        legal_access_confirmed=True,
        notes="Injected-transport adapter test metadata only.",
    )


def _credential_access(
    provider: ManagedApiProviderContract,
    status: ManagedApiCredentialStatus = ManagedApiCredentialStatus.AVAILABLE,
    credential_present: bool = True,
) -> ManagedApiCredentialAccessResult:
    return ManagedApiCredentialAccessResult(
        provider=provider,
        status=status,
        credential_env_var=provider.credential_env_var,
        credential_present=credential_present,
        credential_fingerprint="fixturefp" if credential_present else None,
        message="Credential metadata for injected-transport adapter tests only.",
    )


def _request(
    provider: ManagedApiProviderContract,
    price_preference: ManagedApiFetchPricePreference,
    credential_access: ManagedApiCredentialAccessResult | None = None,
) -> ManagedApiEodFetchRequest:
    return ManagedApiEodFetchRequest(
        provider=provider,
        credential_access=credential_access or _credential_access(provider),
        symbol="SPY",
        start_date=date(2024, 1, 2),
        end_date=date(2024, 1, 5),
        price_preference=price_preference,
        timezone="America/New_York",
        purpose="Injected-transport adapter tests only.",
    )


def _raw_payload() -> str:
    return json.dumps(
        [
            {
                "date": "2024-01-02T00:00:00.000Z",
                "open": 470.0,
                "high": 475.0,
                "low": 468.0,
                "close": 474.0,
                "volume": 1000,
            },
            {
                "date": "2024-01-03T00:00:00.000Z",
                "open": 474.0,
                "high": 476.0,
                "low": 472.0,
                "close": 475.0,
                "volume": 1100,
            },
        ]
    )


def _adjusted_payload() -> str:
    return json.dumps(
        [
            {
                "date": "2024-01-02T00:00:00.000Z",
                "open": 470.0,
                "high": 475.0,
                "low": 468.0,
                "close": 474.0,
                "volume": 1000,
                "adjOpen": 469.0,
                "adjHigh": 474.0,
                "adjLow": 467.0,
                "adjClose": 473.0,
                "adjVolume": 1200,
            }
        ]
    )


def test_adapter_can_be_constructed_with_valid_provider_and_transport() -> None:
    adapter = TiingoEodAdapter(_provider(), lambda request, credential: _raw_payload())

    assert isinstance(adapter, TiingoEodAdapter)


def test_invalid_provider_raises_value_error() -> None:
    with pytest.raises(ValueError, match="provider must be"):
        TiingoEodAdapter("provider", lambda request, credential: _raw_payload())


def test_non_callable_transport_raises_value_error() -> None:
    with pytest.raises(ValueError, match="transport must be callable"):
        TiingoEodAdapter(_provider(), "transport")


def test_capability_metadata_matches_tiingo_adapter_policy() -> None:
    provider = _provider()
    adapter = TiingoEodAdapter(provider, lambda request, credential: _raw_payload())

    capability = adapter.capability

    assert isinstance(capability, ManagedApiProviderAdapterCapability)
    assert capability.provider is provider
    assert capability.adapter_name == "TiingoEodAdapter"
    assert capability.supports_fetch_eod is True
    assert capability.supports_single_symbol_fetch is True
    assert capability.supports_bulk_fetch is False


def test_raw_request_with_injected_fixture_payload_returns_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    request = _request(provider, ManagedApiFetchPricePreference.RAW)
    adapter = TiingoEodAdapter(provider, lambda request, credential: _raw_payload())
    monkeypatch.setenv(provider.credential_env_var, DUMMY_CREDENTIAL)

    result = adapter.fetch_eod(request)

    assert isinstance(result, ManagedApiEodFetchResult)
    assert result.status is ManagedApiFetchStatus.SUCCESS
    assert all(isinstance(record, ManagedApiEodRecord) for record in result.records)
    assert result.records_count == len(result.records)
    assert result.first_record_date == date(2024, 1, 2)
    assert result.last_record_date == date(2024, 1, 3)


def test_adjusted_request_with_injected_fixture_payload_returns_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    request = _request(provider, ManagedApiFetchPricePreference.ADJUSTED)
    adapter = TiingoEodAdapter(
        provider,
        lambda request, credential: _adjusted_payload(),
    )
    monkeypatch.setenv(provider.credential_env_var, DUMMY_CREDENTIAL)

    result = adapter.fetch_eod(request)

    assert result.status is ManagedApiFetchStatus.SUCCESS
    assert result.records[0].open == 469.0
    assert result.records[0].close == 473.0
    assert result.records[0].adjusted_close == 473.0


def test_adapter_calls_injected_transport_with_request_and_dummy_credential(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    request = _request(provider, ManagedApiFetchPricePreference.RAW)
    seen: dict[str, object] = {}

    def transport(
        transport_request: ManagedApiEodFetchRequest,
        raw_credential: str,
    ) -> str:
        seen["request"] = transport_request
        seen["credential"] = raw_credential
        return _raw_payload()

    adapter = TiingoEodAdapter(provider, transport)
    monkeypatch.setenv(provider.credential_env_var, DUMMY_CREDENTIAL)

    adapter.fetch_eod(request)

    assert seen["request"] is request
    assert seen["credential"] == DUMMY_CREDENTIAL


def test_adapter_uses_preflight_and_rejects_failed_preflight(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    request = _request(provider, ManagedApiFetchPricePreference.RAW)
    adapter = TiingoEodAdapter(provider, lambda request, credential: _raw_payload())
    monkeypatch.setenv(provider.credential_env_var, DUMMY_CREDENTIAL)
    monkeypatch.setattr(
        "app.data.tiingo_eod_adapter.can_execute_managed_api_fetch_preflight",
        lambda request, capability: False,
    )

    with pytest.raises(ValueError, match="managed API fetch preflight failed"):
        adapter.fetch_eod(request)


def test_missing_environment_credential_produces_failed_result_without_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    request = _request(provider, ManagedApiFetchPricePreference.RAW)
    adapter = TiingoEodAdapter(provider, lambda request, credential: _raw_payload())
    monkeypatch.delenv(provider.credential_env_var, raising=False)

    result = adapter.fetch_eod(request)

    assert result.status is ManagedApiFetchStatus.FAILED
    assert result.records == []
    assert result.first_record_date is None
    assert result.last_record_date is None
    assert DUMMY_CREDENTIAL not in result.message


def test_transport_returning_non_string_raises_value_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    request = _request(provider, ManagedApiFetchPricePreference.RAW)
    adapter = TiingoEodAdapter(provider, lambda request, credential: {"rows": []})
    monkeypatch.setenv(provider.credential_env_var, DUMMY_CREDENTIAL)

    with pytest.raises(ValueError, match="JSON payload string"):
        adapter.fetch_eod(request)


def test_transport_payload_containing_raw_credential_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    request = _request(provider, ManagedApiFetchPricePreference.RAW)
    adapter = TiingoEodAdapter(
        provider,
        lambda request, credential: f"{_raw_payload()}{credential}",
    )
    monkeypatch.setenv(provider.credential_env_var, DUMMY_CREDENTIAL)

    with pytest.raises(ValueError, match="must not contain raw credential"):
        adapter.fetch_eod(request)


def test_malformed_fixture_payload_returns_failed_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    request = _request(provider, ManagedApiFetchPricePreference.RAW)
    adapter = TiingoEodAdapter(provider, lambda request, credential: "{bad json")
    monkeypatch.setenv(provider.credential_env_var, DUMMY_CREDENTIAL)

    result = adapter.fetch_eod(request)

    assert result.status is ManagedApiFetchStatus.FAILED
    assert result.records_count == 0
    assert result.records == []
    assert result.first_record_date is None
    assert result.last_record_date is None


def test_result_message_does_not_contain_dummy_raw_credential(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    request = _request(provider, ManagedApiFetchPricePreference.RAW)
    adapter = TiingoEodAdapter(provider, lambda request, credential: _raw_payload())
    monkeypatch.setenv(provider.credential_env_var, DUMMY_CREDENTIAL)

    result = adapter.fetch_eod(request)

    assert DUMMY_CREDENTIAL not in result.message


def test_adapter_does_not_mutate_request_provider_or_credential_access(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = _provider()
    credential_access = _credential_access(provider)
    request = _request(
        provider,
        ManagedApiFetchPricePreference.RAW,
        credential_access=credential_access,
    )
    before_provider = repr(provider)
    before_credential_access = repr(credential_access)
    before_request = repr(request)
    adapter = TiingoEodAdapter(provider, lambda request, credential: _raw_payload())
    monkeypatch.setenv(provider.credential_env_var, DUMMY_CREDENTIAL)

    adapter.fetch_eod(request)

    assert repr(provider) == before_provider
    assert repr(credential_access) == before_credential_access
    assert repr(request) == before_request


def test_adapter_file_does_not_contain_forbidden_imports() -> None:
    tree = ast.parse(ADAPTER_PATH.read_text(encoding="utf-8"))
    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.add(node.module)

    forbidden_imports = {
        "os",
        "csv",
        "pathlib",
        "urllib",
        "urllib.request",
        "requests",
        "httpx",
        "aiohttp",
        "pandas",
        "numpy",
        "yfinance",
        "sqlalchemy",
        "dotenv",
        "python-dotenv",
        "app.engine",
        "app.domain.data_contract",
    }

    assert imported_modules.isdisjoint(forbidden_imports)


def test_adapter_file_does_not_contain_forbidden_runtime_surfaces() -> None:
    content = ADAPTER_PATH.read_text(encoding="utf-8")
    forbidden_snippets = [
        "os.environ",
        "print(",
        "requests.",
        "httpx.",
        "aiohttp.",
        "urllib.",
        ".env",
        "DailyMarketData",
        "Data Quality Gate",
        "engine execution",
        "market analysis",
        "financial conclusion",
        "open(",
        ".write(",
    ]

    for snippet in forbidden_snippets:
        assert snippet not in content


def test_public_docs_contain_adapter_section_and_boundaries() -> None:
    roadmap = (REPO_ROOT / "docs" / "PUBLIC_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    required_phrases = [
        "Tiingo planning/test boundaries",
        "fake transports",
        "injected callables",
        "No real Tiingo response payload",
        "API key",
        "provider validation artifact is included",
        "must not read `.env`",
        "store raw credentials",
        "verify provider access",
        "ingest API data",
        "produce market conclusions",
    ]

    for phrase in required_phrases:
        assert phrase in roadmap
