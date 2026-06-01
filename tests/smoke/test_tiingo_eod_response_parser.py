import ast
import json
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from app.data.tiingo_eod_response_parser import parse_tiingo_eod_prices_response
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
from app.domain.managed_api_eod_record import (
    ManagedApiEodRecord,
    ManagedApiPriceMode,
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
PARSER_PATH = REPO_ROOT / "app" / "data" / "tiingo_eod_response_parser.py"


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
        notes="Fixture-only provider metadata for parser tests.",
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
        rate_limit_notes="Fixture rate limit evidence.",
        legal_access_confirmed=True,
        notes="Fixture-only provider metadata for parser tests.",
    )


def _request(
    price_preference: ManagedApiFetchPricePreference,
) -> ManagedApiEodFetchRequest:
    provider = _provider()
    credential_access = ManagedApiCredentialAccessResult(
        provider=provider,
        status=ManagedApiCredentialStatus.AVAILABLE,
        credential_env_var=provider.credential_env_var,
        credential_present=True,
        credential_fingerprint="fixturefp",
        message="Fixture credential access metadata.",
    )
    return ManagedApiEodFetchRequest(
        provider=provider,
        credential_access=credential_access,
        symbol="SPY",
        start_date=date(2024, 1, 2),
        end_date=date(2024, 1, 5),
        price_preference=price_preference,
        timezone="America/New_York",
        purpose="Fixture parser tests only.",
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


def _single_raw_row(**overrides: object) -> str:
    row = {
        "date": "2024-01-02T00:00:00.000Z",
        "open": 470.0,
        "high": 475.0,
        "low": 468.0,
        "close": 474.0,
        "volume": 1000,
    }
    row.update(overrides)
    return json.dumps([row])


def test_raw_fixture_payload_parses_into_managed_api_eod_records() -> None:
    request = _request(ManagedApiFetchPricePreference.RAW)

    records = parse_tiingo_eod_prices_response(_raw_payload(), request)

    assert all(isinstance(record, ManagedApiEodRecord) for record in records)
    assert [record.price_mode for record in records] == [
        ManagedApiPriceMode.RAW,
        ManagedApiPriceMode.RAW,
    ]
    assert all(record.adjusted_close is None for record in records)
    assert all(record.corporate_action_adjusted is False for record in records)


def test_adjusted_fixture_payload_uses_adjusted_fields() -> None:
    request = _request(ManagedApiFetchPricePreference.ADJUSTED)

    records = parse_tiingo_eod_prices_response(_adjusted_payload(), request)

    assert all(isinstance(record, ManagedApiEodRecord) for record in records)
    assert records[0].price_mode is ManagedApiPriceMode.ADJUSTED
    assert records[0].open == 469.0
    assert records[0].high == 474.0
    assert records[0].low == 467.0
    assert records[0].close == 473.0
    assert records[0].volume == 1200.0
    assert records[0].adjusted_close == 473.0
    assert records[0].corporate_action_adjusted is True


def test_provider_symbol_and_timezone_are_preserved_from_request() -> None:
    request = _request(ManagedApiFetchPricePreference.RAW)

    records = parse_tiingo_eod_prices_response(_raw_payload(), request)

    assert all(record.provider_name == request.provider.provider_name for record in records)
    assert all(record.symbol == request.symbol for record in records)
    assert all(record.timezone == request.timezone for record in records)


@pytest.mark.parametrize(
    "payload",
    [
        "[]",
        "{bad json",
        "{}",
        json.dumps([1]),
    ],
)
def test_invalid_payload_shape_raises_value_error(payload: str) -> None:
    request = _request(ManagedApiFetchPricePreference.RAW)

    with pytest.raises(ValueError):
        parse_tiingo_eod_prices_response(payload, request)


def test_missing_required_raw_field_raises_value_error() -> None:
    request = _request(ManagedApiFetchPricePreference.RAW)
    payload = json.dumps(
        [
            {
                "date": "2024-01-02T00:00:00.000Z",
                "high": 475.0,
                "low": 468.0,
                "close": 474.0,
                "volume": 1000,
            }
        ]
    )

    with pytest.raises(ValueError):
        parse_tiingo_eod_prices_response(payload, request)


def test_missing_required_adjusted_field_raises_value_error() -> None:
    request = _request(ManagedApiFetchPricePreference.ADJUSTED)
    payload = json.dumps(
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
                "adjVolume": 1200,
            }
        ]
    )

    with pytest.raises(ValueError):
        parse_tiingo_eod_prices_response(payload, request)


