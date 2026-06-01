"""Public-safe local CSV quality evidence report contracts."""

from dataclasses import dataclass
from datetime import date

from app.domain.local_csv_batch_run import LocalCsvBatchRunResult
from app.domain.local_csv_quality_validation import LocalCsvQualityValidationResult


LIMITATIONS = (
    "Public-safe summary of existing local CSV quality validation outputs only.",
    "Not real-data verification, source reliability approval, historical verification, or production approval.",
    "Not permission for engine execution, market analysis, trading output, or financial conclusions.",
)


@dataclass(frozen=True, slots=True)
class LocalCsvQualityCheckEvidence:
    """Safe pass/fail summary for one existing quality check."""

    check_name: str
    passed: bool

    def __post_init__(self) -> None:
        if type(self.check_name) is not str:
            raise ValueError("check_name must be a string")

        if not self.check_name.strip():
            raise ValueError("check_name must not be empty")

        if type(self.passed) is not bool:
            raise ValueError("passed must be bool")


@dataclass(frozen=True, slots=True)
class LocalCsvQualityEvidenceReport:
    """Immutable public-safe summary of existing local CSV quality outputs."""

    source_label: str
    symbol: str
    requested_start_date: date
    requested_end_date: date
    records_count: int
    first_date: date | None
    last_date: date | None
    quality_checks: tuple[LocalCsvQualityCheckEvidence, ...]
    quality_gate_passed: bool
    limitations: tuple[str, ...]
    is_real_data_verification: bool
    approves_source_reliability: bool
    verifies_historical_data: bool
    approves_production_use: bool
    permits_engine_execution: bool
    permits_market_analysis: bool
    permits_trading_output: bool
    permits_financial_conclusions: bool

    def __post_init__(self) -> None:
        self._validate_non_empty_string("source_label")
        self._validate_non_empty_string("symbol")
        self._validate_date("requested_start_date")
        self._validate_date("requested_end_date")

        if self.requested_end_date < self.requested_start_date:
            raise ValueError("requested_end_date must be greater than or equal to requested_start_date")

        if type(self.records_count) is not int:
            raise ValueError("records_count must be an integer")

        if self.records_count < 0:
            raise ValueError("records_count must be greater than or equal to 0")

        self._validate_optional_date("first_date")
        self._validate_optional_date("last_date")

        if self.first_date is not None and self.last_date is not None and self.last_date < self.first_date:
            raise ValueError("last_date must be greater than or equal to first_date")

        if self.records_count == 0 and (self.first_date is not None or self.last_date is not None):
            raise ValueError("first_date and last_date must be None when records_count is 0")

        if type(self.quality_checks) is not tuple:
            raise ValueError("quality_checks must be a tuple")

        if not self.quality_checks:
            raise ValueError("quality_checks must not be empty")

        if any(not isinstance(item, LocalCsvQualityCheckEvidence) for item in self.quality_checks):
            raise ValueError("all quality_checks must be LocalCsvQualityCheckEvidence instances")

        if type(self.quality_gate_passed) is not bool:
            raise ValueError("quality_gate_passed must be bool")

        if type(self.limitations) is not tuple:
            raise ValueError("limitations must be a tuple")

        if not self.limitations:
            raise ValueError("limitations must not be empty")

        if any(type(item) is not str or not item.strip() for item in self.limitations):
            raise ValueError("all limitations must be non-empty strings")

        self._validate_false_flag("is_real_data_verification")
        self._validate_false_flag("approves_source_reliability")
        self._validate_false_flag("verifies_historical_data")
        self._validate_false_flag("approves_production_use")
        self._validate_false_flag("permits_engine_execution")
        self._validate_false_flag("permits_market_analysis")
        self._validate_false_flag("permits_trading_output")
        self._validate_false_flag("permits_financial_conclusions")

    def _validate_non_empty_string(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not str:
            raise ValueError(f"{field_name} must be a string")

        if not value.strip():
            raise ValueError(f"{field_name} must not be empty")

    def _validate_date(self, field_name: str) -> None:
        if type(getattr(self, field_name)) is not date:
            raise ValueError(f"{field_name} must be a date")

    def _validate_optional_date(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if value is not None and type(value) is not date:
            raise ValueError(f"{field_name} must be a date or None")

    def _validate_false_flag(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not bool:
            raise ValueError(f"{field_name} must be bool")

        if value is not False:
            raise ValueError(f"{field_name} must be False")


def build_local_csv_quality_evidence_report(
    result: LocalCsvQualityValidationResult | LocalCsvBatchRunResult,
) -> LocalCsvQualityEvidenceReport:
    """Build a safe evidence report from an existing local CSV validation result."""

    validation_result = _validation_result_from_input(result)
    batch = validation_result.batch
    plan = batch.plan
    ingestion_result = batch.result

    quality_checks = tuple(
        LocalCsvQualityCheckEvidence(
            check_name=quality_result.check.value,
            passed=quality_result.passed,
        )
        for quality_result in validation_result.quality_results
    )

    return LocalCsvQualityEvidenceReport(
        source_label=plan.source.name,
        symbol=plan.symbol,
        requested_start_date=plan.start_date,
        requested_end_date=plan.end_date,
        records_count=ingestion_result.records_count,
        first_date=ingestion_result.first_date,
        last_date=ingestion_result.last_date,
        quality_checks=quality_checks,
        quality_gate_passed=validation_result.quality_gate_passed,
        limitations=LIMITATIONS,
        is_real_data_verification=False,
        approves_source_reliability=False,
        verifies_historical_data=False,
        approves_production_use=False,
        permits_engine_execution=False,
        permits_market_analysis=False,
        permits_trading_output=False,
        permits_financial_conclusions=False,
    )


def _validation_result_from_input(
    result: LocalCsvQualityValidationResult | LocalCsvBatchRunResult,
) -> LocalCsvQualityValidationResult:
    if isinstance(result, LocalCsvQualityValidationResult):
        return result

    if isinstance(result, LocalCsvBatchRunResult):
        return result.validation_result

    raise ValueError("result must be a LocalCsvQualityValidationResult or LocalCsvBatchRunResult")
