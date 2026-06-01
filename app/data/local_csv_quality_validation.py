"""Local CSV quality validation orchestration utilities."""

from app.data.local_csv_ingestion import ingest_local_csv
from app.data.quality_evaluation import evaluate_daily_dataset_quality
from app.data.quality_gate import can_pass_data_quality_gate
from app.domain.data_ingestion_plan import DataIngestionPlan
from app.domain.local_csv_contract import LocalCsvIngestionContract
from app.domain.local_csv_quality_validation import LocalCsvQualityValidationResult


def validate_local_csv_quality(
    csv_contract: LocalCsvIngestionContract,
    plan: DataIngestionPlan,
) -> LocalCsvQualityValidationResult:
    """Ingest a local CSV and apply existing data quality checks and gate."""

    batch = ingest_local_csv(csv_contract, plan)
    quality_results = evaluate_daily_dataset_quality(batch)
    gate_result = can_pass_data_quality_gate(quality_results)

    return LocalCsvQualityValidationResult(
        batch=batch,
        quality_results=quality_results,
        quality_gate_passed=gate_result,
    )
