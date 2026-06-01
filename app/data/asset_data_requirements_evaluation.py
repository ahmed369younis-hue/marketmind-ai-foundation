"""Metadata-only evaluation gate for asset data requirements."""

from app.domain.asset_data_requirements import (
    AssetDataRequirements,
    MarketAsset,
    MarketSessionModel,
    VolumeModel,
)
from app.domain.asset_data_requirements_evaluation import (
    AssetDataRequirementsEvaluationCheck,
    AssetDataRequirementsEvaluationResult,
)


def evaluate_asset_data_requirements(
    requirements: AssetDataRequirements,
) -> list[AssetDataRequirementsEvaluationResult]:
    """Evaluate requirements for future data-source planning only."""

    if not isinstance(requirements, AssetDataRequirements):
        raise ValueError("requirements must be an AssetDataRequirements instance")

    return [
        _result(
            requirements,
            AssetDataRequirementsEvaluationCheck.ASSET_PROFILE_CHECK,
            _asset_profile_passed(requirements),
            "Asset profile is recognized for metadata-only planning.",
        ),
        _result(
            requirements,
            AssetDataRequirementsEvaluationCheck.SESSION_POLICY_CHECK,
            _session_policy_passed(requirements),
            "Session and timezone policy requirements match the asset profile.",
        ),
        _result(
            requirements,
            AssetDataRequirementsEvaluationCheck.VOLUME_MODEL_CHECK,
            _volume_model_passed(requirements),
            "Volume model matches the asset-specific planning boundary.",
        ),
        _result(
            requirements,
            AssetDataRequirementsEvaluationCheck.CALENDAR_POLICY_CHECK,
            _calendar_policy_passed(requirements),
            "Calendar policy requirements match the asset-specific planning boundary.",
        ),
        _result(
            requirements,
            AssetDataRequirementsEvaluationCheck.SOURCE_POLICY_CHECK,
            _source_policy_passed(requirements),
            "Source, quote, timestamp, and price-policy requirements are present where required.",
        ),
        _result(
            requirements,
            AssetDataRequirementsEvaluationCheck.CROSS_SOURCE_VALIDATION_CHECK,
            _cross_source_validation_passed(requirements),
            "Cross-source validation requirements match the asset-specific planning boundary.",
        ),
        _result(
            requirements,
            AssetDataRequirementsEvaluationCheck.LIQUIDITY_PROXY_CHECK,
            _liquidity_proxy_passed(requirements),
            "Liquidity proxy requirements match the asset-specific planning boundary.",
        ),
        _result(
            requirements,
            AssetDataRequirementsEvaluationCheck.FUTURES_ROLL_POLICY_CHECK,
            _futures_roll_policy_passed(requirements),
            "Futures roll and contract selection policy requirements match the asset profile.",
        ),
        _result(
            requirements,
            AssetDataRequirementsEvaluationCheck.FIRST_MARKET_PRIORITY_CHECK,
            _first_market_priority_passed(requirements),
            "First execution market priority is preserved.",
        ),
        _result(
            requirements,
            AssetDataRequirementsEvaluationCheck.NON_APPROVAL_BOUNDARY_CHECK,
            True,
            "Evaluation is planning-only and does not approve sources, providers, historical reliability, or production use.",
        ),
    ]


def is_asset_ready_for_data_source_planning(
    requirements: AssetDataRequirements,
) -> bool:
    """Return whether requirements pass the metadata-only planning gate."""

    results = evaluate_asset_data_requirements(requirements)
    return all(result.passed and result.planning_ready_only for result in results)


def _result(
    requirements: AssetDataRequirements,
    check: AssetDataRequirementsEvaluationCheck,
    passed: bool,
    details: str,
) -> AssetDataRequirementsEvaluationResult:
    return AssetDataRequirementsEvaluationResult(
        asset=requirements.asset,
        check=check,
        passed=passed,
        details=details,
        planning_ready_only=passed,
        source_approved=False,
        provider_approved=False,
        historical_reliability_verified=False,
        production_approved=False,
    )


