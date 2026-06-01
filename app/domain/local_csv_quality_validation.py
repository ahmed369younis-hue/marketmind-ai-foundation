"""Local CSV quality validation result contract definitions."""

from dataclasses import dataclass

from app.data.quality_gate import can_pass_data_quality_gate
from app.domain.data_ingestion_result import DataIngestionStatus
from app.domain.data_quality_result import DataQualityResult
from app.domain.ingested_daily_dataset import IngestedDailyDataset


@dataclass(frozen=True, slots=True)
class LocalCsvQualityValidationResult:
    """Strict result container for local CSV quality validation orchestration."""

    batch: IngestedDailyDataset
    quality_results: list[DataQualityResult]
    quality_gate_passed: bool

    def __post_init__(self) -> None:
        if not isinstance(self.batch, IngestedDailyDataset):
            raise ValueError("batch must be an IngestedDailyDataset instance")

        if type(self.quality_results) is not list:
            raise ValueError("quality_results must be a list")

        if not self.quality_results:
            raise ValueError("quality_results must not be empty")

        if any(not isinstance(result, DataQualityResult) for result in self.quality_results):
            raise ValueError("all quality_results must be DataQualityResult instances")

        if type(self.quality_gate_passed) is not bool:
            raise ValueError("quality_gate_passed must be bool")

        expected_gate_result = can_pass_data_quality_gate(self.quality_results)
        if self.quality_gate_passed != expected_gate_result:
            raise ValueError("quality_gate_passed must match Data Quality Gate output")

        if (
            self.batch.result.status == DataIngestionStatus.FAILED
            and self.quality_gate_passed
        ):
            raise ValueError("failed ingestion batches cannot pass the quality gate")
