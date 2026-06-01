from datetime import date, timedelta
from pathlib import Path

import pytest

from app.domain.managed_api_provider_documentation_evidence import (
    ManagedApiDocumentationEvidenceStatus,
    ManagedApiProviderDocumentationEvidence,
)


CONTRACT_PATH = Path("app/domain/managed_api_provider_documentation_evidence.py")


def _evidence(**overrides: object) -> ManagedApiProviderDocumentationEvidence:
    values = {
        "provider_name": "Documentation Evidence Provider",
        "evidence_status": ManagedApiDocumentationEvidenceStatus.DOCUMENTED,
        "documentation_reference": "Provider documentation reference recorded by caller.",
        "documentation_retrieved_date": date.today(),
        "supports_eod_ohlcv_evidence": "Caller-supplied EOD OHLCV evidence text.",
        "supports_adjusted_prices_evidence": (
            "Caller-supplied adjusted prices evidence text."
        ),
        "supports_corporate_actions_evidence": (
            "Caller-supplied corporate actions evidence text."
        ),
        "supported_asset_classes_evidence": (
            "Caller-supplied supported asset classes evidence text."
        ),
        "rate_limit_evidence": "Caller-supplied rate limit evidence text.",
        "legal_access_evidence": "Caller-supplied legal access evidence text.",
        "notes": "Evidence contract shape test only.",
    }
    values.update(overrides)
    return ManagedApiProviderDocumentationEvidence(**values)


def test_valid_documentation_evidence_passes_with_explicit_fields() -> None:
    evidence = _evidence()

    assert evidence.evidence_status is ManagedApiDocumentationEvidenceStatus.DOCUMENTED


def test_constructor_requires_explicit_values_and_has_no_defaults() -> None:
    with pytest.raises(TypeError):
        ManagedApiProviderDocumentationEvidence()


def test_empty_provider_name_raises_value_error() -> None:
    with pytest.raises(ValueError, match="provider_name must not be empty"):
        _evidence(provider_name=" ")


def test_invalid_evidence_status_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="evidence_status must be a valid ManagedApiDocumentationEvidenceStatus value",
    ):
        _evidence(evidence_status="DOCUMENTED")


def test_empty_documentation_reference_raises_value_error() -> None:
    with pytest.raises(ValueError, match="documentation_reference must not be empty"):
        _evidence(documentation_reference="")


def test_future_documentation_retrieved_date_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="documentation_retrieved_date must not be in the future",
    ):
        _evidence(documentation_retrieved_date=date.today() + timedelta(days=1))


def test_empty_supports_eod_ohlcv_evidence_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="supports_eod_ohlcv_evidence must not be empty",
    ):
        _evidence(supports_eod_ohlcv_evidence=" ")


def test_empty_supports_adjusted_prices_evidence_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="supports_adjusted_prices_evidence must not be empty",
    ):
        _evidence(supports_adjusted_prices_evidence="")


def test_empty_supports_corporate_actions_evidence_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="supports_corporate_actions_evidence must not be empty",
    ):
        _evidence(supports_corporate_actions_evidence=" ")


def test_empty_supported_asset_classes_evidence_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="supported_asset_classes_evidence must not be empty",
    ):
        _evidence(supported_asset_classes_evidence="")


def test_empty_rate_limit_evidence_raises_value_error() -> None:
    with pytest.raises(ValueError, match="rate_limit_evidence must not be empty"):
        _evidence(rate_limit_evidence=" ")


def test_empty_legal_access_evidence_raises_value_error() -> None:
    with pytest.raises(ValueError, match="legal_access_evidence must not be empty"):
        _evidence(legal_access_evidence="")


def test_empty_notes_raises_value_error() -> None:
    with pytest.raises(ValueError, match="notes must not be empty"):
        _evidence(notes=" ")


def test_contract_file_does_not_contain_forbidden_imports() -> None:
    source = CONTRACT_PATH.read_text(encoding="utf-8")

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


def test_contract_file_does_not_import_blocked_internal_boundaries() -> None:
    source = CONTRACT_PATH.read_text(encoding="utf-8")

    blocked_terms = [
        "app.data",
        "app.engine",
        "DailyMarketData",
        "ManagedApiProviderAdapterPort",
        "ManagedApiEodFetchRequest",
        "ManagedApiEodFetchResult",
        "ManagedApiEodRecord",
    ]

    for blocked_term in blocked_terms:
        assert blocked_term not in source


def test_contract_file_does_not_contain_forbidden_behavior_language() -> None:
    source = CONTRACT_PATH.read_text(encoding="utf-8")

    forbidden_terms = [
        "API client",
        "os.environ",
        "environ",
        ".env",
        "read_text",
        "open(",
        "fetch(",
        "parse",
        "response",
        "ingest",
        "persist",
        "engine execution",
        "financial conclusion",
    ]

    for forbidden_term in forbidden_terms:
        assert forbidden_term not in source
