from datetime import date
from pathlib import Path

import pytest

from app.data.tiingo_provider_metadata_factory import (
    build_tiingo_provider_contract_from_documentation_evidence,
)
from app.domain.data_source_contract import (
    DataGranularity,
    DataSourceReliability,
    DataSourceType,
)
from app.domain.managed_api_provider_contract import (
    ManagedApiProviderContract,
    ManagedApiProviderType,
)
from app.domain.managed_api_provider_documentation_evidence import (
    ManagedApiDocumentationEvidenceStatus,
    ManagedApiProviderDocumentationEvidence,
)


FACTORY_PATH = Path("app/data/tiingo_provider_metadata_factory.py")


def _evidence(
    **overrides: object,
) -> ManagedApiProviderDocumentationEvidence:
    values = {
        "provider_name": "Tiingo",
        "evidence_status": ManagedApiDocumentationEvidenceStatus.DOCUMENTED,
        "documentation_reference": "Caller supplied Tiingo documentation reference.",
        "documentation_retrieved_date": date.today(),
        "supports_eod_ohlcv_evidence": "Caller supplied EOD OHLCV evidence.",
        "supports_adjusted_prices_evidence": (
            "Caller supplied adjusted prices evidence."
        ),
        "supports_corporate_actions_evidence": (
            "Caller supplied corporate actions evidence."
        ),
        "supported_asset_classes_evidence": (
            "Caller supplied supported asset classes evidence."
        ),
        "rate_limit_evidence": "Caller supplied rate limit evidence.",
        "legal_access_evidence": "Caller supplied legal access evidence.",
        "notes": "Documentation evidence for metadata planning only.",
    }
    values.update(overrides)
    return ManagedApiProviderDocumentationEvidence(**values)


def test_complete_documented_evidence_creates_provider_contract() -> None:
    provider = build_tiingo_provider_contract_from_documentation_evidence(
        _evidence()
    )

    assert isinstance(provider, ManagedApiProviderContract)


def test_provider_name_is_tiingo() -> None:
    provider = build_tiingo_provider_contract_from_documentation_evidence(
        _evidence()
    )

    assert provider.provider_name == "Tiingo"


def test_provider_type_is_secondary_cross_check() -> None:
    provider = build_tiingo_provider_contract_from_documentation_evidence(
        _evidence()
    )

    assert provider.provider_type is ManagedApiProviderType.SECONDARY_CROSS_CHECK


def test_source_type_is_real() -> None:
    provider = build_tiingo_provider_contract_from_documentation_evidence(
        _evidence()
    )

    assert provider.source.source_type is DataSourceType.REAL


def test_source_granularity_is_daily() -> None:
    provider = build_tiingo_provider_contract_from_documentation_evidence(
        _evidence()
    )

    assert provider.source.granularity is DataGranularity.DAILY


def test_source_reliability_is_structure_only_not_historical() -> None:
    provider = build_tiingo_provider_contract_from_documentation_evidence(
        _evidence()
    )

    assert provider.source.reliability is DataSourceReliability.VERIFIED_STRUCTURE_ONLY
    assert provider.source.reliability is not DataSourceReliability.VERIFIED_HISTORICAL


def test_credential_env_var_is_tiingo_api_key() -> None:
    provider = build_tiingo_provider_contract_from_documentation_evidence(
        _evidence()
    )

    assert provider.credential_env_var == "TIINGO_API_KEY"


def test_allowed_first_symbol_is_spy() -> None:
    provider = build_tiingo_provider_contract_from_documentation_evidence(
        _evidence()
    )

    assert provider.allowed_first_symbol == "SPY"


def test_eod_ohlcv_support_is_true() -> None:
    provider = build_tiingo_provider_contract_from_documentation_evidence(
        _evidence()
    )

    assert provider.supports_eod_ohlcv is True


