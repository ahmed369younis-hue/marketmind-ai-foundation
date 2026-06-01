"""Signal output contract definitions."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class DailySignals:
    """Strict output contract for future daily signal computation."""

    date: date
    symbol: str
    accumulation_strength: float
    distribution_strength: float
    liquidity_inflow: float
    liquidity_outflow: float
    absorption_score: float
    fake_move_score: float

    def __post_init__(self) -> None:
        self._validate_date()
        self._validate_symbol()
        self._validate_signal_value("accumulation_strength")
        self._validate_signal_value("distribution_strength")
        self._validate_signal_value("liquidity_inflow")
        self._validate_signal_value("liquidity_outflow")
        self._validate_signal_value("absorption_score")
        self._validate_signal_value("fake_move_score")

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

    def _validate_signal_value(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not float:
            raise TypeError(f"{field_name} must be a float")

        if not 0 <= value <= 1:
            raise ValueError(f"{field_name} must be within [0,1]")
