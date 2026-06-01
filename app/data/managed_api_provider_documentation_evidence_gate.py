"""Provider evidence planning gate."""

from app.domain.managed_api_provider_documentation_evidence import (
    ManagedApiDocumentationEvidenceStatus,
    ManagedApiProviderDocumentationEvidence,
)


_REQUIRED_TEXT_FIELDS = (
    "documentation_reference",
    "supports_eod_ohlcv_evidence",
    "supports_adjusted_prices_evidence",
    "supports_corporate_actions_evidence",
    "supported_asset_classes_evidence",
    "rate_limit_evidence",
    "legal_access_evidence",
    "notes",
)


def can_use_provider_documentation_evidence_for_planning(
    evidence: ManagedApiProviderDocumentationEvidence,
) -> bool:
    if not isinstance(evidence, ManagedApiProviderDocumentationEvidence):
        raise ValueError(
            "evidence must be a ManagedApiProviderDocumentationEvidence instance"
        )

    if evidence.evidence_status is not ManagedApiDocumentationEvidenceStatus.DOCUMENTED:
        return False

    return all(
        _has_text(getattr(evidence, field_name))
        for field_name in _REQUIRED_TEXT_FIELDS
    )


def _has_text(value: object) -> bool:
    return type(value) is str and bool(value.strip())
