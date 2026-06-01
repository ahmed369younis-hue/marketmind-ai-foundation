"""Local CSV ingestion metadata contract definitions."""

from dataclasses import dataclass
from enum import Enum


class CsvPriceMode(Enum):
    """Allowed local CSV price modes for future ingestion planning."""

    RAW = "RAW"
    ADJUSTED = "ADJUSTED"


@dataclass(frozen=True, slots=True)
class LocalCsvIngestionContract:
    """Strict metadata contract for future local CSV ingestion."""

    file_path: str
    delimiter: str
    date_format: str
    symbol_column: str
    date_column: str
    open_column: str
    high_column: str
    low_column: str
    close_column: str
    volume_column: str
    price_mode: CsvPriceMode
    timezone: str

    def __post_init__(self) -> None:
        self._validate_non_empty_string("file_path")
        if not self.file_path.endswith(".csv"):
            raise ValueError("file_path must end with .csv")

        self._validate_non_empty_string("delimiter")
        if len(self.delimiter) != 1:
            raise ValueError("delimiter must be exactly one character")

        self._validate_non_empty_string("date_format")
        self._validate_column_names()

        if not isinstance(self.price_mode, CsvPriceMode):
            raise ValueError("price_mode must be a valid CsvPriceMode value")

        self._validate_non_empty_string("timezone")

    def _validate_non_empty_string(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not str:
            raise ValueError(f"{field_name} must be a string")

        if not value.strip():
            raise ValueError(f"{field_name} must not be empty")

    def _validate_column_names(self) -> None:
        column_fields = (
            "symbol_column",
            "date_column",
            "open_column",
            "high_column",
            "low_column",
            "close_column",
            "volume_column",
        )

        for field_name in column_fields:
            self._validate_non_empty_string(field_name)

        column_names = [getattr(self, field_name).strip() for field_name in column_fields]
        if len(column_names) != len(set(column_names)):
            raise ValueError("all column names must be unique")
