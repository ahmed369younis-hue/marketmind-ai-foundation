"""Confidence output contract definitions."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class DailyConfidence:
    """Strict output contract for future daily confidence results."""

    date: date
    symbol: str
    confidence: float

    def __post_init__(self) -> None:
        self._validate_date()
        self._validate_symbol()
        self._validate_confidence()

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

    def _validate_confidence(self) -> None:
        if type(self.confidence) is not float:
            raise ValueError("confidence must be a float")

        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be within [0,1]")
