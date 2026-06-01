"""Provider documentation evidence contract definitions."""

from dataclasses import dataclass
from datetime import date
from enum import Enum


class ManagedApiDocumentationEvidenceStatus(Enum):
    """Allowed documentation evidence statuses."""

    DOCUMENTED = "DOCUMENTED"
    MISSING = "MISSING"
    CONFLICTING = "CONFLICTING"
    UNVERIFIED = "UNVERIFIED"


@dataclass(frozen=True, slots=True)
class ManagedApiProviderDocumentationEvidence:
    """Strict record for future provider documentation evidence."""

    provider_name: str
    evidence_status: ManagedApiDocumentationEvidenceStatus
    documentation_reference: str
    documentation_retrieved_date: date
    supports_eod_ohlcv_evidence: str
    supports_adjusted_prices_evidence: str
    supports_corporate_actions_evidence: str
    supported_asset_classes_evidence: str
    rate_limit_evidence: str
    legal_access_evidence: str
    notes: str

    def __post_init__(self) -> None:
        self._validate_non_empty_string("provider_name")
        self._validate_evidence_status()
        self._validate_non_empty_string("documentation_reference")
        self._validate_documentation_retrieved_date()

        for field_name in (
            "supports_eod_ohlcv_evidence",
            "supports_adjusted_prices_evidence",
            "supports_corporate_actions_evidence",
            "supported_asset_classes_evidence",
            "rate_limit_evidence",
            "legal_access_evidence",
            "notes",
        ):
            self._validate_non_empty_string(field_name)

    def _validate_non_empty_string(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not str:
            raise ValueError(f"{field_name} must be a string")

        if not value.strip():
            raise ValueError(f"{field_name} must not be empty")

    def _validate_evidence_status(self) -> None:
        if not isinstance(self.evidence_status, ManagedApiDocumentationEvidenceStatus):
            raise ValueError(
                "evidence_status must be a valid "
                "ManagedApiDocumentationEvidenceStatus value"
            )

    def _validate_documentation_retrieved_date(self) -> None:
        if not isinstance(self.documentation_retrieved_date, date):
            raise ValueError("documentation_retrieved_date must be a date")

        if self.documentation_retrieved_date > date.today():
            raise ValueError("documentation_retrieved_date must not be in the future")
