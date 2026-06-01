from datetime import date
from pathlib import Path

import pytest

from app.data.local_csv_quality_validation import validate_local_csv_quality
from app.data.quality_evaluation import evaluate_daily_dataset_quality
from app.domain.data_ingestion_plan import DataIngestionPlan
from app.domain.data_quality_result import DataQualityCheck, DataQualityResult
from app.domain.data_source_contract import (
    DataGranularity,
    DataSourceContract,
    DataSourceReliability,
    DataSourceType,
)
from app.domain.ingested_daily_dataset import IngestedDailyDataset
from app.domain.local_csv_contract import CsvPriceMode, LocalCsvIngestionContract
from app.domain.local_csv_quality_validation import LocalCsvQualityValidationResult


def _source(**overrides: object) -> DataSourceContract:
    values = {
        "name": "Eligible Local CSV Source",
        "source_type": DataSourceType.REAL,
        "granularity": DataGranularity.DAILY,
        "reliability": DataSourceReliability.VERIFIED_STRUCTURE_ONLY,
        "supports_ohlcv": True,
        "supports_adjusted_prices": True,
        "supports_corporate_actions": True,
        "timezone": "UTC",
        "notes": "Metadata-only local CSV source for quality validation tests.",
    }
    values.update(overrides)
    return DataSourceContract(**values)


def _plan(**overrides: object) -> DataIngestionPlan:
    values = {
        "source": _source(),
        "symbol": "AAPL",
        "start_date": date(2024, 1, 1),
        "end_date": date(2024, 1, 3),
        "use_adjusted_prices": True,
        "include_corporate_actions": True,
        "purpose": "Local CSV quality validation smoke test.",
    }
    values.update(overrides)
    return DataIngestionPlan(**values)


def _csv_contract(file_path: str, **overrides: object) -> LocalCsvIngestionContract:
    values = {
        "file_path": file_path,
        "delimiter": ",",
        "date_format": "%Y-%m-%d",
        "symbol_column": "symbol",
        "date_column": "date",
        "open_column": "open",
        "high_column": "high",
        "low_column": "low",
        "close_column": "close",
        "volume_column": "volume",
        "price_mode": CsvPriceMode.RAW,
        "timezone": "UTC",
    }
    values.update(overrides)
    return LocalCsvIngestionContract(**values)


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
        details="Local CSV quality validation result.",
    )


def _passing_quality_results() -> list[DataQualityResult]:
    return [
        _quality_result(DataQualityCheck.RECORD_COUNT_CHECK),
        _quality_result(DataQualityCheck.DATE_RANGE_COVERAGE_CHECK),
        _quality_result(DataQualityCheck.SYMBOL_CONSISTENCY_CHECK),
        _quality_result(DataQualityCheck.OHLCV_VALIDITY_CHECK),
        _quality_result(DataQualityCheck.DAILY_CONTINUITY_CHECK),
        _quality_result(DataQualityCheck.MISSING_VALUE_CHECK),
    ]


def _valid_validation_result(tmp_path: Path) -> LocalCsvQualityValidationResult:
    file_path = _write_csv(tmp_path, _valid_rows())
    return validate_local_csv_quality(_csv_contract(file_path), _plan())


def test_valid_csv_returns_local_csv_quality_validation_result(tmp_path: Path) -> None:
    result = _valid_validation_result(tmp_path)

    assert isinstance(result, LocalCsvQualityValidationResult)


def test_valid_csv_result_contains_ingested_daily_dataset(tmp_path: Path) -> None:
    result = _valid_validation_result(tmp_path)

    assert isinstance(result.batch, IngestedDailyDataset)


def test_valid_csv_result_contains_six_data_quality_results(tmp_path: Path) -> None:
    result = _valid_validation_result(tmp_path)

    assert len(result.quality_results) == 6
    assert all(isinstance(item, DataQualityResult) for item in result.quality_results)


def test_valid_csv_quality_gate_passed_is_true_when_all_checks_pass(tmp_path: Path) -> None:
    result = _valid_validation_result(tmp_path)

    assert result.quality_gate_passed is True


def test_no_matching_records_produces_failed_batch_and_failed_gate(tmp_path: Path) -> None:
    file_path = _write_csv(
        tmp_path,
        [("MSFT", "2024-01-01", "100", "102", "99", "101", "1000")],
    )
    result = validate_local_csv_quality(_csv_contract(file_path), _plan())

    assert result.batch.result.status.value == "FAILED"
    assert result.batch.records == []
    assert result.quality_gate_passed is False
    assert all(quality_result.passed is False for quality_result in result.quality_results)


