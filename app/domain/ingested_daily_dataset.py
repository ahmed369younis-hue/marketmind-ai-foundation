"""Ingested daily dataset batch contract definitions."""

from dataclasses import dataclass

from app.domain.data_contract import DailyMarketData
from app.domain.data_ingestion_plan import DataIngestionPlan
from app.domain.data_ingestion_result import DataIngestionResult, DataIngestionStatus
from app.domain.dataset_validation import validate_daily_dataset


@dataclass(frozen=True, slots=True)
class IngestedDailyDataset:
    """Strict batch contract linking ingestion planning, result, and daily records."""

    plan: DataIngestionPlan
    result: DataIngestionResult
    records: list[DailyMarketData]

    def __post_init__(self) -> None:
        if not isinstance(self.plan, DataIngestionPlan):
            raise ValueError("plan must be a valid DataIngestionPlan instance")

        if not isinstance(self.result, DataIngestionResult):
            raise ValueError("result must be a valid DataIngestionResult instance")

        if self.result.plan is not self.plan:
            raise ValueError("result.plan must reference the same plan object")

        if type(self.records) is not list:
            raise ValueError("records must be a list")

        if self.result.status == DataIngestionStatus.FAILED:
            self._validate_failed_batch()
        elif self.result.status == DataIngestionStatus.SUCCESS:
            self._validate_success_batch()

    def _validate_failed_batch(self) -> None:
        if self.records:
            raise ValueError("records must be empty when result status is FAILED")

    def _validate_success_batch(self) -> None:
        if not self.records:
            raise ValueError("records must not be empty when result status is SUCCESS")

        if len(self.records) != self.result.records_count:
            raise ValueError("records length must equal result.records_count")

        validate_daily_dataset(self.records)

        if any(record.symbol != self.plan.symbol for record in self.records):
            raise ValueError("every record symbol must equal plan.symbol")

        first_record_date = self.records[0].date
        last_record_date = self.records[-1].date

        if first_record_date != self.result.first_date:
            raise ValueError("first record date must equal result.first_date")

        if last_record_date != self.result.last_date:
            raise ValueError("last record date must equal result.last_date")

        if first_record_date < self.plan.start_date:
            raise ValueError("first record date must be greater than or equal to plan.start_date")

        if last_record_date > self.plan.end_date:
            raise ValueError("last record date must be less than or equal to plan.end_date")
