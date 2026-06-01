from pathlib import Path

from app.domain.confidence_contract import DailyConfidence
from app.domain.data_contract import DailyMarketData
from app.domain.feature_contract import DailyFeatures
from app.domain.market_phase_contract import DailyMarketPhase
from app.domain.score_contract import DailyScore
from app.domain.signal_contract import DailySignals
from app.domain.validation_parameters import ValidationParameters
from app.domain.validation_result_contract import DailyValidationResult
from app.engine.confidence import compute_daily_confidence
from app.engine.features import compute_daily_features
from app.engine.market_phase import compute_daily_market_phases
from app.engine.scoring import compute_daily_scores
from app.engine.signals import compute_daily_signals
from app.engine.validation import (
    compute_false_signal_detection,
    compute_forward_validation,
    compute_stability_check,
    compute_validation_results,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = REPO_ROOT / "app"


def _python_files(path: Path) -> list[Path]:
    return [
        file_path
        for file_path in path.rglob("*.py")
        if "__pycache__" not in file_path.parts and ".venv" not in file_path.parts
    ]


def test_phase1_required_engine_functions_exist() -> None:
    required_functions = [
        compute_daily_features,
        compute_daily_signals,
        compute_daily_scores,
        compute_daily_market_phases,
        compute_daily_confidence,
        compute_forward_validation,
        compute_stability_check,
        compute_false_signal_detection,
        compute_validation_results,
    ]

    assert all(callable(function) for function in required_functions)


def test_phase1_required_domain_contracts_exist() -> None:
    required_contracts = [
        DailyMarketData,
        DailyFeatures,
        DailySignals,
        DailyScore,
        DailyMarketPhase,
        DailyConfidence,
        ValidationParameters,
        DailyValidationResult,
    ]

    assert all(isinstance(contract.__name__, str) for contract in required_contracts)


def test_phase1_forbidden_production_surfaces_are_absent() -> None:
    api_files = _python_files(APP_ROOT / "api")
    data_files = _python_files(APP_ROOT / "data")
    services_files = _python_files(APP_ROOT / "services")
    allowed_data_files = {
        APP_ROOT / "data" / "__init__.py",
        APP_ROOT / "data" / "local_csv_batch_run.py",
        APP_ROOT / "data" / "local_csv_ingestion.py",
        APP_ROOT / "data" / "local_csv_quality_validation.py",
        APP_ROOT / "data" / "managed_api_credentials.py",
        APP_ROOT / "data" / "managed_api_fetch_preflight.py",
        APP_ROOT / "data" / "managed_api_provider_access_verification_gate.py",
        APP_ROOT / "data" / "managed_api_provider_documentation_evidence_gate.py",
        APP_ROOT / "data" / "managed_api_runtime_credentials.py",
        APP_ROOT / "data" / "quality_evaluation.py",
        APP_ROOT / "data" / "quality_gate.py",
        APP_ROOT / "data" / "source_evaluation.py",
        APP_ROOT / "data" / "tiingo_eod_adapter.py",
        APP_ROOT / "data" / "tiingo_eod_network_transport.py",
        APP_ROOT / "data" / "tiingo_eod_response_parser.py",
        APP_ROOT / "data" / "tiingo_provider_metadata_factory.py",
    }
    forbidden_data_module_terms = [
        "client",
        "database",
        "download",
        "fetch",
        "ingest",
        "ingestion",
        "loader",
        "pipeline",
        "reader",
        "vendor",
    ]

    assert api_files == [APP_ROOT / "api" / "__init__.py"]
    assert set(data_files) <= allowed_data_files
    assert not any(
        forbidden_term in file_path.stem
        for file_path in data_files
        if file_path not in allowed_data_files
        for forbidden_term in forbidden_data_module_terms
    )
    assert services_files == [APP_ROOT / "services" / "__init__.py"]

    forbidden_paths = [
        REPO_ROOT / "ui",
        REPO_ROOT / "frontend",
        REPO_ROOT / "client",
        REPO_ROOT / "web",
        APP_ROOT / "ui",
        APP_ROOT / "ingestion",
        APP_ROOT / "database",
        APP_ROOT / "db",
        APP_ROOT / "pipelines",
        APP_ROOT / "pipeline",
    ]
    forbidden_frontend_files = [
        REPO_ROOT / "package.json",
        REPO_ROOT / "package-lock.json",
        REPO_ROOT / "pnpm-lock.yaml",
        REPO_ROOT / "yarn.lock",
        REPO_ROOT / "vite.config.js",
        REPO_ROOT / "vite.config.ts",
        REPO_ROOT / "next.config.js",
        REPO_ROOT / "next.config.ts",
    ]

    assert not any(path.exists() for path in forbidden_paths)
    assert not any(path.exists() for path in forbidden_frontend_files)


def test_phase1_forbidden_dependency_imports_are_absent_from_app_code() -> None:
    forbidden_imports = ["pandas", "numpy", "yfinance", "requests", "sqlalchemy"]

    for file_path in _python_files(APP_ROOT):
        content = file_path.read_text(encoding="utf-8")
        for package_name in forbidden_imports:
            assert f"import {package_name}" not in content
            assert f"from {package_name}" not in content


def test_public_docs_contain_required_foundation_safety_statements() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    roadmap = (REPO_ROOT / "docs" / "PUBLIC_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    public_docs = f"{readme}\n{roadmap}"

    assert "Validation result contracts and in-memory validation utility" in public_docs
    assert "No real market dataset is included" in public_docs
    assert "No real data conclusions are produced" in public_docs
    assert "Not an entry or exit recommendation service" in public_docs
