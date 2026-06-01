"""Managed API provider access verification planning gate."""

from app.domain.managed_api_credential_contract import ManagedApiCredentialStatus
from app.domain.managed_api_provider_access_verification import (
    ManagedApiProviderAccessVerificationResult,
    ManagedApiProviderAccessVerificationStatus,
)


def can_use_provider_access_verification_for_fetch_planning(
    verification_result: ManagedApiProviderAccessVerificationResult,
) -> bool:
    if not isinstance(
        verification_result,
        ManagedApiProviderAccessVerificationResult,
    ):
        raise ValueError(
            "verification_result must be a "
            "ManagedApiProviderAccessVerificationResult instance"
        )

    if (
        verification_result.status
        is not ManagedApiProviderAccessVerificationStatus.VERIFIED
    ):
        return False

    return (
        verification_result.access_checked is True
        and verification_result.credential_access.status
        is ManagedApiCredentialStatus.AVAILABLE
        and verification_result.credential_access.credential_present is True
        and verification_result.verification_timestamp_utc is not None
    )