def test_malformed_date_raises_value_error() -> None:
    request = _request(ManagedApiFetchPricePreference.RAW)

    with pytest.raises(ValueError):
        parse_tiingo_eod_prices_response(_single_raw_row(date="bad-date"), request)


def test_row_outside_request_date_range_raises_value_error() -> None:
    request = _request(ManagedApiFetchPricePreference.RAW)

    with pytest.raises(ValueError):
        parse_tiingo_eod_prices_response(
            _single_raw_row(date="2024-01-01T00:00:00.000Z"),
            request,
        )


def test_duplicate_dates_raise_value_error() -> None:
    request = _request(ManagedApiFetchPricePreference.RAW)
    payload = json.dumps(
        [
            json.loads(_single_raw_row())[0],
            json.loads(_single_raw_row())[0],
        ]
    )

    with pytest.raises(ValueError):
        parse_tiingo_eod_prices_response(payload, request)


def test_non_numeric_ohlcv_field_raises_value_error() -> None:
    request = _request(ManagedApiFetchPricePreference.RAW)

    with pytest.raises(ValueError):
        parse_tiingo_eod_prices_response(_single_raw_row(open="470.0"), request)


def test_negative_volume_raises_value_error() -> None:
    request = _request(ManagedApiFetchPricePreference.RAW)

    with pytest.raises(ValueError):
        parse_tiingo_eod_prices_response(_single_raw_row(volume=-1), request)


def test_invalid_ohlc_relationship_raises_value_error() -> None:
    request = _request(ManagedApiFetchPricePreference.RAW)

    with pytest.raises(ValueError):
        parse_tiingo_eod_prices_response(_single_raw_row(high=469.0), request)


def test_parser_preserves_payload_order_and_does_not_sort_silently() -> None:
    request = _request(ManagedApiFetchPricePreference.RAW)
    payload = json.dumps(
        [
            {
                "date": "2024-01-04T00:00:00.000Z",
                "open": 470.0,
                "high": 475.0,
                "low": 468.0,
                "close": 474.0,
                "volume": 1000,
            },
            {
                "date": "2024-01-02T00:00:00.000Z",
                "open": 471.0,
                "high": 476.0,
                "low": 469.0,
                "close": 475.0,
                "volume": 1100,
            },
        ]
    )

    records = parse_tiingo_eod_prices_response(payload, request)

    assert [record.date for record in records] == [
        date(2024, 1, 4),
        date(2024, 1, 2),
    ]


def test_parser_does_not_mutate_request_object() -> None:
    request = _request(ManagedApiFetchPricePreference.RAW)
    before = repr(request)

    parse_tiingo_eod_prices_response(_raw_payload(), request)

    assert repr(request) == before


def test_parser_file_does_not_contain_forbidden_imports() -> None:
    tree = ast.parse(PARSER_PATH.read_text(encoding="utf-8"))
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
        "app.domain.managed_api_provider_adapter_port",
        "app.domain.managed_api_fetch_result",
    }

    assert imported_modules.isdisjoint(forbidden_imports)


def test_parser_file_does_not_contain_forbidden_behavior_language() -> None:
    content = PARSER_PATH.read_text(encoding="utf-8")
    forbidden_snippets = [
        "os.environ",
        ".env",
        "credential",
        "requests.",
        "httpx.",
        "aiohttp.",
        "Data Quality Gate",
        "DailyMarketData",
        "ManagedApiProviderAdapterPort",
        "ManagedApiEodFetchResult",
        "market analysis",
        "financial conclusion",
        "open(",
        ".write(",
    ]

    for snippet in forbidden_snippets:
        assert snippet not in content


def test_public_docs_contain_parser_section_and_boundaries() -> None:
    roadmap = (REPO_ROOT / "docs" / "PUBLIC_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    required_phrases = [
        "Tiingo planning/test boundaries",
        "fixture payloads",
        "No real Tiingo response payload",
        "No real provider API response is included",
        "ingest API data",
        "persist data",
        "run engine logic",
        "produce market conclusions",
    ]

    for phrase in required_phrases:
        assert phrase in roadmap
