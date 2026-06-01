from datetime import date
from pathlib import Path

import pytest

import app.data.local_csv_batch_run as batch_run_module
from app.data.local_csv_quality_validation import validate_local_csv_quality
from app.domain.data_quality_result import DataQualityCheck, DataQualityResult
from app.domain.data_source_contract import (
    DataGranularity,
    DataSourceContract,
    DataSourceReliability,
    DataSourceType,
)
from app.domain.local_csv_batch_run import (
    LocalCsvBatchRunResult,
    LocalCsvBatchRunStatus,
)
from app.domain.data_ingestion_plan import DataIngestionPlan
from app.domain.local_csv_contract import CsvPriceMode, LocalCsvIngestionContract
from app.domain.local_csv_quality_validation import LocalCsvQualityValidationResult


def _source() -> DataSourceContract:
    return DataSourceContract(
        name="Eligible Local CSV Source",
        source_type=DataSourceType.REAL,
        granularity=DataGranularity.DAILY,
        reliability=DataSourceReliability.VERIFIED_STRUCTURE_ONLY,
        supports_ohlcv=True,
        supports_adjusted_prices=True,
        supports_corporate_actions=True,
        timezone="UTC",
        notes="Metadata-only local CSV source for batch run orchestration tests.",
    )


def _plan(**overrides: object) -> DataIngestionPlan:
    values = {
        "source": _source(),
        "symbol": "AAPL",
        "start_date": date(2024, 1, 1),
        "end_date": date(2024, 1, 3),
        "use_adjusted_prices": True,
        "include_corporate_actions": True,
        "purpose": "Local CSV batch run orchestration smoke test.",
    }
    values.update(overrides)
    return DataIngestionPlan(**values)


