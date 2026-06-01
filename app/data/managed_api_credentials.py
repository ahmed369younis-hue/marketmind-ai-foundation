"""Environment credential reader for future managed API access."""

import hashlib
import os

from app.domain.managed_api_credential_contract import (
    ManagedApiCredentialAccessResult,
    ManagedApiCredentialStatus,
)
from app.domain.managed_api_provider_contract import ManagedApiProviderContract


def read_managed_api_credential(
    provider: ManagedApiProviderContract,
) -> ManagedApiCredentialAccessResult:
    if not isinstance(provider, ManagedApiProviderContract):
        raise ValueError("provider must be a ManagedApiProviderContract instance")

    credential_value = os.environ.get(provider.credential_env_var)

    if credential_value is None:
        return ManagedApiCredentialAccessResult(
            provider=provider,
            status=ManagedApiCredentialStatus.MISSING,
            credential_env_var=provider.credential_env_var,
            credential_present=False,
            credential_fingerprint=None,
            message="Managed API credential is missing",
        )

    if not credential_value.strip():
        return ManagedApiCredentialAccessResult(
            provider=provider,
            status=ManagedApiCredentialStatus.MISSING,
            credential_env_var=provider.credential_env_var,
            credential_present=False,
            credential_fingerprint=None,
            message="Managed API credential is empty",
        )

    fingerprint = hashlib.sha256(credential_value.encode("utf-8")).hexdigest()[:16]

    return ManagedApiCredentialAccessResult(
        provider=provider,
        status=ManagedApiCredentialStatus.AVAILABLE,
        credential_env_var=provider.credential_env_var,
        credential_present=True,
        credential_fingerprint=fingerprint,
        message="Managed API credential is available",
    )
