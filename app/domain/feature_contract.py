"""Feature output contract definitions."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class DailyFeatures:
    """Strict output contract for future daily feature computation."""

    date: date
    symbol: str
    range_compression: float
    volume_trend: float
    price_momentum: float
    volume_spike: float

    def __post_init__(self) -> None:
        self._validate_date()
        self._validate_symbol()
        self._validate_normalized_feature("range_compression")
        self._validate_normalized_feature("volume_trend")
        self._validate_normalized_feature("price_momentum")
        self._validate_volume_spike()

    def _validate_date(self) -> None:
        if type(self.date) is not date:
            raise TypeError("date must be a datetime.date instance")

        if self.date > date.today():
            raise ValueError("date must not be in the future")

    def _validate_symbol(self) -> None:
        if type(self.symbol) is not str:
            raise TypeError("symbol must be a string")

        if not self.symbol.strip():
            raise ValueError("symbol must not be empty")

    def _validate_normalized_feature(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not float:
            raise TypeError(f"{field_name} must be a float")

        if not 0 <= value <= 1:
            raise ValueError(f"{field_name} must be within [0,1]")

    def _validate_volume_spike(self) -> None:
        if type(self.volume_spike) is not float:
            raise TypeError("volume_spike must be a float")

        if self.volume_spike < 0:
            raise ValueError("volume_spike must be >= 0")
