"""Tiingo provider metadata construction."""

from app.data.managed_api_provider_documentation_evidence_gate import (
    can_use_provider_documentation_evidence_for_planning,
)
from app.domain.data_source_contract import (
    DataGranularity,
    DataSourceContract,
    DataSourceReliability,
    DataSourceType,
)
from app.domain.managed_api_provider_contract import (
    ManagedApiProviderContract,
    ManagedApiProviderType,
)
from app.domain.managed_api_provider_documentation_evidence import (
    ManagedApiProviderDocumentationEvidence,
)


def build_tiingo_provider_contract_from_documentation_evidence(
    evidence: ManagedApiProviderDocumentationEvidence,
) -> ManagedApiProviderContract:
    if not can_use_provider_documentation_evidence_for_planning(evidence):
        raise ValueError("provider documentation evidence is not sufficient for planning")

    source = DataSourceContract(
        name="Tiingo",
        source_type=DataSourceType.REAL,
        granularity=DataGranularity.DAILY,
        reliability=DataSourceReliability.VERIFIED_STRUCTURE_ONLY,
        supports_ohlcv=True,
        supports_adjusted_prices=True,
        supports_corporate_actions=True,
        timezone="America/New_York",
        notes=(
            "Documentation-gated metadata only; not API access verification "
            "or production approval."
        ),
    )

    return ManagedApiProviderContract(
        provider_name="Tiingo",
        provider_type=ManagedApiProviderType.SECONDARY_CROSS_CHECK,
        source=source,
        credential_env_var="TIINGO_API_KEY",
        supports_eod_ohlcv=True,
        supports_adjusted_prices=True,
        supports_corporate_actions=True,
        supports_us_equities=True,
        supports_us_etfs=True,
        supports_fx=False,
        supports_commodities=False,
        supports_crypto=False,
        allowed_first_symbol="SPY",
        rate_limit_notes=evidence.rate_limit_evidence,
        legal_access_confirmed=True,
        notes=(
            "Documentation-gated metadata only; Tiingo is not production-approved, "
            "source reliability is not VERIFIED_HISTORICAL, and no API access is "
            "verified."
        ),
    )
