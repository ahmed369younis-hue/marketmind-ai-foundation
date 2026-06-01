"""Managed API fetch preflight guard utilities."""

from app.domain.managed_api_credential_contract import ManagedApiCredentialStatus
from app.domain.managed_api_fetch_request import (
    ManagedApiEodFetchRequest,
    ManagedApiFetchPricePreference,
)
from app.domain.managed_api_provider_adapter_port import (
    ManagedApiProviderAdapterCapability,
)


def can_execute_managed_api_fetch_preflight(
    request: ManagedApiEodFetchRequest,
    capability: ManagedApiProviderAdapterCapability,
) -> bool:
    """Return whether a future managed API fetch request is preflight-compatible."""

    if not isinstance(request, ManagedApiEodFetchRequest):
        raise ValueError("request must be a ManagedApiEodFetchRequest instance")

    if not isinstance(capability, ManagedApiProviderAdapterCapability):
        raise ValueError(
            "capability must be a ManagedApiProviderAdapterCapability instance"
        )

    if capability.provider is not request.provider:
        return False

    if capability.supports_fetch_eod is not True:
        return False

    if capability.supports_single_symbol_fetch is not True:
        return False

    if capability.supports_bulk_fetch is not False:
        return False

    if capability.supports_raw_prices is not True:
        return False

    if request.price_preference is ManagedApiFetchPricePreference.RAW:
        if capability.supports_raw_prices is not True:
            return False
    elif request.price_preference is ManagedApiFetchPricePreference.ADJUSTED:
        if capability.supports_adjusted_prices is not True:
            return False

        if request.provider.supports_adjusted_prices is not True:
            return False
    else:
        return False

    if request.credential_access.status is not ManagedApiCredentialStatus.AVAILABLE:
        return False

    if request.credential_access.credential_present is not True:
        return False

    if request.symbol != request.provider.allowed_first_symbol:
        return False

    return True
