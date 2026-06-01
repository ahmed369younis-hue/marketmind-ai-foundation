"""Local CSV batch run orchestration utilities."""

from app.data.local_csv_quality_validation import validate_local_csv_quality
from app.domain.data_ingestion_plan import DataIngestionPlan
from app.domain.data_ingestion_result import DataIngestionStatus
from app.domain.local_csv_batch_run import (
    LocalCsvBatchRunResult,
    LocalCsvBatchRunStatus,
)
from app.domain.local_csv_contract import LocalCsvIngestionContract


def run_local_csv_batch(
    csv_contract: LocalCsvIngestionContract,
    plan: DataIngestionPlan,
    run_label: str,
    notes: str,
) -> LocalCsvBatchRunResult:
    """Run local CSV quality validation and return a batch run result."""

    _validate_non_empty_text(run_label, "run_label")
    _validate_non_empty_text(notes, "notes")

    validation_result = validate_local_csv_quality(csv_contract, plan)
    status = _status_from_validation_result(validation_result)

    return LocalCsvBatchRunResult(
        validation_result=validation_result,
        status=status,
        run_label=run_label,
        notes=notes,
    )


def _validate_non_empty_text(value: str, field_name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must not be empty")


def _status_from_validation_result(
    validation_result: object,
) -> LocalCsvBatchRunStatus:
    if validation_result.batch.result.status == DataIngestionStatus.FAILED:
        return LocalCsvBatchRunStatus.FAILED_INGESTION

    if not validation_result.quality_gate_passed:
        return LocalCsvBatchRunStatus.BLOCKED_BY_QUALITY_GATE

    return LocalCsvBatchRunStatus.READY_FOR_ENGINE_PLANNING
