"""Daily dataset quality result contract definitions."""

from dataclasses import dataclass
from enum import Enum


class DataQualityCheck(Enum):
    """Allowed future daily dataset quality checks."""

    RECORD_COUNT_CHECK = "RECORD_COUNT_CHECK"
    DATE_RANGE_COVERAGE_CHECK = "DATE_RANGE_COVERAGE_CHECK"
    SYMBOL_CONSISTENCY_CHECK = "SYMBOL_CONSISTENCY_CHECK"
    OHLCV_VALIDITY_CHECK = "OHLCV_VALIDITY_CHECK"
    DAILY_CONTINUITY_CHECK = "DAILY_CONTINUITY_CHECK"
    MISSING_VALUE_CHECK = "MISSING_VALUE_CHECK"


@dataclass(frozen=True, slots=True)
class DataQualityResult:
    """Strict output shape for future daily dataset quality checks."""

    check: DataQualityCheck
    passed: bool
    metric_value: float
    details: str

    def __post_init__(self) -> None:
        if not isinstance(self.check, DataQualityCheck):
            raise ValueError("check must be a valid DataQualityCheck value")

        if type(self.passed) is not bool:
            raise ValueError("passed must be bool")

        if type(self.metric_value) is not float:
            raise ValueError("metric_value must be a float")

        if self.metric_value < 0:
            raise ValueError("metric_value must be >= 0")

        if type(self.details) is not str:
            raise ValueError("details must be a string")

        if not self.details.strip():
            raise ValueError("details must not be empty")
