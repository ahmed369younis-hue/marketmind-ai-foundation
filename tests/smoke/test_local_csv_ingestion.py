from datetime import date
from pathlib import Path

import pytest

from app.data.local_csv_ingestion import ingest_local_csv
from app.domain.data_contract import DailyMarketData
from app.domain.data_ingestion_plan import DataIngestionPlan
from app.domain.data_ingestion_result import DataIngestionStatus
from app.domain.data_source_contract import (
    DataGranularity,
    DataSourceContract,
    DataSourceReliability,
    DataSourceType,
)
from app.domain.ingested_daily_dataset import IngestedDailyDataset
from app.domain.local_csv_contract import CsvPriceMode, LocalCsvIngestionContract


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
        "notes": "Metadata-only local CSV source for ingestion tests.",
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
        "purpose": "Local CSV ingestion smoke test.",
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
    header: tuple[str, ...] = ("symbol", "date", "open", "high", "low", "close", "volume"),
) -> str:
    file_path = tmp_path / "daily.csv"
    with file_path.open("w", encoding="utf-8", newline="") as csv_file:
        csv_file.write(",".join(header) + "\n")
        for row in rows:
            csv_file.write(",".join(row) + "\n")
    return str(file_path)


def _valid_rows() -> list[tuple[str, str, str, str, str, str, str]]:
    return [
        ("AAPL", "2024-01-01", "100", "102", "99", "101", "1000"),
        ("AAPL", "2024-01-02", "101", "103", "100", "102", "1100"),
        ("AAPL", "2024-01-03", "102", "104", "101", "103", "1200"),
    ]


def test_valid_csv_with_matching_records_returns_success_batch(tmp_path: Path) -> None:
    file_path = _write_csv(tmp_path, _valid_rows())
    batch = ingest_local_csv(_csv_contract(file_path), _plan())

    assert isinstance(batch, IngestedDailyDataset)
    assert batch.result.status == DataIngestionStatus.SUCCESS
    assert batch.result.records_count == 3
    assert batch.result.reliability_after_ingestion == DataSourceReliability.VERIFIED_STRUCTURE_ONLY
    assert batch.result.message == "Local CSV ingestion completed"


def test_returned_records_are_daily_market_data_objects(tmp_path: Path) -> None:
    file_path = _write_csv(tmp_path, _valid_rows())
    batch = ingest_local_csv(_csv_contract(file_path), _plan())

    assert all(isinstance(record, DailyMarketData) for record in batch.records)


def test_records_are_filtered_by_plan_symbol(tmp_path: Path) -> None:
    rows = [
        ("AAPL", "2024-01-01", "100", "102", "99", "101", "1000"),
        ("MSFT", "2024-01-02", "201", "203", "200", "202", "2100"),
        ("AAPL", "2024-01-02", "101", "103", "100", "102", "1100"),
        ("AAPL", "2024-01-03", "102", "104", "101", "103", "1200"),
    ]
    file_path = _write_csv(tmp_path, rows)
    batch = ingest_local_csv(_csv_contract(file_path), _plan())

    assert [record.symbol for record in batch.records] == ["AAPL", "AAPL", "AAPL"]


def test_records_are_filtered_by_plan_date_range(tmp_path: Path) -> None:
    rows = [
        ("AAPL", "2023-12-31", "99", "101", "98", "100", "900"),
        ("AAPL", "2024-01-01", "100", "102", "99", "101", "1000"),
        ("AAPL", "2024-01-02", "101", "103", "100", "102", "1100"),
        ("AAPL", "2024-01-03", "102", "104", "101", "103", "1200"),
    ]
    file_path = _write_csv(tmp_path, rows)
    plan = _plan(end_date=date(2024, 1, 2))
    batch = ingest_local_csv(_csv_contract(file_path), plan)

    assert [record.date for record in batch.records] == [date(2024, 1, 1), date(2024, 1, 2)]


def test_no_matching_records_returns_failed_result_and_empty_records(tmp_path: Path) -> None:
    rows = [("MSFT", "2024-01-01", "100", "102", "99", "101", "1000")]
    file_path = _write_csv(tmp_path, rows)
    batch = ingest_local_csv(_csv_contract(file_path), _plan())

    assert batch.result.status == DataIngestionStatus.FAILED
    assert batch.result.records_count == 0
    assert batch.records == []
    assert batch.result.message == "Local CSV ingestion produced no matching records"


def test_missing_required_column_raises_value_error(tmp_path: Path) -> None:
    file_path = _write_csv(
        tmp_path,
        [("AAPL", "2024-01-01", "100", "102", "99", "101")],
        header=("symbol", "date", "open", "high", "low", "close"),
    )

    with pytest.raises(ValueError, match="missing required CSV column: volume"):
        ingest_local_csv(_csv_contract(file_path), _plan())


