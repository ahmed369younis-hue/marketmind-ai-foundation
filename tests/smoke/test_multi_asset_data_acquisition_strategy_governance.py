from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
STRATEGY_PATH = REPO_ROOT / "docs" / "MULTI_ASSET_DATA_ACQUISITION_STRATEGY.md"
ROADMAP_PATH = REPO_ROOT / "docs" / "PUBLIC_ROADMAP.md"


def _strategy_text() -> str:
    return STRATEGY_PATH.read_text(encoding="utf-8")


def test_multi_asset_strategy_document_exists() -> None:
    assert STRATEGY_PATH.is_file()


def test_strategy_records_coverage_and_current_first_execution_market() -> None:
    strategy = _strategy_text()

    for text in ["Gold", "Oil", "Bitcoin", "EUR/USD"]:
        assert text in strategy

    assert (
        "US Equities / ETFs remain the first execution market using Daily EOD local CSV"
        in strategy
    )
    assert "strategy and governance only, not implementation" in strategy


def test_strategy_records_future_multi_asset_scope_only() -> None:
    strategy = _strategy_text()

    assert "Future multi-asset planning covers" in strategy
    for text in ["Gold", "Oil", "Bitcoin", "EUR/USD"]:
        assert text in strategy

    assert "Asset-specific requirements must exist before multi-asset implementation" in strategy


def test_strategy_includes_required_data_source_tiers() -> None:
    strategy = _strategy_text()

    required_tiers = [
        "Tier 0: Synthetic/public-safe fixtures for tests only",
        "Tier 1: Local CSV validation path",
        "Tier 2: ETF proxy path",
        "Tier 3: Direct institutional data providers",
        "Tier 4: Cross-check providers",
        "Tier 5: Future internal curated datasets",
    ]

    for tier in required_tiers:
        assert tier in strategy


def test_strategy_records_asset_specific_differences() -> None:
    strategy = _strategy_text()

    assert "Gold futures later require contract expiry and roll logic" in strategy
    assert "Oil futures later require contract expiry, roll logic" in strategy
    assert "Requires 24/7 calendar handling" in strategy
    assert "Requires volume fragmentation handling" in strategy
    assert "Requires cross-exchange validation before reliability claims" in strategy
    assert "Must not treat FX volume like centralized equity volume" in strategy
    assert "non-centralized-volume or liquidity-proxy policy" in strategy


def test_strategy_records_provider_and_quality_gate_non_approval_boundaries() -> None:
    strategy = _strategy_text()

    required_text = [
        "No provider is approved by this document",
        "No vendor is selected by this document",
        "documentation-evidence-gated candidates",
        "documentation evidence",
        "legal credential/access confirmation",
        "source metadata evaluation",
        "fetch preflight",
        "response parsing",
        "data quality evaluation",
        "Data Quality Gate",
        "No metadata or credential presence may imply source reliability approval",
        "No Data Quality Gate pass alone may imply historical verification or production approval",
    ]

    for text in required_text:
        assert text in strategy


def test_strategy_links_cross_source_policy_and_evaluation_gate_boundaries() -> None:
    strategy = _strategy_text()

    required_text = [
        "cross-source validation policy contract exists for future planning",
        "cross-source validation policy evaluation gate exists for metadata-only planning readiness only",
        "metadata-only planning",
        "They do not:",
        "validate real data",
        "select or approve any provider",
        "approve source reliability",
        "verify historical reliability",
        "assign VERIFIED_HISTORICAL",
        "approve production use",
        "run ingestion",
        "execute the Data Quality Gate",
        "run engine logic",
        "produce market analysis",
        "trading output",
        "buy/sell output",
        "financial conclusions",
    ]

    for text in required_text:
        assert text in strategy


def test_strategy_includes_data_quality_requirements() -> None:
    strategy = _strategy_text()

    required_text = [
        "schema validation",
        "date/time validation",
        "missing data checks",
        "duplicate record checks",
        "OHLC relationship checks",
        "adjusted/unadjusted price policy",
        "timezone/session/calendar validation",
        "source consistency and cross-check rules",
        "gap and coverage reporting",
        "evidence report generation",
    ]

    for text in required_text:
        assert text in strategy


def test_strategy_forbids_implementation_and_market_output_surfaces() -> None:
    strategy = _strategy_text()

    required_text = [
        "API call implementation",
        "real data download",
        "provider response fixtures from real APIs",
        "persistence",
        "database",
        "engine execution",
        "signals, scores, phase, or confidence output",
        "buy/sell/trading output",
        "market analysis",
        "financial conclusions",
        "production approval",
        "source reliability approval",
        "VERIFIED_HISTORICAL classification",
    ]

    for text in required_text:
        assert text in strategy


def test_strategy_does_not_imply_production_or_real_data_readiness() -> None:
    strategy = _strategy_text()

    forbidden_text = [
        "production-ready",
        "real-data ready",
        "real datasets exist",
        "providers are selected",
        "providers are approved",
        "system can already analyze live markets",
        "live market analysis",
    ]

    for text in forbidden_text:
        assert text not in strategy.lower()


def test_strategy_records_future_implementation_gates() -> None:
    strategy = _strategy_text()

    required_text = [
        "Local CSV path must remain first",
        "Real local CSV batch execution must be separately scoped",
        "Managed API fetch must be separately scoped",
        "Provider access verification must be separately scoped",
        "Real-data ingestion must be separately scoped",
        "Engine execution must require explicit future approval after quality validation",
    ]

    for text in required_text:
        assert text in strategy


def test_strategy_document_does_not_contain_code_like_behavior() -> None:
    strategy = _strategy_text()

    forbidden_line_prefixes = [
        "import ",
        "from ",
        "def ",
        "class ",
        "return ",
    ]
    forbidden_inline_terms = [
        "pip install",
        "python -m",
        "curl ",
    ]

    for line in strategy.splitlines():
        stripped_line = line.strip()
        for text in forbidden_line_prefixes:
            assert not stripped_line.startswith(text)

    for text in forbidden_inline_terms:
        assert text not in strategy


def test_strategy_does_not_introduce_forbidden_dependency_terms() -> None:
    combined_text = f"{_strategy_text()}\n{ROADMAP_PATH.read_text(encoding='utf-8')}"

    for package_name in ["pandas", "numpy", "yfinance", "requests", "sqlalchemy"]:
        assert package_name not in combined_text


def test_public_roadmap_links_strategy_without_claiming_implementation() -> None:
    roadmap = ROADMAP_PATH.read_text(encoding="utf-8")

    assert "docs/MULTI_ASSET_DATA_ACQUISITION_STRATEGY.md" in roadmap
    assert "as governance only" in roadmap
