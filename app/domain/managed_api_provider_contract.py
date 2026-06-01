"""Managed API provider metadata contract definitions."""

from dataclasses import dataclass
from enum import Enum

from app.domain.data_source_contract import (
    DataGranularity,
    DataSourceContract,
    DataSourceReliability,
    DataSourceType,
)


class ManagedApiProviderType(Enum):
    """Allowed managed API provider roles for future data access planning."""

    PRIMARY_INSTITUTIONAL = "PRIMARY_INSTITUTIONAL"
    SECONDARY_CROSS_CHECK = "SECONDARY_CROSS_CHECK"
    BROKER_SOURCED = "BROKER_SOURCED"


@dataclass(frozen=True, slots=True)
class ManagedApiProviderContract:
    """Strict metadata record for future managed API provider access."""

    provider_name: str
    provider_type: ManagedApiProviderType
    source: DataSourceContract
    credential_env_var: str
    supports_eod_ohlcv: bool
    supports_adjusted_prices: bool
    supports_corporate_actions: bool
    supports_us_equities: bool
    supports_us_etfs: bool
    supports_fx: bool
    supports_commodities: bool
    supports_crypto: bool
    allowed_first_symbol: str
    rate_limit_notes: str
    legal_access_confirmed: bool
    notes: str

    def __post_init__(self) -> None:
        self._validate_non_empty_string("provider_name")
        self._validate_provider_type()
        self._validate_source()
        self._validate_credential_env_var()

        for field_name in (
            "supports_eod_ohlcv",
            "supports_adjusted_prices",
            "supports_corporate_actions",
            "supports_us_equities",
            "supports_us_etfs",
            "supports_fx",
            "supports_commodities",
            "supports_crypto",
        ):
            self._validate_bool(field_name)

        self._validate_allowed_first_symbol()
        self._validate_non_empty_string("rate_limit_notes")
        self._validate_legal_access_confirmed()
        self._validate_non_empty_string("notes")

    def _validate_non_empty_string(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not str:
            raise ValueError(f"{field_name} must be a string")

        if not value.strip():
            raise ValueError(f"{field_name} must not be empty")

    def _validate_provider_type(self) -> None:
        if not isinstance(self.provider_type, ManagedApiProviderType):
            raise ValueError(
                "provider_type must be a valid ManagedApiProviderType value"
            )

    def _validate_source(self) -> None:
        if not isinstance(self.source, DataSourceContract):
            raise ValueError("source must be a DataSourceContract instance")

        if self.source.source_type is not DataSourceType.REAL:
            raise ValueError("source.source_type must be REAL")

        if self.source.granularity is not DataGranularity.DAILY:
            raise ValueError("source.granularity must be DAILY")

        if self.source.supports_ohlcv is not True:
            raise ValueError("source.supports_ohlcv must be True")

        if self.source.reliability is DataSourceReliability.VERIFIED_HISTORICAL:
            raise ValueError("source.reliability must not be VERIFIED_HISTORICAL")

    def _validate_credential_env_var(self) -> None:
        self._validate_non_empty_string("credential_env_var")

        if self.credential_env_var != self.credential_env_var.upper():
            raise ValueError("credential_env_var must be uppercase")

        if " " in self.credential_env_var:
            raise ValueError("credential_env_var must not contain spaces")

    def _validate_bool(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not bool:
            raise ValueError(f"{field_name} must be bool")

    def _validate_allowed_first_symbol(self) -> None:
        self._validate_non_empty_string("allowed_first_symbol")

        if self.allowed_first_symbol != "SPY":
            raise ValueError("allowed_first_symbol must be SPY")

    def _validate_legal_access_confirmed(self) -> None:
        self._validate_bool("legal_access_confirmed")

        if self.legal_access_confirmed is not True:
            raise ValueError("legal_access_confirmed must be True")
