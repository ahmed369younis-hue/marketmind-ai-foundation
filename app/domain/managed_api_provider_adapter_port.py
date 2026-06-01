"""Provider-neutral managed API adapter port contract definitions."""

from dataclasses import dataclass
from typing import Protocol

from app.domain.managed_api_fetch_request import ManagedApiEodFetchRequest
from app.domain.managed_api_fetch_result import ManagedApiEodFetchResult
from app.domain.managed_api_provider_contract import ManagedApiProviderContract


@dataclass(frozen=True, slots=True)
class ManagedApiProviderAdapterCapability:
    """Strict future provider adapter capability metadata contract."""

    provider: ManagedApiProviderContract
    adapter_name: str
    supports_fetch_eod: bool
    supports_raw_prices: bool
    supports_adjusted_prices: bool
    supports_single_symbol_fetch: bool
    supports_bulk_fetch: bool
    notes: str

    def __post_init__(self) -> None:
        self._validate_provider()
        self._validate_non_empty_string("adapter_name")
        self._validate_bool("supports_fetch_eod")
        self._validate_bool("supports_raw_prices")
        self._validate_bool("supports_adjusted_prices")
        self._validate_bool("supports_single_symbol_fetch")
        self._validate_bool("supports_bulk_fetch")
        self._validate_capability_policy()
        self._validate_non_empty_string("notes")

    def _validate_provider(self) -> None:
        if not isinstance(self.provider, ManagedApiProviderContract):
            raise ValueError("provider must be a ManagedApiProviderContract instance")

    def _validate_non_empty_string(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not str:
            raise ValueError(f"{field_name} must be a string")

        if not value.strip():
            raise ValueError(f"{field_name} must not be empty")

    def _validate_bool(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not bool:
            raise ValueError(f"{field_name} must be bool")

    def _validate_capability_policy(self) -> None:
        if self.supports_fetch_eod is not True:
            raise ValueError("supports_fetch_eod must be True")

        if self.supports_single_symbol_fetch is not True:
            raise ValueError("supports_single_symbol_fetch must be True")

        if self.supports_bulk_fetch is not False:
            raise ValueError(
                "supports_bulk_fetch must be False for the first implementation policy"
            )

        if self.supports_raw_prices is not True:
            raise ValueError("supports_raw_prices must be True")

        if (
            self.supports_adjusted_prices is True
            and self.provider.supports_adjusted_prices is not True
        ):
            raise ValueError(
                "provider.supports_adjusted_prices must be True when "
                "supports_adjusted_prices is True"
            )


class ManagedApiProviderAdapterPort(Protocol):
    """Provider-neutral Protocol for future managed API EOD adapters."""

    capability: ManagedApiProviderAdapterCapability

    def fetch_eod(
        self,
        request: ManagedApiEodFetchRequest,
    ) -> ManagedApiEodFetchResult:
        ...
