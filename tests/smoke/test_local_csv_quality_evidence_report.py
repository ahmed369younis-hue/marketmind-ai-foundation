from datetime import date
from pathlib import Path
import socket
import urllib.request

import pytest

from app.data.local_csv_batch_run import run_local_csv_batch
from app.data.local_csv_quality_validation import validate_local_csv_quality
from app.domain.data_quality_result import DataQualityCheck
from app.domain.data_source_contract import (
    DataGranularity,
    DataSourceContract,
    DataSourceReliability,
    DataSourceType,
)
from app.domain.local_csv_batch_run import LocalCsvBatchRunStatus
from app.domain.local_csv_contract import CsvPriceMode, LocalCsvIngestionContract
from app.domain.local_csv_quality_evidence_report import (
    build_local_csv_quality_evidence_report,
    LocalCsvQualityCheckEvidence,
    LocalCsvQualityEvidenceReport,
)


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
            "Synthetic fixture metadata for public-safe local CSV evidence testing only."
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
        purpose="Public-safe synthetic local CSV quality evidence report test.",
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


def _build_report_from_synthetic_path(
    monkeypatch: pytest.MonkeyPatch,
) -> LocalCsvQualityEvidenceReport:
    _block_external_network(monkeypatch)
    validation_result = validate_local_csv_quality(_csv_contract(), _plan())

    return build_local_csv_quality_evidence_report(validation_result)


def test_report_from_synthetic_validation_path_contains_safe_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = _build_report_from_synthetic_path(monkeypatch)

    assert isinstance(report, LocalCsvQualityEvidenceReport)
    assert report.source_label == "Public-safe synthetic local CSV fixture source"
    assert report.symbol == SYNTHETIC_FIXTURE_SYMBOL
    assert report.requested_start_date == SYNTHETIC_FIXTURE_START
    assert report.requested_end_date == SYNTHETIC_FIXTURE_END
    assert report.records_count == 3
    assert report.first_date == SYNTHETIC_FIXTURE_START
    assert report.last_date == SYNTHETIC_FIXTURE_END


def test_report_summarizes_existing_quality_checks_and_gate_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    validation_result = validate_local_csv_quality(_csv_contract(), _plan())
    report = build_local_csv_quality_evidence_report(validation_result)

    assert report.quality_gate_passed is validation_result.quality_gate_passed
    assert report.quality_gate_passed is True
    assert report.quality_checks == tuple(
        LocalCsvQualityCheckEvidence(
            check_name=result.check.value,
            passed=result.passed,
        )
        for result in validation_result.quality_results
    )
    assert {item.check_name for item in report.quality_checks} == {
        check.value for check in DataQualityCheck
    }


def test_report_from_batch_run_uses_existing_validation_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _block_external_network(monkeypatch)
    run_result = run_local_csv_batch(
        _csv_contract(),
        _plan(),
        "Public-safe local CSV quality evidence report.",
        "Evidence report summarizes validation output only.",
    )
    report = build_local_csv_quality_evidence_report(run_result)

    assert run_result.status == LocalCsvBatchRunStatus.READY_FOR_ENGINE_PLANNING
    assert report.records_count == run_result.validation_result.batch.result.records_count
    assert report.quality_gate_passed is run_result.validation_result.quality_gate_passed


def test_report_encodes_limitations_and_non_approval_flags(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = _build_report_from_synthetic_path(monkeypatch)
    limitations_text = " ".join(report.limitations).lower()

    assert "summary of existing local csv quality validation outputs only" in limitations_text
    assert "not real-data verification" in limitations_text
    assert "source reliability approval" in limitations_text
    assert "historical verification" in limitations_text
    assert "production approval" in limitations_text
    assert "engine execution" in limitations_text
    assert "market analysis" in limitations_text
    assert "trading output" in limitations_text
    assert "financial conclusions" in limitations_text
    assert report.is_real_data_verification is False
    assert report.approves_source_reliability is False
    assert report.verifies_historical_data is False
    assert report.approves_production_use is False
    assert report.permits_engine_execution is False
    assert report.permits_market_analysis is False
    assert report.permits_trading_output is False
    assert report.permits_financial_conclusions is False


def test_report_does_not_include_engine_market_or_order_outputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = _build_report_from_synthetic_path(monkeypatch)

    for attribute_name in [
        "features",
        "signals",
        "scores",
        "market_phases",
        "confidence",
        "analysis",
        "recommendations",
        "buy_signal",
        "sell_signal",
        "orders",
        "positions",
        "source_reliability_approved",
        "historical_verification_approved",
        "production_approved",
    ]:
        assert not hasattr(report, attribute_name)


def test_report_builder_creates_no_persistence_files(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _block_external_network(monkeypatch)
    public_outputs_before = _public_output_files()

    build_local_csv_quality_evidence_report(
        validate_local_csv_quality(_csv_contract(), _plan())
    )

    assert _public_output_files() == public_outputs_before


def test_report_builder_rejects_unknown_input_type() -> None:
    with pytest.raises(ValueError, match="result must be"):
        build_local_csv_quality_evidence_report("not a validation result")


def test_report_modules_do_not_import_engine_or_forbidden_dependencies() -> None:
    for path in [
        Path("app/domain/local_csv_quality_evidence_report.py"),
    ]:
        source = path.read_text(encoding="utf-8")

        assert "app.engine" not in source
        assert "from app.engine" not in source
        assert "import app.engine" not in source
        for package_name in ["pandas", "numpy", "yfinance", "requests", "sqlalchemy"]:
            assert f"import {package_name}" not in source
            assert f"from {package_name}" not in source
        assert "open(" not in source
        assert ".write(" not in source
        assert "Path(" not in source
        assert "pickle" not in source
        assert "shelve" not in source
