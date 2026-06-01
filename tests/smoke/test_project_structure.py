from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


REQUIRED_FILES = [
    "README.md",
    ".gitignore",
    ".env.example",
    "LICENSE",
    "SECURITY.md",
    "docs/PUBLIC_ROADMAP.md",
    "pyproject.toml",
    "pytest.ini",
    "app/__init__.py",
    "app/core/__init__.py",
    "app/core/config.py",
    "app/domain/data_contract.py",
    "app/domain/dataset_validation.py",
    "app/domain/feature_contract.py",
    "app/domain/signal_contract.py",
    "app/domain/score_contract.py",
    "app/domain/market_phase_contract.py",
    "app/domain/confidence_contract.py",
    "app/domain/__init__.py",
    "app/data/__init__.py",
    "app/engine/__init__.py",
    "app/engine/normalization.py",
    "app/engine/time_series.py",
    "app/services/__init__.py",
    "app/api/__init__.py",
    "tests/__init__.py",
    "tests/smoke/test_data_contract.py",
    "tests/smoke/test_dataset_validation.py",
    "tests/smoke/test_feature_contract.py",
    "tests/smoke/test_signal_contract.py",
    "tests/smoke/test_score_contract.py",
    "tests/smoke/test_market_phase_contract.py",
    "tests/smoke/test_confidence_contract.py",
    "tests/smoke/test_contract_boundaries.py",
    "tests/smoke/test_normalization.py",
    "tests/smoke/test_time_series.py",
    "tests/smoke/test_project_structure.py",
    "scripts/.gitkeep",
    "docs/.gitkeep",
    "artifacts/.gitkeep",
    "data/raw/.gitkeep",
    "data/processed/.gitkeep",
]

REQUIRED_DIRECTORIES = [
    "app",
    "app/core",
    "app/domain",
    "app/data",
    "app/engine",
    "app/services",
    "app/api",
    "tests",
    "tests/smoke",
    "scripts",
    "docs",
    "artifacts",
    "data",
    "data/raw",
    "data/processed",
]

NON_EMPTY_FILES = [
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "docs/PUBLIC_ROADMAP.md",
    "pyproject.toml",
    "app/core/config.py",
]

README_REQUIRED_TEXT = [
    "Engine-first Smart Money Intelligence Platform",
    "Execution Governance",
    "private local execution authority",
    "intentionally excluded from the public release",
]

PUBLIC_ROADMAP_REQUIRED_TEXT = [
    "Current Phase",
    "Implemented Public-Safe Components",
    "Limitations",
    "Future Roadmap",
    "No trading advice is provided",
    "No AI model is currently implemented",
    "No real data conclusions are produced",
]

SECURITY_REQUIRED_TEXT = [
    "Do not commit secrets",
    ".env files must never be committed",
    "Do not commit real market datasets",
    "API keys must be supplied only through local environment variables",
]


def test_foundation_project_structure_exists() -> None:
    for directory in REQUIRED_DIRECTORIES:
        path = PROJECT_ROOT / directory
        assert path.is_dir(), f"Missing required directory: {directory}"

    for file_path in REQUIRED_FILES:
        path = PROJECT_ROOT / file_path
        assert path.is_file(), f"Missing required file: {file_path}"

    for file_path in NON_EMPTY_FILES:
        path = PROJECT_ROOT / file_path
        assert path.read_text(encoding="utf-8").strip(), (
            f"Required file must not be empty: {file_path}"
        )


def test_public_release_governance_is_documented() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    roadmap = (PROJECT_ROOT / "docs" / "PUBLIC_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    security = (PROJECT_ROOT / "SECURITY.md").read_text(encoding="utf-8")
    license_text = (PROJECT_ROOT / "LICENSE").read_text(encoding="utf-8")

    for expected_text in README_REQUIRED_TEXT:
        assert expected_text in readme

    for expected_text in PUBLIC_ROADMAP_REQUIRED_TEXT:
        assert expected_text in roadmap

    for expected_text in SECURITY_REQUIRED_TEXT:
        assert expected_text in security

    assert "Apache License" in license_text
    assert "Version 2.0" in license_text
