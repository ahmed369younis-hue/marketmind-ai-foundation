"""Managed API credential access result contract definitions."""

from dataclasses import dataclass
from enum import Enum

from app.domain.managed_api_provider_contract import ManagedApiProviderContract


class ManagedApiCredentialStatus(Enum):
    """Allowed future managed API credential access statuses."""

    AVAILABLE = "AVAILABLE"
    MISSING = "MISSING"
    INVALID = "INVALID"


@dataclass(frozen=True, slots=True)
class ManagedApiCredentialAccessResult:
    """Strict future managed API credential access result contract."""

    provider: ManagedApiProviderContract
    status: ManagedApiCredentialStatus
    credential_env_var: str
    credential_present: bool
    credential_fingerprint: str | None
    message: str

    def __post_init__(self) -> None:
        self._validate_provider()
        self._validate_status()
        self._validate_credential_env_var()
        self._validate_bool("credential_present")
        self._validate_non_empty_string("message")

        if self.status is ManagedApiCredentialStatus.AVAILABLE:
            self._validate_available()
        elif self.status is ManagedApiCredentialStatus.MISSING:
            self._validate_missing()
        elif self.status is ManagedApiCredentialStatus.INVALID:
            self._validate_invalid()

    def _validate_provider(self) -> None:
        if not isinstance(self.provider, ManagedApiProviderContract):
            raise ValueError("provider must be a ManagedApiProviderContract instance")

    def _validate_status(self) -> None:
        if not isinstance(self.status, ManagedApiCredentialStatus):
            raise ValueError(
                "status must be a valid ManagedApiCredentialStatus value"
            )

    def _validate_non_empty_string(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not str:
            raise ValueError(f"{field_name} must be a string")

        if not value.strip():
            raise ValueError(f"{field_name} must not be empty")

    def _validate_credential_env_var(self) -> None:
        self._validate_non_empty_string("credential_env_var")

        if self.credential_env_var != self.credential_env_var.upper():
            raise ValueError("credential_env_var must be uppercase")

        if " " in self.credential_env_var:
            raise ValueError("credential_env_var must not contain spaces")

        if self.credential_env_var != self.provider.credential_env_var:
            raise ValueError("credential_env_var must equal provider.credential_env_var")

    def _validate_bool(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not bool:
            raise ValueError(f"{field_name} must be bool")

    def _validate_fingerprint_required(self) -> None:
        if self.credential_fingerprint is None:
            raise ValueError("credential_fingerprint must not be None")

        if type(self.credential_fingerprint) is not str:
            raise ValueError("credential_fingerprint must be a string")

        if not self.credential_fingerprint.strip():
            raise ValueError("credential_fingerprint must not be empty")

        if len(self.credential_fingerprint) > 16:
            raise ValueError("credential_fingerprint length must be <= 16")

    def _validate_available(self) -> None:
        if self.credential_present is not True:
            raise ValueError("credential_present must be True when status is AVAILABLE")

        self._validate_fingerprint_required()

    def _validate_missing(self) -> None:
        if self.credential_present is not False:
            raise ValueError("credential_present must be False when status is MISSING")

        if self.credential_fingerprint is not None:
            raise ValueError("credential_fingerprint must be None when status is MISSING")

    def _validate_invalid(self) -> None:
        if self.credential_present is not True:
            raise ValueError("credential_present must be True when status is INVALID")

        self._validate_fingerprint_required()
