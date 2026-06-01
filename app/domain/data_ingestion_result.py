"""Data ingestion result contract definitions."""

from dataclasses import dataclass
from datetime import date
from enum import Enum

from app.domain.data_ingestion_plan import DataIngestionPlan
from app.domain.data_source_contract import DataSourceReliability


class DataIngestionStatus(Enum):
    """Allowed future ingestion outcome statuses."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class DataIngestionResult:
    """Strict result record for future ingestion outcomes, without ingestion behavior."""

    plan: DataIngestionPlan
    status: DataIngestionStatus
    records_count: int
    first_date: date | None
    last_date: date | None
    reliability_after_ingestion: DataSourceReliability
    message: str

    def __post_init__(self) -> None:
        if not isinstance(self.plan, DataIngestionPlan):
            raise ValueError("plan must be a valid DataIngestionPlan instance")

        if not isinstance(self.status, DataIngestionStatus):
            raise ValueError("status must be a valid DataIngestionStatus value")

        if type(self.records_count) is not int:
            raise ValueError("records_count must be an integer")

        if self.records_count < 0:
            raise ValueError("records_count must be greater than or equal to 0")

        if self.status == DataIngestionStatus.SUCCESS:
            self._validate_success_result()
        elif self.status == DataIngestionStatus.FAILED:
            self._validate_failed_result()

        if not isinstance(self.reliability_after_ingestion, DataSourceReliability):
            raise ValueError(
                "reliability_after_ingestion must be a valid DataSourceReliability value"
            )

        if self.reliability_after_ingestion == DataSourceReliability.VERIFIED_HISTORICAL:
            raise ValueError("reliability_after_ingestion must not be VERIFIED_HISTORICAL")

        self._validate_non_empty_string("message")

    def _validate_success_result(self) -> None:
        if self.records_count == 0:
            raise ValueError("records_count must be greater than 0 when status is SUCCESS")

        self._validate_date_not_future("first_date")
        self._validate_date_not_future("last_date")

        if self.last_date < self.first_date:
            raise ValueError("last_date must be greater than or equal to first_date")

        if self.first_date < self.plan.start_date:
            raise ValueError("first_date must be greater than or equal to plan.start_date")

        if self.last_date > self.plan.end_date:
            raise ValueError("last_date must be less than or equal to plan.end_date")

    def _validate_failed_result(self) -> None:
        if self.records_count != 0:
            raise ValueError("records_count must be 0 when status is FAILED")

        if self.first_date is not None:
            raise ValueError("first_date must be None when status is FAILED")

        if self.last_date is not None:
            raise ValueError("last_date must be None when status is FAILED")

    def _validate_date_not_future(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if value is None:
            raise ValueError(f"{field_name} must not be None when status is SUCCESS")

        if type(value) is not date:
            raise ValueError(f"{field_name} must be a date")

        if value > date.today():
            raise ValueError(f"{field_name} must not be in the future")

    def _validate_non_empty_string(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not str:
            raise ValueError(f"{field_name} must be a string")

        if not value.strip():
            raise ValueError(f"{field_name} must not be empty")
