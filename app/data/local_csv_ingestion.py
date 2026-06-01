"""Local CSV ingestion utilities."""

import csv
from datetime import datetime

from app.domain.data_contract import DailyMarketData
from app.domain.data_ingestion_plan import DataIngestionPlan
from app.domain.data_ingestion_result import DataIngestionResult, DataIngestionStatus
from app.domain.data_source_contract import DataSourceReliability
from app.domain.ingested_daily_dataset import IngestedDailyDataset
from app.domain.local_csv_contract import CsvPriceMode, LocalCsvIngestionContract


def ingest_local_csv(
    csv_contract: LocalCsvIngestionContract,
    plan: DataIngestionPlan,
) -> IngestedDailyDataset:
    """Read a local CSV file into an ingested daily dataset batch."""

    if not isinstance(csv_contract, LocalCsvIngestionContract):
        raise ValueError("csv_contract must be a LocalCsvIngestionContract instance")

    if not isinstance(plan, DataIngestionPlan):
        raise ValueError("plan must be a DataIngestionPlan instance")

    if csv_contract.timezone != plan.source.timezone:
        raise ValueError("csv timezone must match plan source timezone")

    if csv_contract.price_mode == CsvPriceMode.ADJUSTED and not plan.use_adjusted_prices:
        raise ValueError("adjusted CSV requires plan.use_adjusted_prices")

    records = _read_matching_records(csv_contract, plan)

    if not records:
        result = DataIngestionResult(
            plan=plan,
            status=DataIngestionStatus.FAILED,
            records_count=0,
            first_date=None,
            last_date=None,
            reliability_after_ingestion=DataSourceReliability.UNVERIFIED,
            message="Local CSV ingestion produced no matching records",
        )
        return IngestedDailyDataset(plan=plan, result=result, records=[])

    result = DataIngestionResult(
        plan=plan,
        status=DataIngestionStatus.SUCCESS,
        records_count=len(records),
        first_date=records[0].date,
        last_date=records[-1].date,
        reliability_after_ingestion=DataSourceReliability.VERIFIED_STRUCTURE_ONLY,
        message="Local CSV ingestion completed",
    )
    return IngestedDailyDataset(plan=plan, result=result, records=records)


def _read_matching_records(
    csv_contract: LocalCsvIngestionContract,
    plan: DataIngestionPlan,
) -> list[DailyMarketData]:
    required_columns = _required_columns(csv_contract)

    try:
        with open(csv_contract.file_path, newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file, delimiter=csv_contract.delimiter)
            _validate_required_columns(reader.fieldnames, required_columns)

            records: list[DailyMarketData] = []
            for row_number, row in enumerate(reader, start=2):
                record = _parse_row(row, row_number, csv_contract)
                if record.symbol == plan.symbol and plan.start_date <= record.date <= plan.end_date:
                    records.append(record)

            return records
    except FileNotFoundError as error:
        raise ValueError("CSV file not found") from error


def _required_columns(csv_contract: LocalCsvIngestionContract) -> tuple[str, ...]:
    return (
        csv_contract.symbol_column,
        csv_contract.date_column,
        csv_contract.open_column,
        csv_contract.high_column,
        csv_contract.low_column,
        csv_contract.close_column,
        csv_contract.volume_column,
    )


def _validate_required_columns(
    header_columns: list[str] | None,
    required_columns: tuple[str, ...],
) -> None:
    available_columns = set(header_columns or [])
    for column in required_columns:
        if column not in available_columns:
            raise ValueError(f"missing required CSV column: {column}")


def _parse_row(
    row: dict[str, str],
    row_number: int,
    csv_contract: LocalCsvIngestionContract,
) -> DailyMarketData:
    try:
        record_date = datetime.strptime(
            row[csv_contract.date_column],
            csv_contract.date_format,
        ).date()
        return DailyMarketData(
            date=record_date,
            open=float(row[csv_contract.open_column]),
            high=float(row[csv_contract.high_column]),
            low=float(row[csv_contract.low_column]),
            close=float(row[csv_contract.close_column]),
            volume=float(row[csv_contract.volume_column]),
            symbol=row[csv_contract.symbol_column],
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"CSV row {row_number} failed to parse: {error}") from error
