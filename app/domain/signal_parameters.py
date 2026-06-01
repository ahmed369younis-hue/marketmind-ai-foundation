"""Signal parameter contract definitions."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SignalParameters:
    """Required parameter contract for future signal computation."""

    rolling_window: int
    threshold_std: float
    support_level: float
    breakout_level: float
    high_volume_threshold: float
    low_volume_threshold: float
    low_price_movement_threshold: float
    reversal_candles: int

    def __post_init__(self) -> None:
        self._validate_int("rolling_window")
        self._validate_int("reversal_candles")
        self._validate_float("threshold_std")
        self._validate_float("support_level")
        self._validate_float("breakout_level")
        self._validate_float("high_volume_threshold")
        self._validate_float("low_volume_threshold")
        self._validate_float("low_price_movement_threshold")
        self._validate_ranges()

    def _validate_int(self, field_name: str) -> None:
        if type(getattr(self, field_name)) is not int:
            raise ValueError(f"{field_name} must be an int")

    def _validate_float(self, field_name: str) -> None:
        if type(getattr(self, field_name)) is not float:
            raise ValueError(f"{field_name} must be a float")

    def _validate_ranges(self) -> None:
        if self.rolling_window <= 1:
            raise ValueError("rolling_window must be > 1")

        if self.threshold_std <= 0:
            raise ValueError("threshold_std must be > 0")

        if self.support_level <= 0:
            raise ValueError("support_level must be > 0")

        if self.breakout_level <= 0:
            raise ValueError("breakout_level must be > 0")

        if self.high_volume_threshold <= 0:
            raise ValueError("high_volume_threshold must be > 0")

        if self.low_volume_threshold < 0:
            raise ValueError("low_volume_threshold must be >= 0")

        if self.low_price_movement_threshold < 0:
            raise ValueError("low_price_movement_threshold must be >= 0")

        if self.reversal_candles <= 0:
            raise ValueError("reversal_candles must be > 0")