def test_adjusted_prices_support_is_true() -> None:
    provider = build_tiingo_provider_contract_from_documentation_evidence(
        _evidence()
    )

    assert provider.supports_adjusted_prices is True


def test_corporate_actions_support_is_true() -> None:
    provider = build_tiingo_provider_contract_from_documentation_evidence(
        _evidence()
    )

    assert provider.supports_corporate_actions is True


def test_us_equities_support_is_true() -> None:
    provider = build_tiingo_provider_contract_from_documentation_evidence(
        _evidence()
    )

    assert provider.supports_us_equities is True


def test_us_etfs_support_is_true() -> None:
    provider = build_tiingo_provider_contract_from_documentation_evidence(
        _evidence()
    )

    assert provider.supports_us_etfs is True


def test_fx_support_is_false() -> None:
    provider = build_tiingo_provider_contract_from_documentation_evidence(
        _evidence()
    )

    assert provider.supports_fx is False


def test_commodities_support_is_false() -> None:
    provider = build_tiingo_provider_contract_from_documentation_evidence(
        _evidence()
    )

    assert provider.supports_commodities is False


def test_crypto_support_is_false() -> None:
    provider = build_tiingo_provider_contract_from_documentation_evidence(
        _evidence()
    )

    assert provider.supports_crypto is False


def test_rate_limit_notes_equal_evidence_rate_limit_evidence() -> None:
    evidence = _evidence(rate_limit_evidence="Explicit rate limit documentation.")

    provider = build_tiingo_provider_contract_from_documentation_evidence(
        evidence
    )

    assert provider.rate_limit_notes == evidence.rate_limit_evidence


@pytest.mark.parametrize(
    "status",
    [
        ManagedApiDocumentationEvidenceStatus.MISSING,
        ManagedApiDocumentationEvidenceStatus.CONFLICTING,
        ManagedApiDocumentationEvidenceStatus.UNVERIFIED,
    ],
)
def test_incomplete_evidence_status_raises_value_error(
    status: ManagedApiDocumentationEvidenceStatus,
) -> None:
    with pytest.raises(
        ValueError,
        match="provider documentation evidence is not sufficient for planning",
    ):
        build_tiingo_provider_contract_from_documentation_evidence(
            _evidence(evidence_status=status)
        )


def test_invalid_input_type_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="evidence must be a ManagedApiProviderDocumentationEvidence instance",
    ):
        build_tiingo_provider_contract_from_documentation_evidence("evidence")


def test_factory_does_not_mutate_evidence_object() -> None:
    evidence = _evidence()
    before = _evidence()

    build_tiingo_provider_contract_from_documentation_evidence(evidence)

    assert evidence == before


def test_factory_file_does_not_contain_forbidden_imports() -> None:
    source = FACTORY_PATH.read_text(encoding="utf-8")

    forbidden_imports = [
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
    ]

    for forbidden_import in forbidden_imports:
        assert forbidden_import not in source


def test_factory_file_does_not_import_blocked_internal_boundaries() -> None:
    source = FACTORY_PATH.read_text(encoding="utf-8")

    blocked_terms = [
        "app.engine",
        "DailyMarketData",
        "ManagedApiProviderAdapterPort",
        "ManagedApiEodFetchRequest",
        "ManagedApiEodFetchResult",
        "ManagedApiEodRecord",
    ]

    for blocked_term in blocked_terms:
        assert blocked_term not in source


def test_factory_file_does_not_contain_forbidden_behavior_language() -> None:
    source = FACTORY_PATH.read_text(encoding="utf-8")

    forbidden_terms = [
        "API client",
        "os.environ",
        "environ",
        ".env",
        "load",
        "credentials",
        "provider access",
        "adapter",
        "parse",
        "response",
        "DailyMarketData",
        "ingest",
        "persist",
        "Data Quality Gate",
        "engine execution",
        "financial conclusion",
        "fetch",
        "read_text",
        "open(",
    ]

    for forbidden_term in forbidden_terms:
        assert forbidden_term not in source