def _asset_profile_passed(requirements: AssetDataRequirements) -> bool:
    return requirements.asset in set(MarketAsset)


def _session_policy_passed(requirements: AssetDataRequirements) -> bool:
    expected_sessions = {
        MarketAsset.US_EQUITIES_ETFS: MarketSessionModel.EXCHANGE_SESSION,
        MarketAsset.GOLD: MarketSessionModel.FUTURES_SESSION,
        MarketAsset.OIL: MarketSessionModel.FUTURES_SESSION,
        MarketAsset.BITCOIN: MarketSessionModel.TWENTY_FOUR_SEVEN,
        MarketAsset.EUR_USD: MarketSessionModel.FX_SESSION,
    }

    return (
        requirements.market_session_model == expected_sessions[requirements.asset]
        and requirements.requires_session_policy
        and requirements.requires_timezone_policy
    )


def _volume_model_passed(requirements: AssetDataRequirements) -> bool:
    if requirements.asset == MarketAsset.US_EQUITIES_ETFS:
        return requirements.volume_model in {
            VolumeModel.CENTRALIZED_EXCHANGE_VOLUME,
            VolumeModel.ETF_REPORTED_VOLUME,
        }

    expected_volume_models = {
        MarketAsset.GOLD: VolumeModel.FUTURES_CONTRACT_VOLUME,
        MarketAsset.OIL: VolumeModel.FUTURES_CONTRACT_VOLUME,
        MarketAsset.BITCOIN: VolumeModel.FRAGMENTED_EXCHANGE_VOLUME,
        MarketAsset.EUR_USD: VolumeModel.NO_CENTRALIZED_VOLUME,
    }

    return requirements.volume_model == expected_volume_models[requirements.asset]


def _calendar_policy_passed(requirements: AssetDataRequirements) -> bool:
    if requirements.asset == MarketAsset.BITCOIN:
        return requirements.requires_twenty_four_seven_calendar

    return not requirements.requires_twenty_four_seven_calendar


def _source_policy_passed(requirements: AssetDataRequirements) -> bool:
    if requirements.asset == MarketAsset.US_EQUITIES_ETFS:
        return (
            requirements.requires_adjusted_price_policy
            and requirements.requires_corporate_action_policy
            and not requirements.requires_exchange_source_policy
        )

    if requirements.asset == MarketAsset.BITCOIN:
        return (
            requirements.requires_exchange_source_policy
            and requirements.requires_quote_timestamp_validation
        )

    if requirements.asset == MarketAsset.EUR_USD:
        return (
            not requirements.requires_exchange_source_policy
            and requirements.requires_quote_timestamp_validation
        )

    return (
        not requirements.requires_exchange_source_policy
        and requirements.requires_quote_timestamp_validation
    )


def _cross_source_validation_passed(requirements: AssetDataRequirements) -> bool:
    if requirements.asset == MarketAsset.US_EQUITIES_ETFS:
        return not requirements.requires_cross_source_validation

    return requirements.requires_cross_source_validation


def _liquidity_proxy_passed(requirements: AssetDataRequirements) -> bool:
    if requirements.asset == MarketAsset.EUR_USD:
        return (
            requirements.volume_model == VolumeModel.NO_CENTRALIZED_VOLUME
            and requirements.requires_liquidity_proxy
        )

    return not requirements.requires_liquidity_proxy


def _futures_roll_policy_passed(requirements: AssetDataRequirements) -> bool:
    if requirements.asset in {MarketAsset.GOLD, MarketAsset.OIL}:
        return (
            requirements.requires_roll_logic
            and requirements.requires_contract_selection_policy
        )

    return (
        not requirements.requires_roll_logic
        and not requirements.requires_contract_selection_policy
    )


def _first_market_priority_passed(requirements: AssetDataRequirements) -> bool:
    if requirements.asset == MarketAsset.US_EQUITIES_ETFS:
        return requirements.is_first_execution_market

    return not requirements.is_first_execution_market
