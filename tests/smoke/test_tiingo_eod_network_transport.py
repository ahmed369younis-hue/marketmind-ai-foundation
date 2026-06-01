import ast
from datetime import date
from pathlib import Path
import urllib.error
import urllib.parse

import pytest

from app.data.tiingo_eod_network_transport import (
    TiingoEodNetworkTransport,
    build_tiingo_eod_prices_url,
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
from app.domain.managed_api_provider_contract import (
    ManagedApiProviderContract,
    ManagedApiProviderType,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
TRANSPORT_PATH = REPO_ROOT / "app" / "data" / "tiingo_eod_network_transport.py"
TEST_PATH = REPO_ROOT / "tests" / "smoke" / "test_tiingo_eod_network_transport.py"
DUMMY_CREDENTIAL = "dummy-tiingo-network-credential"


class _FakeResponse:
    def __init__(self, body: bytes, status: int = 200) -> None:
        self._body = body
        self.status = status

    def read(self) -> bytes:
        return self._body


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
        notes="Network transport test metadata only.",
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
        rate_limit_notes="Network transport tests only.",
        legal_access_confirmed=True,
        notes="Network transport test metadata only.",
    )


def _credential_access(
    provider: ManagedApiProviderContract,
) -> ManagedApiCredentialAccessResult:
    return ManagedApiCredentialAccessResult(
        provider=provider,
        status=ManagedApiCredentialStatus.AVAILABLE,
        credential_env_var=provider.credential_env_var,
        credential_present=True,
        credential_fingerprint="fixturefp",
        message="Credential metadata for network transport tests only.",
    )


def _request() -> ManagedApiEodFetchRequest:
    provider = _provider()
    return ManagedApiEodFetchRequest(
        provider=provider,
        credential_access=_credential_access(provider),
        symbol="SPY",
        start_date=date(2024, 1, 2),
        end_date=date(2024, 1, 5),
        price_preference=ManagedApiFetchPricePreference.RAW,
        timezone="America/New_York",
        purpose="Network transport tests only.",
    )


def test_build_tiingo_eod_prices_url_returns_expected_spy_url_shape() -> None:
    url = build_tiingo_eod_prices_url(_request())
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)

    assert parsed.scheme == "https"
    assert parsed.netloc == "api.tiingo.com"
    assert parsed.path == "/tiingo/daily/SPY/prices"
    assert query["startDate"] == ["2024-01-02"]
    assert query["endDate"] == ["2024-01-05"]
    assert query["resampleFreq"] == ["daily"]
    assert DUMMY_CREDENTIAL not in url
    assert "token" not in query


def test_url_builder_rejects_invalid_request_input() -> None:
    with pytest.raises(ValueError, match="request must be"):
        build_tiingo_eod_prices_url("request")


def test_transport_can_be_constructed_with_fake_urlopen() -> None:
    transport = TiingoEodNetworkTransport(
        urlopen=lambda request, timeout: _FakeResponse(b"[]"),
    )

    assert isinstance(transport, TiingoEodNetworkTransport)


def test_transport_rejects_invalid_timeout_seconds() -> None:
    with pytest.raises(ValueError, match="timeout_seconds"):
        TiingoEodNetworkTransport(
            urlopen=lambda request, timeout: _FakeResponse(b"[]"),
            timeout_seconds=0,
        )

    with pytest.raises(ValueError, match="timeout_seconds"):
        TiingoEodNetworkTransport(
            urlopen=lambda request, timeout: _FakeResponse(b"[]"),
            timeout_seconds=True,
        )


def test_call_rejects_invalid_request_input() -> None:
    transport = TiingoEodNetworkTransport(
        urlopen=lambda request, timeout: _FakeResponse(b"[]"),
    )

    with pytest.raises(ValueError, match="request must be"):
        transport("request", DUMMY_CREDENTIAL)


def test_call_rejects_empty_or_whitespace_raw_credential() -> None:
    transport = TiingoEodNetworkTransport(
        urlopen=lambda request, timeout: _FakeResponse(b"[]"),
    )

    with pytest.raises(ValueError, match="raw_credential"):
        transport(_request(), "")

    with pytest.raises(ValueError, match="raw_credential"):
        transport(_request(), "   ")


def test_call_sends_authorization_accept_and_timeout_to_fake_urlopen() -> None:
    seen: dict[str, object] = {}

    def fake_urlopen(network_request, timeout: int):
        seen["authorization"] = network_request.get_header("Authorization")
        seen["accept"] = network_request.get_header("Accept")
        seen["timeout"] = timeout
        seen["url"] = network_request.full_url
        seen["method"] = network_request.get_method()
        return _FakeResponse(b'[{"date":"2024-01-02"}]')

    transport = TiingoEodNetworkTransport(
        urlopen=fake_urlopen,
        timeout_seconds=7,
    )

    body = transport(_request(), DUMMY_CREDENTIAL)

    assert seen["authorization"] == f"Token {DUMMY_CREDENTIAL}"
    assert seen["accept"] == "application/json"
    assert seen["timeout"] == 7
    assert seen["method"] == "GET"
    assert DUMMY_CREDENTIAL not in str(seen["url"])
    assert body == '[{"date":"2024-01-02"}]'


