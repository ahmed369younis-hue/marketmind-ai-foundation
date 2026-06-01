"""Daily market data contract definitions."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class DailyMarketData:
    """Strict daily market data record required before feature computation."""

    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    symbol: str

    def __post_init__(self) -> None:
        self._validate_date()
        self._validate_price("open")
        self._validate_price("high")
        self._validate_price("low")
        self._validate_price("close")
        self._validate_volume()
        self._validate_symbol()
        self._validate_price_relationships()

    def _validate_date(self) -> None:
        if type(self.date) is not date:
            raise TypeError("date must be a datetime.date instance")

        if self.date > date.today():
            raise ValueError("date must not be in the future")

    def _validate_price(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not float:
            raise TypeError(f"{field_name} must be a float")

        if value <= 0:
            raise ValueError(f"{field_name} must be > 0")

    def _validate_volume(self) -> None:
        if type(self.volume) is not float:
            raise TypeError("volume must be a float")

        if self.volume < 0:
            raise ValueError("volume must be >= 0")

    def _validate_symbol(self) -> None:
        if type(self.symbol) is not str:
            raise TypeError("symbol must be a string")

        if not self.symbol.strip():
            raise ValueError("symbol must not be empty")

    def _validate_price_relationships(self) -> None:
        if self.high < self.low:
            raise ValueError("high must be >= low")

        if self.high < self.open:
            raise ValueError("high must be >= open")

        if self.high < self.close:
            raise ValueError("high must be >= close")

        if self.low > self.open:
            raise ValueError("low must be <= open")

        if self.low > self.close:
            raise ValueError("low must be <= close")
