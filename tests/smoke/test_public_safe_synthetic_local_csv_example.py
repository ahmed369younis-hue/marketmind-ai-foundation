from datetime import date
from pathlib import Path
import socket
import urllib.request

import pytest

from app.data.local_csv_batch_run import run_local_csv_batch
from app.data.local_csv_ingestion import ingest_local_csv
from app.data.local_csv_quality_validation import validate_local_csv_quality
from app.domain.data_ingestion_result import DataIngestionStatus
from app.domain.data_source_contract import (
    DataGranularity,
    DataSourceContract,
    DataSourceReliability,
    DataSourceType,
)
from app.domain.local_csv_batch_run import LocalCsvBatchRunStatus
from app.domain.local_csv_contract import CsvPriceMode, LocalCsvIngestionContract


FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "local_csv"
    / "synthetic_spy_daily_valid.csv"
)
SYNTHETIC_FIXTURE_SYMBOL = "SPY"
SYNTHETIC_FIXTURE_START = date(2001, 1, 1)
SYNTHETIC_FIXTURE_END = date(2001, 1, 3)


def _source() -> DataSourceContract:
    return DataSourceContract(
        name="Public-safe synthetic local CSV fixture source",
        source_type=DataSourceType.REAL,
        granularity=DataGranularity.DAILY,
        reliability=DataSourceReliability.VERIFIED_STRUCTURE_ONLY,
        supports_ohlcv=True,
        supports_adjusted_prices=True,
        supports_corporate_actions=True,
        timezone="UTC",
        notes=(
            "Synthetic fixture metadata for public-safe local CSV validation testing only."
        ),
    )


def _plan() -> object:
    from app.domain.data_ingestion_plan import DataIngestionPlan

    return DataIngestionPlan(
        source=_source(),
        symbol=SYNTHETIC_FIXTURE_SYMBOL,
        start_date=SYNTHETIC_FIXTURE_START,
        end_date=SYNTHETIC_FIXTURE_END,
        use_adjusted_prices=True,
        include_corporate_actions=True,
        purpose="Public-safe synthetic local CSV validation example.",
    )


def _csv_contract() -> LocalCsvIngestionContract:
    return LocalCsvIngestionContract(
        file_path=str(FIXTURE_PATH),
        delimiter=",",
        date_format="%Y-%m-%d",
        symbol_column="symbol",
        date_column="date",
        open_column="open",
        high_column="high",
        low_column="low",
        close_column="close",
        volume_column="volume",
        price_mode=CsvPriceMode.RAW,
        timezone="UTC",
    )


def _public_output_files() -> set[str]:
    output_files: set[str] = set()
    for directory in [
        Path("logs"),
        Path("artifacts"),
        Path("data/raw"),
        Path("data/processed"),
    ]:
        if not directory.exists():
            continue

        for path in directory.rglob("*"):
            if path.is_file() and path.name != ".gitkeep":
                output_files.add(path.as_posix())

    return output_files


def _block_external_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("external network/API usage is forbidden")

    monkeypatch.setattr(socket, "create_connection", fail_network)
    monkeypatch.setattr(urllib.request, "urlopen", fail_network)


def test_synthetic_fixture_is_public_safe_schema_fixture_only() -> None:
    assert FIXTURE_PATH.is_file()
    assert "synthetic" in FIXTURE_PATH.name
    assert FIXTURE_PATH.parts[-3:] == (
        "fixtures",
        "local_csv",
        "synthetic_spy_daily_valid.csv",
    )
    assert "data/raw" not in FIXTURE_PATH.as_posix()
    assert "data/processed" not in FIXTURE_PATH.as_posix()


def test_synthetic_fixture_runs_existing_local_csv_quality_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _block_external_network(monkeypatch)
    public_outputs_before = _public_output_files()

    csv_contract = _csv_contract()
    plan = _plan()
    batch = ingest_local_csv(csv_contract, plan)
    validation_result = validate_local_csv_quality(csv_contract, plan)
    run_result = run_local_csv_batch(
        csv_contract,
        plan,
        "Public-safe synthetic local CSV validation example.",
        "Synthetic fixture exercises existing local CSV validation path only.",
    )

    assert batch.result.status == DataIngestionStatus.SUCCESS
    assert batch.result.records_count == 3
    assert validation_result.quality_gate_passed is True
    assert run_result.status == LocalCsvBatchRunStatus.READY_FOR_ENGINE_PLANNING

    assert batch.plan.source.reliability == DataSourceReliability.VERIFIED_STRUCTURE_ONLY
    assert batch.result.reliability_after_ingestion == (
        DataSourceReliability.VERIFIED_STRUCTURE_ONLY
    )
    assert batch.result.reliability_after_ingestion != DataSourceReliability.VERIFIED_HISTORICAL

    for attribute_name in [
        "features",
        "signals",
        "scores",
        "market_phases",
        "confidence",
        "analysis",
        "recommendations",
        "orders",
        "positions",
        "source_reliability_approved",
        "production_approved",
    ]:
        assert not hasattr(run_result, attribute_name)
        assert not hasattr(run_result.validation_result.batch, attribute_name)

    assert _public_output_files() == public_outputs_before


def test_synthetic_example_modules_do_not_add_forbidden_dependencies_or_engine_imports() -> None:
    for path in [
        Path("app/data/local_csv_ingestion.py"),
        Path("app/data/local_csv_quality_validation.py"),
        Path("app/data/local_csv_batch_run.py"),
    ]:
        source = path.read_text(encoding="utf-8")

        assert "app.engine" not in source
        assert "from app.engine" not in source
        assert "import app.engine" not in source
        for package_name in ["pandas", "numpy", "yfinance", "requests", "sqlalchemy"]:
            assert f"import {package_name}" not in source
            assert f"from {package_name}" not in source
