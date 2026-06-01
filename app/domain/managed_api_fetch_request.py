"""Managed API EOD fetch request contract definitions."""

from dataclasses import dataclass
from datetime import date
from enum import Enum

from app.domain.data_source_contract import DataGranularity
from app.domain.managed_api_credential_contract import (
    ManagedApiCredentialAccessResult,
    ManagedApiCredentialStatus,
)
from app.domain.managed_api_provider_contract import ManagedApiProviderContract


class ManagedApiFetchPricePreference(Enum):
    """Allowed future managed API EOD fetch price preferences."""

    RAW = "RAW"
    ADJUSTED = "ADJUSTED"


@dataclass(frozen=True, slots=True)
class ManagedApiEodFetchRequest:
    """Strict future managed API EOD fetch request contract."""

    provider: ManagedApiProviderContract
    credential_access: ManagedApiCredentialAccessResult
    symbol: str
    start_date: date
    end_date: date
    price_preference: ManagedApiFetchPricePreference
    timezone: str
    purpose: str

    def __post_init__(self) -> None:
        self._validate_provider()
        self._validate_credential_access()
        self._validate_symbol()
        self._validate_date("start_date")
        self._validate_date("end_date")
        self._validate_date_range()
        self._validate_price_preference()
        self._validate_provider_capabilities()
        self._validate_timezone()
        self._validate_non_empty_string("purpose")

    def _validate_provider(self) -> None:
        if not isinstance(self.provider, ManagedApiProviderContract):
            raise ValueError("provider must be a ManagedApiProviderContract instance")

    def _validate_credential_access(self) -> None:
        if not isinstance(self.credential_access, ManagedApiCredentialAccessResult):
            raise ValueError(
                "credential_access must be a ManagedApiCredentialAccessResult instance"
            )

        if self.credential_access.provider is not self.provider:
            raise ValueError("credential_access.provider must reference provider")

        if self.credential_access.status is not ManagedApiCredentialStatus.AVAILABLE:
            raise ValueError("credential_access.status must be AVAILABLE")

        if self.credential_access.credential_present is not True:
            raise ValueError("credential_access.credential_present must be True")

    def _validate_non_empty_string(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not str:
            raise ValueError(f"{field_name} must be a string")

        if not value.strip():
            raise ValueError(f"{field_name} must not be empty")

    def _validate_symbol(self) -> None:
        self._validate_non_empty_string("symbol")

        if self.symbol != self.provider.allowed_first_symbol:
            raise ValueError("symbol must equal provider.allowed_first_symbol")

    def _validate_date(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not date:
            raise ValueError(f"{field_name} must be a datetime.date instance")

        if value > date.today():
            raise ValueError(f"{field_name} must not be in the future")

    def _validate_date_range(self) -> None:
        if self.end_date < self.start_date:
            raise ValueError("end_date must be greater than or equal to start_date")

    def _validate_price_preference(self) -> None:
        if not isinstance(self.price_preference, ManagedApiFetchPricePreference):
            raise ValueError(
                "price_preference must be a valid ManagedApiFetchPricePreference value"
            )

        if (
            self.price_preference is ManagedApiFetchPricePreference.ADJUSTED
            and self.provider.supports_adjusted_prices is not True
        ):
            raise ValueError(
                "provider.supports_adjusted_prices must be True for ADJUSTED requests"
            )

    def _validate_provider_capabilities(self) -> None:
        if self.provider.supports_eod_ohlcv is not True:
            raise ValueError("provider.supports_eod_ohlcv must be True")

        if self.provider.source.granularity is not DataGranularity.DAILY:
            raise ValueError("provider.source.granularity must be DAILY")

    def _validate_timezone(self) -> None:
        self._validate_non_empty_string("timezone")

        if self.timezone != self.provider.source.timezone:
            raise ValueError("timezone must equal provider.source.timezone")
