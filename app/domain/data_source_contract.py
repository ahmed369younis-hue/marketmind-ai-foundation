"""Data source metadata contract definitions."""

from dataclasses import dataclass
from enum import Enum


class DataSourceType(Enum):
    """Allowed source categories for future data evaluation."""

    REAL = "REAL"
    MOCK = "MOCK"
    SYNTHETIC = "SYNTHETIC"


class DataGranularity(Enum):
    """Allowed data granularity for the current phase."""

    DAILY = "DAILY"


class DataSourceReliability(Enum):
    """Allowed reliability classifications before data can be used."""

    UNVERIFIED = "UNVERIFIED"
    VERIFIED_STRUCTURE_ONLY = "VERIFIED_STRUCTURE_ONLY"
    VERIFIED_HISTORICAL = "VERIFIED_HISTORICAL"


@dataclass(frozen=True, slots=True)
class DataSourceContract:
    """Strict metadata record required before future data source use."""

    name: str
    source_type: DataSourceType
    granularity: DataGranularity
    reliability: DataSourceReliability
    supports_ohlcv: bool
    supports_adjusted_prices: bool
    supports_corporate_actions: bool
    timezone: str
    notes: str

    def __post_init__(self) -> None:
        self._validate_non_empty_string("name")
        self._validate_enum("source_type", DataSourceType)
        self._validate_enum("granularity", DataGranularity)
        self._validate_enum("reliability", DataSourceReliability)
        self._validate_bool("supports_ohlcv")
        self._validate_bool("supports_adjusted_prices")
        self._validate_bool("supports_corporate_actions")
        self._validate_non_empty_string("timezone")
        self._validate_non_empty_string("notes")

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