def test_call_rejects_non_200_response_status() -> None:
    transport = TiingoEodNetworkTransport(
        urlopen=lambda request, timeout: _FakeResponse(b"server body", status=503),
    )

    with pytest.raises(ValueError) as exc_info:
        transport(_request(), DUMMY_CREDENTIAL)

    message = str(exc_info.value)
    assert "non-200" in message
    assert DUMMY_CREDENTIAL not in message
    assert "server body" not in message


def test_call_converts_http_error_to_value_error_without_secret() -> None:
    def fake_urlopen(network_request, timeout: int):
        raise urllib.error.HTTPError(
            network_request.full_url,
            401,
            "Unauthorized",
            hdrs=None,
            fp=None,
        )

    transport = TiingoEodNetworkTransport(urlopen=fake_urlopen)

    with pytest.raises(ValueError) as exc_info:
        transport(_request(), DUMMY_CREDENTIAL)

    assert "HTTP error" in str(exc_info.value)
    assert DUMMY_CREDENTIAL not in str(exc_info.value)


def test_call_converts_url_error_to_value_error_without_secret() -> None:
    transport = TiingoEodNetworkTransport(
        urlopen=lambda request, timeout: (_ for _ in ()).throw(
            urllib.error.URLError("network unavailable")
        ),
    )

    with pytest.raises(ValueError) as exc_info:
        transport(_request(), DUMMY_CREDENTIAL)

    assert "URL error" in str(exc_info.value)
    assert DUMMY_CREDENTIAL not in str(exc_info.value)


def test_call_rejects_response_body_containing_raw_credential() -> None:
    body = f'[{{"leak":"{DUMMY_CREDENTIAL}"}}]'.encode("utf-8")
    transport = TiingoEodNetworkTransport(
        urlopen=lambda request, timeout: _FakeResponse(body),
    )

    with pytest.raises(ValueError, match="must not contain raw credential"):
        transport(_request(), DUMMY_CREDENTIAL)


def test_call_does_not_mutate_request() -> None:
    request = _request()
    before = repr(request)
    transport = TiingoEodNetworkTransport(
        urlopen=lambda request, timeout: _FakeResponse(b"[]"),
    )

    transport(request, DUMMY_CREDENTIAL)

    assert repr(request) == before


def test_transport_file_does_not_contain_forbidden_imports() -> None:
    tree = ast.parse(TRANSPORT_PATH.read_text(encoding="utf-8"))
    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.add(node.module)

    forbidden_imports = {
        "os",
        "pathlib",
        "csv",
        "json",
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
        "app.domain.managed_api_eod_record",
        "app.domain.managed_api_fetch_result",
        "app.data.tiingo_eod_adapter",
    }

    assert imported_modules.isdisjoint(forbidden_imports)


def test_transport_file_does_not_contain_forbidden_runtime_surfaces() -> None:
    content = TRANSPORT_PATH.read_text(encoding="utf-8")
    forbidden_snippets = [
        "os.environ",
        "print(",
        "requests.",
        "httpx.",
        "aiohttp.",
        "pandas",
        "numpy",
        "yfinance",
        "sqlalchemy",
        "dotenv",
        "DailyMarketData",
        "ManagedApiEodRecord",
        "ManagedApiEodFetchResult",
        "json.loads",
        "parse_tiingo_eod_prices_response",
        "Data Quality Gate",
        "engine execution",
        "market analysis",
        "financial conclusion",
        ".write(",
    ]

    for snippet in forbidden_snippets:
        assert snippet not in content


def test_tests_use_fake_urlopen_only() -> None:
    content = TEST_PATH.read_text(encoding="utf-8")
    real_urlopen_reference = "urllib.request." + "urlopen"
    http_url_prefix = "http" + "://"

    assert real_urlopen_reference not in content
    assert http_url_prefix not in content


def test_public_docs_contain_network_transport_boundaries() -> None:
    roadmap = (REPO_ROOT / "docs" / "PUBLIC_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    required_phrases = [
        "Tiingo planning/test boundaries",
        "fake transports",
        "injected callables",
        "No real Tiingo response payload",
        "No external provider access is approved by this public release",
        "must not read `.env`",
        "store raw credentials",
        "verify provider access",
        "provider validation artifact is included",
    ]

    for phrase in required_phrases:
        assert phrase in roadmap
