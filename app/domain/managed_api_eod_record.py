"""Managed API EOD OHLCV record contract definitions."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum


class ManagedApiPriceMode(Enum):
    """Allowed price modes for future managed API EOD records."""

    RAW = "RAW"
    ADJUSTED = "ADJUSTED"


@dataclass(frozen=True, slots=True)
class ManagedApiEodRecord:
    """Strict future provider-returned daily OHLCV record contract."""

    provider_name: str
    symbol: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    price_mode: ManagedApiPriceMode
    timezone: str
    adjusted_close: float | None
    corporate_action_adjusted: bool
    source_timestamp_utc: datetime | None
    provider_record_id: str | None
    notes: str

    def __post_init__(self) -> None:
        self._validate_non_empty_string("provider_name")
        self._validate_non_empty_string("symbol")
        self._validate_date()
        self._validate_price("open")
        self._validate_price("high")
        self._validate_price("low")
        self._validate_price("close")
        self._validate_volume()
        self._validate_price_relationships()
        self._validate_price_mode()
        self._validate_non_empty_string("timezone")
        self._validate_adjusted_close()
        self._validate_corporate_action_adjusted()
        self._validate_source_timestamp_utc()
        self._validate_provider_record_id()
        self._validate_non_empty_string("notes")

    def _validate_non_empty_string(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not str:
            raise ValueError(f"{field_name} must be a string")

        if not value.strip():
            raise ValueError(f"{field_name} must not be empty")

    def _validate_date(self) -> None:
        if type(self.date) is not date:
            raise ValueError("date must be a datetime.date instance")

        if self.date > date.today():
            raise ValueError("date must not be in the future")

    def _validate_price(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not float:
            raise ValueError(f"{field_name} must be a float")

        if value <= 0:
            raise ValueError(f"{field_name} must be > 0")

    def _validate_volume(self) -> None:
        if type(self.volume) is not float:
            raise ValueError("volume must be a float")

        if self.volume < 0:
            raise ValueError("volume must be >= 0")

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

    def _validate_price_mode(self) -> None:
        if not isinstance(self.price_mode, ManagedApiPriceMode):
            raise ValueError("price_mode must be a valid ManagedApiPriceMode value")

    def _validate_adjusted_close(self) -> None:
        if self.adjusted_close is None:
            if self.price_mode is ManagedApiPriceMode.ADJUSTED:
                raise ValueError(
                    "adjusted_close must be provided when price_mode is ADJUSTED"
                )
            return

        if type(self.adjusted_close) is not float:
            raise ValueError("adjusted_close must be a float")

        if self.adjusted_close <= 0:
            raise ValueError("adjusted_close must be > 0")

    def _validate_corporate_action_adjusted(self) -> None:
        if type(self.corporate_action_adjusted) is not bool:
            raise ValueError("corporate_action_adjusted must be bool")

        if (
            self.price_mode is ManagedApiPriceMode.ADJUSTED
            and self.corporate_action_adjusted is not True
        ):
            raise ValueError(
                "corporate_action_adjusted must be True when price_mode is ADJUSTED"
            )

    def _validate_source_timestamp_utc(self) -> None:
        if self.source_timestamp_utc is None:
            return

        if type(self.source_timestamp_utc) is not datetime:
            raise ValueError("source_timestamp_utc must be a datetime.datetime instance")

        if (
            self.source_timestamp_utc.tzinfo is None
            or self.source_timestamp_utc.utcoffset() is None
        ):
            raise ValueError("source_timestamp_utc must be timezone-aware UTC")

        if self.source_timestamp_utc.utcoffset() != timedelta(0):
            raise ValueError("source_timestamp_utc must be timezone-aware UTC")

    def _validate_provider_record_id(self) -> None:
        if self.provider_record_id is None:
            return

        if type(self.provider_record_id) is not str:
            raise ValueError("provider_record_id must be a string")

        if not self.provider_record_id.strip():
            raise ValueError("provider_record_id must not be empty")
