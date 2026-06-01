"""Runtime credential callback boundary for managed API planning."""

import os
from collections.abc import Callable
from typing import TypeVar

from app.domain.managed_api_credential_contract import (
    ManagedApiCredentialAccessResult,
    ManagedApiCredentialStatus,
)
from app.domain.managed_api_provider_contract import ManagedApiProviderContract


T = TypeVar("T")


def use_managed_api_runtime_credential(
    provider: ManagedApiProviderContract,
    credential_access: ManagedApiCredentialAccessResult,
    consumer: Callable[[str], T],
) -> T:
    if not isinstance(provider, ManagedApiProviderContract):
        raise ValueError("provider must be a ManagedApiProviderContract instance")

    if not isinstance(credential_access, ManagedApiCredentialAccessResult):
        raise ValueError(
            "credential_access must be a ManagedApiCredentialAccessResult instance"
        )

    if credential_access.provider is not provider:
        raise ValueError("credential_access.provider must reference provider")

    if credential_access.status is not ManagedApiCredentialStatus.AVAILABLE:
        raise ValueError("credential_access.status must be AVAILABLE")

    if credential_access.credential_present is not True:
        raise ValueError("credential_access.credential_present must be True")

    if credential_access.credential_env_var != provider.credential_env_var:
        raise ValueError(
            "credential_access.credential_env_var must equal provider.credential_env_var"
        )

    if not callable(consumer):
        raise ValueError("consumer must be callable")

    credential_value = os.environ.get(provider.credential_env_var)
    if credential_value is None or not credential_value.strip():
        raise ValueError("managed API runtime credential is unavailable")

    result = consumer(credential_value)
    if isinstance(result, str) and result == credential_value:
        raise ValueError("consumer result must not be the raw credential")

    return result