def test_missing_daily_date_gap_propagates_value_error_from_ingestion(
    tmp_path: Path,
) -> None:
    file_path = _write_csv(
        tmp_path,
        [
            ("AAPL", "2024-01-01", "100", "102", "99", "101", "1000"),
            ("AAPL", "2024-01-02", "101", "103", "100", "102", "1100"),
            ("AAPL", "2024-01-04", "103", "105", "102", "104", "1300"),
        ],
    )
    plan = _plan(end_date=date(2024, 1, 4))

    with pytest.raises(ValueError):
        validate_local_csv_quality(_csv_contract(file_path), plan)


def test_invalid_csv_numeric_value_propagates_value_error(tmp_path: Path) -> None:
    file_path = _write_csv(
        tmp_path,
        [("AAPL", "2024-01-01", "not-a-number", "102", "99", "101", "1000")],
    )

    with pytest.raises(ValueError, match="CSV row 2 failed to parse"):
        validate_local_csv_quality(_csv_contract(file_path), _plan())


def test_result_rejects_non_ingested_daily_dataset_batch(tmp_path: Path) -> None:
    quality_results = _valid_validation_result(tmp_path).quality_results

    with pytest.raises(ValueError):
        LocalCsvQualityValidationResult(
            batch="not a batch",
            quality_results=quality_results,
            quality_gate_passed=True,
        )


def test_result_rejects_non_list_quality_results(tmp_path: Path) -> None:
    batch = _valid_validation_result(tmp_path).batch

    with pytest.raises(ValueError):
        LocalCsvQualityValidationResult(
            batch=batch,
            quality_results=tuple(_passing_quality_results()),
            quality_gate_passed=True,
        )


def test_result_rejects_empty_quality_results(tmp_path: Path) -> None:
    batch = _valid_validation_result(tmp_path).batch

    with pytest.raises(ValueError):
        LocalCsvQualityValidationResult(
            batch=batch,
            quality_results=[],
            quality_gate_passed=False,
        )


def test_result_rejects_non_data_quality_result_item(tmp_path: Path) -> None:
    batch = _valid_validation_result(tmp_path).batch

    with pytest.raises(ValueError):
        LocalCsvQualityValidationResult(
            batch=batch,
            quality_results=_passing_quality_results() + ["not a result"],
            quality_gate_passed=True,
        )


def test_result_rejects_non_bool_quality_gate_passed(tmp_path: Path) -> None:
    validation_result = _valid_validation_result(tmp_path)

    with pytest.raises(ValueError):
        LocalCsvQualityValidationResult(
            batch=validation_result.batch,
            quality_results=validation_result.quality_results,
            quality_gate_passed="yes",
        )


def test_result_rejects_mismatched_quality_gate_passed(tmp_path: Path) -> None:
    validation_result = _valid_validation_result(tmp_path)

    with pytest.raises(ValueError):
        LocalCsvQualityValidationResult(
            batch=validation_result.batch,
            quality_results=validation_result.quality_results,
            quality_gate_passed=False,
        )


def test_failed_ingestion_batch_cannot_pass_quality_gate(tmp_path: Path) -> None:
    file_path = _write_csv(
        tmp_path,
        [("MSFT", "2024-01-01", "100", "102", "99", "101", "1000")],
    )
    failed_result = validate_local_csv_quality(_csv_contract(file_path), _plan())

    with pytest.raises(ValueError):
        LocalCsvQualityValidationResult(
            batch=failed_result.batch,
            quality_results=_passing_quality_results(),
            quality_gate_passed=True,
        )


def test_orchestration_does_not_import_engine_modules() -> None:
    for path in [
        Path("app/data/local_csv_quality_validation.py"),
        Path("app/domain/local_csv_quality_validation.py"),
    ]:
        source = path.read_text(encoding="utf-8")

        assert "app.engine" not in source
        assert "from app.engine" not in source
        assert "import app.engine" not in source


def test_orchestration_does_not_import_forbidden_external_dependencies() -> None:
    for path in [
        Path("app/data/local_csv_quality_validation.py"),
        Path("app/domain/local_csv_quality_validation.py"),
    ]:
        source = path.read_text(encoding="utf-8")

        for package_name in ["pandas", "numpy", "yfinance", "requests", "sqlalchemy"]:
            assert f"import {package_name}" not in source
            assert f"from {package_name}" not in source


def test_orchestration_does_not_persist_files() -> None:
    source = Path("app/data/local_csv_quality_validation.py").read_text(encoding="utf-8")

    assert "open(" not in source
    assert ".write(" not in source
    assert "Path(" not in source
    assert "pickle" not in source
    assert "shelve" not in source