def _csv_contract(file_path: str) -> LocalCsvIngestionContract:
    return LocalCsvIngestionContract(
        file_path=file_path,
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


def _write_csv(
    tmp_path: Path,
    rows: list[tuple[str, str, str, str, str, str, str]],
) -> str:
    file_path = tmp_path / "daily.csv"
    with file_path.open("w", encoding="utf-8", newline="") as csv_file:
        csv_file.write("symbol,date,open,high,low,close,volume\n")
        for row in rows:
            csv_file.write(",".join(row) + "\n")
    return str(file_path)


def _write_csv_without_volume(tmp_path: Path) -> str:
    file_path = tmp_path / "missing_volume.csv"
    with file_path.open("w", encoding="utf-8", newline="") as csv_file:
        csv_file.write("symbol,date,open,high,low,close\n")
        csv_file.write("AAPL,2024-01-01,100,102,99,101\n")
    return str(file_path)


def _valid_rows() -> list[tuple[str, str, str, str, str, str, str]]:
    return [
        ("AAPL", "2024-01-01", "100", "102", "99", "101", "1000"),
        ("AAPL", "2024-01-02", "101", "103", "100", "102", "1100"),
        ("AAPL", "2024-01-03", "102", "104", "101", "103", "1200"),
    ]


def _quality_result(
    check: DataQualityCheck,
    passed: bool = True,
) -> DataQualityResult:
    return DataQualityResult(
        check=check,
        passed=passed,
        metric_value=1.0,
        details="Local CSV batch run orchestration quality result.",
    )


def _quality_results_with_failed_gate() -> list[DataQualityResult]:
    return [
        _quality_result(DataQualityCheck.RECORD_COUNT_CHECK, passed=False),
        _quality_result(DataQualityCheck.DATE_RANGE_COVERAGE_CHECK),
        _quality_result(DataQualityCheck.SYMBOL_CONSISTENCY_CHECK),
        _quality_result(DataQualityCheck.OHLCV_VALIDITY_CHECK),
        _quality_result(DataQualityCheck.DAILY_CONTINUITY_CHECK),
        _quality_result(DataQualityCheck.MISSING_VALUE_CHECK),
    ]


def _run_valid_batch(tmp_path: Path) -> LocalCsvBatchRunResult:
    file_path = _write_csv(tmp_path, _valid_rows())
    return batch_run_module.run_local_csv_batch(
        _csv_contract(file_path),
        _plan(),
        "Validated local CSV batch.",
        "Quality path orchestration smoke test.",
    )


def test_valid_csv_with_all_quality_checks_passed_returns_batch_run_result(
    tmp_path: Path,
) -> None:
    result = _run_valid_batch(tmp_path)

    assert isinstance(result, LocalCsvBatchRunResult)


def test_valid_csv_with_all_quality_checks_passed_returns_ready_for_engine_planning(
    tmp_path: Path,
) -> None:
    result = _run_valid_batch(tmp_path)

    assert result.status == LocalCsvBatchRunStatus.READY_FOR_ENGINE_PLANNING
    assert result.validation_result.quality_gate_passed is True


def test_no_matching_records_returns_failed_ingestion(tmp_path: Path) -> None:
    file_path = _write_csv(
        tmp_path,
        [("MSFT", "2024-01-01", "100", "102", "99", "101", "1000")],
    )

    result = batch_run_module.run_local_csv_batch(
        _csv_contract(file_path),
        _plan(),
        "No matching rows.",
        "Expected failed ingestion.",
    )

    assert result.status == LocalCsvBatchRunStatus.FAILED_INGESTION
    assert result.validation_result.batch.records == []


def test_csv_that_ingests_but_fails_quality_gate_returns_blocked_by_quality_gate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    file_path = _write_csv(tmp_path, _valid_rows())
    csv_contract = _csv_contract(file_path)
    plan = _plan()
    successful_validation = validate_local_csv_quality(csv_contract, plan)
    failed_gate_validation = LocalCsvQualityValidationResult(
        batch=successful_validation.batch,
        quality_results=_quality_results_with_failed_gate(),
        quality_gate_passed=False,
    )

    def fake_validate_local_csv_quality(
        received_contract: LocalCsvIngestionContract,
        received_plan: DataIngestionPlan,
    ) -> LocalCsvQualityValidationResult:
        assert received_contract is csv_contract
        assert received_plan is plan
        return failed_gate_validation

    monkeypatch.setattr(
        batch_run_module,
        "validate_local_csv_quality",
        fake_validate_local_csv_quality,
    )

    result = batch_run_module.run_local_csv_batch(
        csv_contract,
        plan,
        "Blocked quality gate.",
        "Quality gate failure orchestration test.",
    )

    assert result.status == LocalCsvBatchRunStatus.BLOCKED_BY_QUALITY_GATE


def test_empty_run_label_raises_value_error(tmp_path: Path) -> None:
    file_path = _write_csv(tmp_path, _valid_rows())

    with pytest.raises(ValueError, match="run_label must not be empty"):
        batch_run_module.run_local_csv_batch(
            _csv_contract(file_path),
            _plan(),
            " ",
            "Notes are present.",
        )


def test_empty_notes_raises_value_error(tmp_path: Path) -> None:
    file_path = _write_csv(tmp_path, _valid_rows())

    with pytest.raises(ValueError, match="notes must not be empty"):
        batch_run_module.run_local_csv_batch(
            _csv_contract(file_path),
            _plan(),
            "Run label is present.",
            " ",
        )


def test_invalid_csv_numeric_value_propagates_value_error(tmp_path: Path) -> None:
    file_path = _write_csv(
        tmp_path,
        [("AAPL", "2024-01-01", "not-a-number", "102", "99", "101", "1000")],
    )

    with pytest.raises(ValueError, match="CSV row 2 failed to parse"):
        batch_run_module.run_local_csv_batch(
            _csv_contract(file_path),
            _plan(),
            "Invalid numeric value.",
            "Parsing error should propagate.",
        )


def test_missing_required_csv_column_propagates_value_error(tmp_path: Path) -> None:
    file_path = _write_csv_without_volume(tmp_path)

    with pytest.raises(ValueError, match="missing required CSV column: volume"):
        batch_run_module.run_local_csv_batch(
            _csv_contract(file_path),
            _plan(),
            "Missing required column.",
            "Header error should propagate.",
        )


def test_run_does_not_import_engine_modules() -> None:
    source = Path("app/data/local_csv_batch_run.py").read_text(encoding="utf-8")

    assert "app.engine" not in source
    assert "from app.engine" not in source
    assert "import app.engine" not in source


def test_run_does_not_import_forbidden_external_dependencies() -> None:
    source = Path("app/data/local_csv_batch_run.py").read_text(encoding="utf-8")

    for package_name in ["pandas", "numpy", "yfinance", "requests", "sqlalchemy"]:
        assert f"import {package_name}" not in source
        assert f"from {package_name}" not in source


def test_run_does_not_persist_files() -> None:
    source = Path("app/data/local_csv_batch_run.py").read_text(encoding="utf-8")

    assert "open(" not in source
    assert ".write(" not in source
    assert "Path(" not in source
    assert "pickle" not in source
    assert "shelve" not in source


def test_ready_for_engine_planning_does_not_produce_engine_output(
    tmp_path: Path,
) -> None:
    result = _run_valid_batch(tmp_path)

    for attribute_name in [
        "features",
        "signals",
        "scores",
        "market_phases",
        "confidence",
        "validation_results",
    ]:
        assert not hasattr(result, attribute_name)
        assert not hasattr(result.validation_result.batch, attribute_name)
