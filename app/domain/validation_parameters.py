"""Validation framework parameter contract definitions."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ValidationParameters:
    """Required parameter contract for future validation framework behavior."""

    high_score_threshold: float
    forward_window: int
    forward_return_threshold: float
    stability_window: int
    stability_min_persistence_ratio: float
    false_signal_window: int
    false_signal_reversal_threshold: float

    def __post_init__(self) -> None:
        self._validate_float("high_score_threshold")
        self._validate_int("forward_window")
        self._validate_float("forward_return_threshold")
        self._validate_int("stability_window")
        self._validate_float("stability_min_persistence_ratio")
        self._validate_int("false_signal_window")
        self._validate_float("false_signal_reversal_threshold")
        self._validate_ranges()

    def _validate_float(self, field_name: str) -> None:
        if type(getattr(self, field_name)) is not float:
            raise ValueError(f"{field_name} must be a float")

    def _validate_int(self, field_name: str) -> None:
        if type(getattr(self, field_name)) is not int:
            raise ValueError(f"{field_name} must be an int")

    def _validate_ranges(self) -> None:
        if not 0 <= self.high_score_threshold <= 100:
            raise ValueError("high_score_threshold must be within [0,100]")

        if self.forward_window <= 0:
            raise ValueError("forward_window must be > 0")

        if self.forward_return_threshold < 0:
            raise ValueError("forward_return_threshold must be >= 0")

        if self.stability_window <= 1:
            raise ValueError("stability_window must be > 1")

        if not 0 <= self.stability_min_persistence_ratio <= 1:
            raise ValueError("stability_min_persistence_ratio must be within [0,1]")

        if self.false_signal_window <= 0:
            raise ValueError("false_signal_window must be > 0")

        if self.false_signal_reversal_threshold < 0:
            raise ValueError("false_signal_reversal_threshold must be >= 0")
