"""Validation result output contract definitions."""

from dataclasses import dataclass
from datetime import date
from enum import Enum


class ValidationCheckType(Enum):
    """Allowed validation result check types."""

    FORWARD_VALIDATION = "FORWARD_VALIDATION"
    STABILITY_CHECK = "STABILITY_CHECK"
    FALSE_SIGNAL_DETECTION = "FALSE_SIGNAL_DETECTION"


@dataclass(frozen=True, slots=True)
class DailyValidationResult:
    """Strict output contract for future daily validation framework results."""

    date: date
    symbol: str
    check_type: ValidationCheckType
    passed: bool
    metric_value: float

    def __post_init__(self) -> None:
        self._validate_date()
        self._validate_symbol()
        self._validate_check_type()
        self._validate_passed()
        self._validate_metric_value()

    def _validate_date(self) -> None:
        if type(self.date) is not date:
            raise ValueError("date must be a datetime.date instance")

        if self.date > date.today():
            raise ValueError("date must not be in the future")

    def _validate_symbol(self) -> None:
        if type(self.symbol) is not str:
            raise ValueError("symbol must be a string")

        if not self.symbol.strip():
            raise ValueError("symbol must not be empty")

    def _validate_check_type(self) -> None:
        if not isinstance(self.check_type, ValidationCheckType):
            raise ValueError("check_type must be a valid ValidationCheckType value")

    def _validate_passed(self) -> None:
        if type(self.passed) is not bool:
            raise ValueError("passed must be bool")

    def _validate_metric_value(self) -> None:
        if type(self.metric_value) is not float:
            raise ValueError("metric_value must be a float")

        if self.metric_value < 0:
            raise ValueError("metric_value must be >= 0")
