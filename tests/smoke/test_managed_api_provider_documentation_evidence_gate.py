from datetime import date
from pathlib import Path

import pytest

from app.data.managed_api_provider_documentation_evidence_gate import (
    can_use_provider_documentation_evidence_for_planning,
)
from app.domain.managed_api_provider_documentation_evidence import (
    ManagedApiDocumentationEvidenceStatus,
    ManagedApiProviderDocumentationEvidence,
)


GATE_PATH = Path("app/data/managed_api_provider_documentation_evidence_gate.py")


def _evidence(
    **overrides: object,
) -> ManagedApiProviderDocumentationEvidence:
    values = {
        "provider_name": "Documentation Evidence Provider",
        "evidence_status": ManagedApiDocumentationEvidenceStatus.DOCUMENTED,
        "documentation_reference": "Caller supplied provider documentation reference.",
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
        "notes": "Evidence gate test record.",
    }
    values.update(overrides)
    return ManagedApiProviderDocumentationEvidence(**values)


def test_documented_complete_evidence_returns_true() -> None:
    result = can_use_provider_documentation_evidence_for_planning(_evidence())

    assert result is True


def test_missing_evidence_returns_false() -> None:
    result = can_use_provider_documentation_evidence_for_planning(
        _evidence(evidence_status=ManagedApiDocumentationEvidenceStatus.MISSING)
    )

    assert result is False


def test_conflicting_evidence_returns_false() -> None:
    result = can_use_provider_documentation_evidence_for_planning(
        _evidence(evidence_status=ManagedApiDocumentationEvidenceStatus.CONFLICTING)
    )

    assert result is False


def test_unverified_evidence_returns_false() -> None:
    result = can_use_provider_documentation_evidence_for_planning(
        _evidence(evidence_status=ManagedApiDocumentationEvidenceStatus.UNVERIFIED)
    )

    assert result is False


def test_invalid_input_type_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="evidence must be a ManagedApiProviderDocumentationEvidence instance",
    ):
        can_use_provider_documentation_evidence_for_planning("evidence")


def test_function_returns_bool() -> None:
    result = can_use_provider_documentation_evidence_for_planning(_evidence())

    assert type(result) is bool


def test_function_does_not_mutate_evidence_object() -> None:
    evidence = _evidence()
    before = _evidence()

    can_use_provider_documentation_evidence_for_planning(evidence)

    assert evidence == before


def test_gate_file_does_not_contain_forbidden_imports() -> None:
    source = GATE_PATH.read_text(encoding="utf-8")

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


def test_gate_file_does_not_import_blocked_internal_boundaries() -> None:
    source = GATE_PATH.read_text(encoding="utf-8")

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


def test_gate_file_does_not_contain_forbidden_behavior_language() -> None:
    source = GATE_PATH.read_text(encoding="utf-8")

    forbidden_terms = [
        "API client",
        "os.environ",
        "environ",
        ".env",
        "load",
        "credentials",
        "verify",
        "provider access",
        "Tiingo",
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
