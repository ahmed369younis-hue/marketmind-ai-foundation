"""Confidence parameter contract definitions."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ConfidenceParameters:
    """Required parameter contract for future confidence computation."""

    consistency_window: int
    signal_active_threshold: float

    def __post_init__(self) -> None:
        self._validate_int("consistency_window")
        self._validate_float("signal_active_threshold")
        self._validate_ranges()

    def _validate_int(self, field_name: str) -> None:
        if type(getattr(self, field_name)) is not int:
            raise ValueError(f"{field_name} must be an int")

    def _validate_float(self, field_name: str) -> None:
        if type(getattr(self, field_name)) is not float:
            raise ValueError(f"{field_name} must be a float")

    def _validate_ranges(self) -> None:
        if self.consistency_window <= 1:
            raise ValueError("consistency_window must be > 1")

        if not 0 <= self.signal_active_threshold <= 1:
            raise ValueError("signal_active_threshold must be within [0,1]")
