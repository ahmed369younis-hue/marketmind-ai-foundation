"""Data source evaluation result contract definitions."""

from dataclasses import dataclass
from enum import Enum

from app.domain.data_source_contract import DataSourceReliability


class DataSourceEvaluationCheck(Enum):
    """Allowed future data source evaluation checks."""

    SOURCE_TYPE_CHECK = "SOURCE_TYPE_CHECK"
    GRANULARITY_CHECK = "GRANULARITY_CHECK"
    OHLCV_SUPPORT_CHECK = "OHLCV_SUPPORT_CHECK"
    ADJUSTED_PRICE_SUPPORT_CHECK = "ADJUSTED_PRICE_SUPPORT_CHECK"
    CORPORATE_ACTIONS_SUPPORT_CHECK = "CORPORATE_ACTIONS_SUPPORT_CHECK"
    TIMEZONE_CHECK = "TIMEZONE_CHECK"
    RELIABILITY_CLASSIFICATION_CHECK = "RELIABILITY_CLASSIFICATION_CHECK"


@dataclass(frozen=True, slots=True)
class DataSourceEvaluationResult:
    """Strict output shape for future source evaluation checks."""

    source_name: str
    check: DataSourceEvaluationCheck
    passed: bool
    reliability_after_check: DataSourceReliability
    details: str

    def __post_init__(self) -> None:
        self._validate_non_empty_string("source_name")
        self._validate_enum("check", DataSourceEvaluationCheck)
        self._validate_bool("passed")
        self._validate_enum("reliability_after_check", DataSourceReliability)
        self._validate_non_empty_string("details")

    def _validate_non_empty_string(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not str:
            raise ValueError(f"{field_name} must be a string")

        if not value.strip():
            raise ValueError(f"{field_name} must not be empty")

    def _validate_enum(self, field_name: str, enum_type: type[Enum]) -> None:
        value = getattr(self, field_name)
        if not isinstance(value, enum_type):
            raise ValueError(f"{field_name} must be a valid {enum_type.__name__} value")

    def _validate_bool(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not bool:
            raise ValueError(f"{field_name} must be bool")