def test_invalid_date_raises_value_error_with_row_context(tmp_path: Path) -> None:
    rows = [("AAPL", "not-a-date", "100", "102", "99", "101", "1000")]
    file_path = _write_csv(tmp_path, rows)

    with pytest.raises(ValueError, match="CSV row 2 failed to parse"):
        ingest_local_csv(_csv_contract(file_path), _plan())


def test_invalid_numeric_value_raises_value_error_with_row_context(tmp_path: Path) -> None:
    rows = [("AAPL", "2024-01-01", "not-a-number", "102", "99", "101", "1000")]
    file_path = _write_csv(tmp_path, rows)

    with pytest.raises(ValueError, match="CSV row 2 failed to parse"):
        ingest_local_csv(_csv_contract(file_path), _plan())


def test_csv_contract_not_local_csv_contract_raises_value_error() -> None:
    with pytest.raises(ValueError, match="csv_contract must be a LocalCsvIngestionContract instance"):
        ingest_local_csv("not a csv contract", _plan())


def test_plan_not_data_ingestion_plan_raises_value_error(tmp_path: Path) -> None:
    file_path = _write_csv(tmp_path, _valid_rows())

    with pytest.raises(ValueError, match="plan must be a DataIngestionPlan instance"):
        ingest_local_csv(_csv_contract(file_path), "not a plan")


def test_timezone_mismatch_raises_value_error(tmp_path: Path) -> None:
    file_path = _write_csv(tmp_path, _valid_rows())

    with pytest.raises(ValueError, match="csv timezone must match plan source timezone"):
        ingest_local_csv(_csv_contract(file_path, timezone="America/New_York"), _plan())


def test_adjusted_csv_requires_plan_use_adjusted_prices(tmp_path: Path) -> None:
    file_path = _write_csv(tmp_path, _valid_rows())
    csv_contract = _csv_contract(file_path, price_mode=CsvPriceMode.ADJUSTED)
    plan = _plan(use_adjusted_prices=False)

    with pytest.raises(ValueError, match="adjusted CSV requires plan.use_adjusted_prices"):
        ingest_local_csv(csv_contract, plan)


def test_file_not_found_raises_value_error(tmp_path: Path) -> None:
    file_path = str(tmp_path / "missing.csv")

    with pytest.raises(ValueError, match="CSV file not found"):
        ingest_local_csv(_csv_contract(file_path), _plan())


def test_input_file_order_is_preserved(tmp_path: Path) -> None:
    rows = [
        ("AAPL", "2024-01-02", "101", "103", "100", "102", "1100"),
        ("AAPL", "2024-01-03", "102", "104", "101", "103", "1200"),
    ]
    file_path = _write_csv(tmp_path, rows)
    plan = _plan(start_date=date(2024, 1, 2), end_date=date(2024, 1, 3))
    batch = ingest_local_csv(_csv_contract(file_path), plan)

    assert [record.date for record in batch.records] == [date(2024, 1, 2), date(2024, 1, 3)]


def test_unsorted_csv_order_is_rejected_by_batch_validation(tmp_path: Path) -> None:
    rows = [
        ("AAPL", "2024-01-01", "100", "102", "99", "101", "1000"),
        ("AAPL", "2024-01-03", "102", "104", "101", "103", "1200"),
        ("AAPL", "2024-01-02", "101", "103", "100", "102", "1100"),
    ]
    file_path = _write_csv(tmp_path, rows)

    with pytest.raises(ValueError):
        ingest_local_csv(_csv_contract(file_path), _plan())


def test_missing_daily_date_gap_is_rejected_by_batch_validation(tmp_path: Path) -> None:
    rows = [
        ("AAPL", "2024-01-01", "100", "102", "99", "101", "1000"),
        ("AAPL", "2024-01-02", "101", "103", "100", "102", "1100"),
        ("AAPL", "2024-01-04", "103", "105", "102", "104", "1300"),
    ]
    file_path = _write_csv(tmp_path, rows)
    plan = _plan(end_date=date(2024, 1, 4))

    with pytest.raises(ValueError):
        ingest_local_csv(_csv_contract(file_path), plan)


def test_ingestion_does_not_run_daily_dataset_quality_evaluation() -> None:
    source = Path("app/data/local_csv_ingestion.py").read_text(encoding="utf-8")

    assert "evaluate_daily_dataset_quality" not in source


def test_ingestion_does_not_run_data_quality_gate() -> None:
    source = Path("app/data/local_csv_ingestion.py").read_text(encoding="utf-8")

    assert "can_pass_data_quality_gate" not in source


def test_no_forbidden_external_dependency_imports_are_introduced() -> None:
    source = Path("app/data/local_csv_ingestion.py").read_text(encoding="utf-8")

    for package_name in ["pandas", "numpy", "yfinance", "requests", "sqlalchemy"]:
        assert f"import {package_name}" not in source
        assert f"from {package_name}" not in source


def test_no_engine_imports_are_introduced() -> None:
    source = Path("app/data/local_csv_ingestion.py").read_text(encoding="utf-8")

    assert "app.engine" not in source
    assert "from app.engine" not in source
    assert "import app.engine" not in source
