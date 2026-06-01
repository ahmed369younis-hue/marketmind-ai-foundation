"""Data ingestion planning contract definitions."""

from dataclasses import dataclass
from datetime import date

from app.data.source_evaluation import is_data_source_eligible_for_ingestion
from app.domain.data_source_contract import DataSourceContract


@dataclass(frozen=True, slots=True)
class DataIngestionPlan:
    """Strict planning record for future ingestion, without ingestion behavior."""

    source: DataSourceContract
    symbol: str
    start_date: date
    end_date: date
    use_adjusted_prices: bool
    include_corporate_actions: bool
    purpose: str

    def __post_init__(self) -> None:
        if not isinstance(self.source, DataSourceContract):
            raise ValueError("source must be a valid DataSourceContract instance")

        self._validate_non_empty_string("symbol")
        self._validate_date_not_future("start_date")
        self._validate_date_not_future("end_date")

        if self.end_date < self.start_date:
            raise ValueError("end_date must be greater than or equal to start_date")

        self._validate_bool("use_adjusted_prices")
        self._validate_bool("include_corporate_actions")

        if self.use_adjusted_prices and not self.source.supports_adjusted_prices:
            raise ValueError(
                "source must support adjusted prices when use_adjusted_prices is True"
            )

        if self.include_corporate_actions and not self.source.supports_corporate_actions:
            raise ValueError(
                "source must support corporate actions when include_corporate_actions is True"
            )

        self._validate_non_empty_string("purpose")

        if not is_data_source_eligible_for_ingestion(self.source):
            raise ValueError("source must be eligible for future ingestion planning")

    def _validate_non_empty_string(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not str:
            raise ValueError(f"{field_name} must be a string")

        if not value.strip():
            raise ValueError(f"{field_name} must not be empty")

    def _validate_date_not_future(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not date:
            raise ValueError(f"{field_name} must be a date")

        if value > date.today():
            raise ValueError(f"{field_name} must not be in the future")

    def _validate_bool(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not bool:
            raise ValueError(f"{field_name} must be bool")
