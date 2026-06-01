"""Market phase output contract definitions."""

from dataclasses import dataclass
from datetime import date
from enum import Enum


class MarketPhase(Enum):
    """Allowed market phase output values."""

    ACCUMULATION = "ACCUMULATION"
    DISTRIBUTION = "DISTRIBUTION"
    MARKUP = "MARKUP"
    MARKDOWN = "MARKDOWN"


@dataclass(frozen=True, slots=True)
class DailyMarketPhase:
    """Strict output contract for future daily market phase classification."""

    date: date
    symbol: str
    phase: MarketPhase

    def __post_init__(self) -> None:
        self._validate_date()
        self._validate_symbol()
        self._validate_phase()

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

    def _validate_phase(self) -> None:
        if not isinstance(self.phase, MarketPhase):
            raise ValueError("phase must be a valid MarketPhase value")
