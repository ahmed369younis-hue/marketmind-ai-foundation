import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = REPO_ROOT / "scripts" / "run_first_real_tiingo_spy_fetch.py"


def _runner_source() -> str:
    return RUNNER_PATH.read_text(encoding="utf-8")


def _imported_modules() -> set[str]:
    tree = ast.parse(_runner_source())
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.add(node.module)

    return imported_modules


def test_runner_file_exists_and_is_hardcoded_to_first_spy_fetch_scope() -> None:
    source = _runner_source()

    assert RUNNER_PATH.exists()
    assert '"SPY"' in source
    assert "2024-01-02" in source
    assert "2024-01-05" in source
    assert "ManagedApiFetchPricePreference.ADJUSTED" in source
    assert "TiingoEodAdapter" in source
    assert "TiingoEodNetworkTransport" in source
    assert "read_managed_api_credential" in source
    assert source.count("adapter.fetch_eod(request)") == 1


def test_runner_does_not_import_forbidden_dependencies_or_surfaces() -> None:
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
    }

    assert _imported_modules().isdisjoint(forbidden_imports)


def test_runner_does_not_contain_forbidden_runtime_behavior() -> None:
    source = _runner_source()
    forbidden_snippets = [
        "open(",
        ".write(",
        "with open",
        "requests.",
        "httpx.",
        "aiohttp.",
        "pandas",
        "numpy",
        "yfinance",
        "sqlalchemy",
        "dotenv",
        "DailyMarketData",
        "app.engine",
        "database",
        "sqlite",
        "raw_payload",
        "response_body",
        "Authorization",
        "TIINGO_API_KEY",
        "OPEN=",
        "HIGH=",
        "LOW=",
        "CLOSE=",
        "VOLUME=",
    ]

    for snippet in forbidden_snippets:
        assert snippet not in source


def test_runner_prints_only_safe_summary_boundary_flags() -> None:
    source = _runner_source()
    required_flags = [
        "NO_DATA_PERSISTED=True",
        "NO_DAILYMARKETDATA_CONVERSION=True",
        "NO_INGESTION=True",
        "NO_ENGINE_EXECUTION=True",
        "NO_FINANCIAL_CONCLUSIONS=True",
    ]

    for flag in required_flags:
        assert flag in source


def test_public_docs_contain_first_provider_fetch_boundaries() -> None:
    roadmap = (REPO_ROOT / "docs" / "PUBLIC_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    required_phrases = [
        "Tiingo references in the public foundation are planning and test boundaries",
        "No real Tiingo response payload",
        "No provider API response data is included",
        "No external provider access is approved by this public release",
        "ingest API data",
        "persist data",
        "run engine logic",
        "produce market conclusions",
    ]

    for phrase in required_phrases:
        assert phrase in roadmap
