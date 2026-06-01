"""Score output contract definitions."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class DailyScore:
    """Strict output contract for future daily score results."""

    date: date
    symbol: str
    smart_money_score: float

    def __post_init__(self) -> None:
        self._validate_date()
        self._validate_symbol()
        self._validate_smart_money_score()

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

    def _validate_smart_money_score(self) -> None:
        if type(self.smart_money_score) is not float:
            raise TypeError("smart_money_score must be a float")

        if not 0 <= self.smart_money_score <= 100:
            raise ValueError("smart_money_score must be within [0,100]")
