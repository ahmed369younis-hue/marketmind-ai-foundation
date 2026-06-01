"""Real local CSV batch run result contract definitions."""

from dataclasses import dataclass
from enum import Enum

from app.domain.data_ingestion_result import DataIngestionStatus
from app.domain.local_csv_quality_validation import LocalCsvQualityValidationResult


class LocalCsvBatchRunStatus(Enum):
    """Allowed status values for future real local CSV batch run records."""

    READY_FOR_ENGINE_PLANNING = "READY_FOR_ENGINE_PLANNING"
    BLOCKED_BY_QUALITY_GATE = "BLOCKED_BY_QUALITY_GATE"
    FAILED_INGESTION = "FAILED_INGESTION"


@dataclass(frozen=True, slots=True)
class LocalCsvBatchRunResult:
    """Strict record for a future local CSV batch run after quality validation."""

    validation_result: LocalCsvQualityValidationResult
    status: LocalCsvBatchRunStatus
    run_label: str
    notes: str

    def __post_init__(self) -> None:
        if not isinstance(self.validation_result, LocalCsvQualityValidationResult):
            raise ValueError(
                "validation_result must be a LocalCsvQualityValidationResult instance"
            )

        if not isinstance(self.status, LocalCsvBatchRunStatus):
            raise ValueError("status must be a valid LocalCsvBatchRunStatus value")

        self._validate_non_empty_string("run_label")
        self._validate_non_empty_string("notes")
        self._validate_status_matches_validation_result()

    def _validate_non_empty_string(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not str:
            raise ValueError(f"{field_name} must be a string")

        if not value.strip():
            raise ValueError(f"{field_name} must not be empty")

    def _validate_status_matches_validation_result(self) -> None:
        ingestion_status = self.validation_result.batch.result.status
        quality_gate_passed = self.validation_result.quality_gate_passed

        if ingestion_status == DataIngestionStatus.FAILED:
            expected_status = LocalCsvBatchRunStatus.FAILED_INGESTION
        elif quality_gate_passed:
            expected_status = LocalCsvBatchRunStatus.READY_FOR_ENGINE_PLANNING
        else:
            expected_status = LocalCsvBatchRunStatus.BLOCKED_BY_QUALITY_GATE

        if self.status != expected_status:
            raise ValueError("status must match local CSV quality validation result")
