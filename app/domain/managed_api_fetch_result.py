"""Managed API EOD fetch result contract definitions."""

from dataclasses import dataclass
from datetime import date
from enum import Enum

from app.domain.managed_api_eod_record import ManagedApiEodRecord
from app.domain.managed_api_provider_contract import ManagedApiProviderContract


class ManagedApiFetchStatus(Enum):
    """Allowed future managed API fetch statuses."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class ManagedApiEodFetchResult:
    """Strict future managed API EOD fetch result contract."""

    provider: ManagedApiProviderContract
    status: ManagedApiFetchStatus
    symbol: str
    start_date: date
    end_date: date
    records: list[ManagedApiEodRecord]
    records_count: int
    first_record_date: date | None
    last_record_date: date | None
    message: str

    def __post_init__(self) -> None:
        self._validate_provider()
        self._validate_status()
        self._validate_symbol()
        self._validate_date("start_date")
        self._validate_date("end_date")
        self._validate_date_range()
        self._validate_records()
        self._validate_records_count()
        self._validate_non_empty_string("message")

        if self.status is ManagedApiFetchStatus.SUCCESS:
            self._validate_success()
        elif self.status is ManagedApiFetchStatus.FAILED:
            self._validate_failed()

    def _validate_provider(self) -> None:
        if not isinstance(self.provider, ManagedApiProviderContract):
            raise ValueError("provider must be a ManagedApiProviderContract instance")

    def _validate_status(self) -> None:
        if not isinstance(self.status, ManagedApiFetchStatus):
            raise ValueError("status must be a valid ManagedApiFetchStatus value")

    def _validate_non_empty_string(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not str:
            raise ValueError(f"{field_name} must be a string")

        if not value.strip():
            raise ValueError(f"{field_name} must not be empty")

    def _validate_symbol(self) -> None:
        self._validate_non_empty_string("symbol")

        if self.symbol != self.provider.allowed_first_symbol:
            raise ValueError("symbol must equal provider.allowed_first_symbol")

    def _validate_date(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not date:
            raise ValueError(f"{field_name} must be a datetime.date instance")

        if value > date.today():
            raise ValueError(f"{field_name} must not be in the future")

    def _validate_date_range(self) -> None:
        if self.end_date < self.start_date:
            raise ValueError("end_date must be greater than or equal to start_date")

    def _validate_records(self) -> None:
        if type(self.records) is not list:
            raise ValueError("records must be a list")

        for record in self.records:
            if not isinstance(record, ManagedApiEodRecord):
                raise ValueError("all records must be ManagedApiEodRecord instances")

    def _validate_records_count(self) -> None:
        if type(self.records_count) is not int:
            raise ValueError("records_count must be an int")

        if self.records_count < 0:
            raise ValueError("records_count must be >= 0")

        if self.records_count != len(self.records):
            raise ValueError("records_count must equal len(records)")

    def _validate_optional_record_date(self, field_name: str) -> date:
        value = getattr(self, field_name)
        if value is None:
            raise ValueError(f"{field_name} must not be None")

        if type(value) is not date:
            raise ValueError(f"{field_name} must be a datetime.date instance")

        return value

    def _validate_success(self) -> None:
        if not self.records:
            raise ValueError("records must not be empty when status is SUCCESS")

        if self.records_count <= 0:
            raise ValueError("records_count must be > 0 when status is SUCCESS")

        first_record_date = self._validate_optional_record_date("first_record_date")
        last_record_date = self._validate_optional_record_date("last_record_date")

        if first_record_date < self.start_date:
            raise ValueError("first_record_date must be >= start_date")

        if last_record_date > self.end_date:
            raise ValueError("last_record_date must be <= end_date")

        if last_record_date < first_record_date:
            raise ValueError("last_record_date must be >= first_record_date")

        self._validate_success_records()

    def _validate_success_records(self) -> None:
        previous_record_date: date | None = None
        seen_dates: set[date] = set()

        for record in self.records:
            if record.date in seen_dates:
                raise ValueError("duplicate record dates are not allowed")

            if previous_record_date is not None and record.date <= previous_record_date:
                raise ValueError("records must be strictly increasing by date")

            seen_dates.add(record.date)
            previous_record_date = record.date

            if record.symbol != self.symbol:
                raise ValueError("record symbol must match fetch result symbol")

            if record.provider_name != self.provider.provider_name:
                raise ValueError("record provider_name must match provider.provider_name")

            if record.date < self.start_date or record.date > self.end_date:
                raise ValueError("record date must be within requested date range")

    def _validate_failed(self) -> None:
        if self.records:
            raise ValueError("records must be empty when status is FAILED")

        if self.records_count != 0:
            raise ValueError("records_count must be 0 when status is FAILED")

        if self.first_record_date is not None:
            raise ValueError("first_record_date must be None when status is FAILED")

        if self.last_record_date is not None:
            raise ValueError("last_record_date must be None when status is FAILED")
