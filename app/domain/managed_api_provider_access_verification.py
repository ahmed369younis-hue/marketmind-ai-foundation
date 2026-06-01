"""Managed API provider access verification result contract definitions."""

import datetime
from dataclasses import dataclass
from enum import Enum

from app.domain.managed_api_credential_contract import (
    ManagedApiCredentialAccessResult,
    ManagedApiCredentialStatus,
)
from app.domain.managed_api_provider_contract import ManagedApiProviderContract


class ManagedApiProviderAccessVerificationStatus(Enum):
    """Allowed future managed API provider access verification statuses."""

    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    NOT_VERIFIED = "NOT_VERIFIED"


@dataclass(frozen=True, slots=True)
class ManagedApiProviderAccessVerificationResult:
    """Strict future provider access verification result contract."""

    provider: ManagedApiProviderContract
    credential_access: ManagedApiCredentialAccessResult
    status: ManagedApiProviderAccessVerificationStatus
    provider_name: str
    credential_env_var: str
    access_checked: bool
    verification_timestamp_utc: datetime.datetime | None
    message: str

    def __post_init__(self) -> None:
        self._validate_provider()
        self._validate_credential_access()
        self._validate_status()
        self._validate_provider_name()
        self._validate_credential_env_var()
        self._validate_bool("access_checked")
        self._validate_non_empty_string("message")

        if self.status is ManagedApiProviderAccessVerificationStatus.VERIFIED:
            self._validate_verified()
        elif self.status is ManagedApiProviderAccessVerificationStatus.FAILED:
            self._validate_failed()
        elif self.status is ManagedApiProviderAccessVerificationStatus.NOT_VERIFIED:
            self._validate_not_verified()

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

    def _validate_status(self) -> None:
        if not isinstance(
            self.status,
            ManagedApiProviderAccessVerificationStatus,
        ):
            raise ValueError(
                "status must be a valid ManagedApiProviderAccessVerificationStatus value"
            )

    def _validate_non_empty_string(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not str:
            raise ValueError(f"{field_name} must be a string")

        if not value.strip():
            raise ValueError(f"{field_name} must not be empty")

    def _validate_provider_name(self) -> None:
        self._validate_non_empty_string("provider_name")

        if self.provider_name != self.provider.provider_name:
            raise ValueError("provider_name must equal provider.provider_name")

    def _validate_credential_env_var(self) -> None:
        self._validate_non_empty_string("credential_env_var")

        if self.credential_env_var != self.provider.credential_env_var:
            raise ValueError("credential_env_var must equal provider.credential_env_var")

        if self.credential_env_var != self.credential_access.credential_env_var:
            raise ValueError(
                "credential_env_var must equal credential_access.credential_env_var"
            )

    def _validate_bool(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not bool:
            raise ValueError(f"{field_name} must be bool")

    def _validate_timestamp_required(self) -> datetime.datetime:
        if self.verification_timestamp_utc is None:
            raise ValueError("verification_timestamp_utc must not be None")

        if type(self.verification_timestamp_utc) is not datetime.datetime:
            raise ValueError(
                "verification_timestamp_utc must be a datetime.datetime instance"
            )

        if (
            self.verification_timestamp_utc.tzinfo is None
            or self.verification_timestamp_utc.utcoffset() is None
        ):
            raise ValueError("verification_timestamp_utc must be timezone-aware UTC")

        if self.verification_timestamp_utc.utcoffset() != datetime.timedelta(0):
            raise ValueError("verification_timestamp_utc must be timezone-aware UTC")

        if self.verification_timestamp_utc > datetime.datetime.now(
            datetime.timezone.utc
        ):
            raise ValueError("verification_timestamp_utc must not be in the future")

        return self.verification_timestamp_utc

    def _validate_verified(self) -> None:
        if self.access_checked is not True:
            raise ValueError("access_checked must be True when status is VERIFIED")

        if self.credential_access.status is not ManagedApiCredentialStatus.AVAILABLE:
            raise ValueError(
                "credential_access.status must be AVAILABLE when status is VERIFIED"
            )

        if self.credential_access.credential_present is not True:
            raise ValueError(
                "credential_access.credential_present must be True when status is VERIFIED"
            )

        self._validate_timestamp_required()

    def _validate_failed(self) -> None:
        if self.access_checked is not True:
            raise ValueError("access_checked must be True when status is FAILED")

        self._validate_timestamp_required()

    def _validate_not_verified(self) -> None:
        if self.access_checked is not False:
            raise ValueError("access_checked must be False when status is NOT_VERIFIED")

        if self.verification_timestamp_utc is not None:
            raise ValueError(
                "verification_timestamp_utc must be None when status is NOT_VERIFIED"
            )
