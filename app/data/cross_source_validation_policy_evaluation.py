"""Metadata-only evaluation utility for cross-source validation policies."""

from app.domain.asset_data_requirements import MarketAsset
from app.domain.cross_source_validation_policy import (
    CrossSourceValidationPolicy,
    SourceValidationRole,
)
from app.domain.cross_source_validation_policy_evaluation import (
    CrossSourceValidationPolicyEvaluationCheck,
    CrossSourceValidationPolicyEvaluationResult,
)


def evaluate_cross_source_validation_policy(
    policy: CrossSourceValidationPolicy,
) -> list[CrossSourceValidationPolicyEvaluationResult]:
    """Evaluate a policy for future data-source planning only."""

    if not isinstance(policy, CrossSourceValidationPolicy):
        raise ValueError("policy must be a CrossSourceValidationPolicy instance")

    return [
        _result(
            policy,
            CrossSourceValidationPolicyEvaluationCheck.POLICY_SHAPE_CHECK,
            _policy_shape_passed(policy),
            "Policy shape is valid for metadata-only source planning.",
        ),
        _result(
            policy,
            CrossSourceValidationPolicyEvaluationCheck.REQUIRED_ROLES_CHECK,
            _required_roles_passed(policy),
            "Required source roles are internally consistent for planning.",
        ),
        _result(
            policy,
            CrossSourceValidationPolicyEvaluationCheck.INDEPENDENT_CROSS_CHECK_REQUIRED_CHECK,
            _independent_cross_check_passed(policy),
            "Independent cross-check source is required for future source planning.",
        ),
        _result(
            policy,
            CrossSourceValidationPolicyEvaluationCheck.CALENDAR_VALIDATION_CHECK,
            _calendar_validation_passed(policy),
            "Calendar validation requirement matches the asset planning profile.",
        ),
        _result(
            policy,
            CrossSourceValidationPolicyEvaluationCheck.TIMESTAMP_ALIGNMENT_CHECK,
            _timestamp_alignment_passed(policy),
            "Timestamp alignment requirement matches the asset planning profile.",
        ),
        _result(
            policy,
            CrossSourceValidationPolicyEvaluationCheck.PRICE_CONSISTENCY_POLICY_CHECK,
            _price_consistency_passed(policy),
            "Price or quote comparison policy is required for future planning.",
        ),
        _result(
            policy,
            CrossSourceValidationPolicyEvaluationCheck.VOLUME_CONSISTENCY_POLICY_CHECK,
            _volume_consistency_passed(policy),
            "Volume comparison policy matches the asset planning profile.",
        ),
        _result(
            policy,
            CrossSourceValidationPolicyEvaluationCheck.ASSET_SPECIFIC_REFERENCE_CHECK,
            _asset_specific_references_passed(policy),
            "Asset-specific reference requirements match the planning profile.",
        ),
        _result(
            policy,
            CrossSourceValidationPolicyEvaluationCheck.NON_APPROVAL_BOUNDARY_CHECK,
            _non_approval_boundary_passed(policy),
            "Policy evaluation does not select or approve providers, sources, reliability, or production use.",
        ),
        _result(
            policy,
            CrossSourceValidationPolicyEvaluationCheck.PLANNING_ONLY_BOUNDARY_CHECK,
            _planning_only_boundary_passed(policy),
            "Policy evaluation remains planning-only and does not create real-data readiness.",
        ),
    ]


def is_cross_source_policy_ready_for_data_source_planning(
    policy: CrossSourceValidationPolicy,
) -> bool:
    """Return whether the policy passes metadata-only planning checks."""

    results = evaluate_cross_source_validation_policy(policy)
    return all(result.passed and result.planning_ready_only for result in results)


def _result(
    policy: CrossSourceValidationPolicy,
    check: CrossSourceValidationPolicyEvaluationCheck,
    passed: bool,
    details: str,
) -> CrossSourceValidationPolicyEvaluationResult:
    return CrossSourceValidationPolicyEvaluationResult(
        asset=policy.asset,
        check=check,
        passed=passed,
        details=details,
        planning_ready_only=passed,
        provider_selected=False,
        provider_approved=False,
        source_reliability_approved=False,
        historical_reliability_verified=False,
        production_approved=False,
    )


def _policy_shape_passed(policy: CrossSourceValidationPolicy) -> bool:
    return (
        policy.asset in set(MarketAsset)
        and type(policy.required_source_roles) is tuple
        and _has_role(policy, SourceValidationRole.PRIMARY_MARKET_DATA_SOURCE)
    )


def _required_roles_passed(policy: CrossSourceValidationPolicy) -> bool:
    return (
        _has_role(policy, SourceValidationRole.PRIMARY_MARKET_DATA_SOURCE)
        and _flag_role_match(
            policy,
            policy.requires_independent_cross_source_check,
            SourceValidationRole.INDEPENDENT_CROSS_CHECK_SOURCE,
        )
        and _flag_role_match(
            policy,
            policy.requires_calendar_validation,
            SourceValidationRole.MARKET_CALENDAR_REFERENCE,
        )
        and _flag_role_match(
            policy,
            policy.requires_timestamp_alignment,
            SourceValidationRole.TIMESTAMP_ALIGNMENT_REFERENCE,
        )
        and _flag_role_match(
            policy,
            policy.requires_price_consistency_policy,
            SourceValidationRole.PRICE_CONSISTENCY_REFERENCE,
        )
        and _flag_role_match(
            policy,
            policy.requires_volume_consistency_policy,
            SourceValidationRole.VOLUME_CONSISTENCY_REFERENCE,
        )
        and _flag_role_match(
            policy,
            policy.requires_corporate_action_reference,
            SourceValidationRole.CORPORATE_ACTIONS_REFERENCE,
        )
        and _flag_role_match(
            policy,
            policy.requires_contract_specification_reference,
            SourceValidationRole.FUTURES_CONTRACT_SPECIFICATION_REFERENCE,
        )
        and _flag_role_match(
            policy,
            policy.requires_roll_policy_reference,
            SourceValidationRole.FUTURES_ROLL_POLICY_REFERENCE,
        )
        and _flag_role_match(
            policy,
            policy.requires_fx_quote_validation,
            SourceValidationRole.FX_QUOTE_REFERENCE,
        )
        and _flag_role_match(
            policy,
            policy.requires_crypto_exchange_cross_check,
            SourceValidationRole.CRYPTO_EXCHANGE_CROSS_CHECK_SOURCE,
        )
        and _flag_role_match(
            policy,
            policy.requires_liquidity_proxy_reference,
            SourceValidationRole.LIQUIDITY_PROXY_REFERENCE,
        )
    )


def _independent_cross_check_passed(policy: CrossSourceValidationPolicy) -> bool:
    return (
        policy.requires_independent_cross_source_check
        and _has_role(policy, SourceValidationRole.INDEPENDENT_CROSS_CHECK_SOURCE)
    )


def _calendar_validation_passed(policy: CrossSourceValidationPolicy) -> bool:
    return (
        policy.requires_calendar_validation
        and _has_role(policy, SourceValidationRole.MARKET_CALENDAR_REFERENCE)
    )


def _timestamp_alignment_passed(policy: CrossSourceValidationPolicy) -> bool:
    return (
        policy.requires_timestamp_alignment
        and _has_role(policy, SourceValidationRole.TIMESTAMP_ALIGNMENT_REFERENCE)
    )


def _price_consistency_passed(policy: CrossSourceValidationPolicy) -> bool:
    return (
        policy.requires_price_consistency_policy
        and _has_role(policy, SourceValidationRole.PRICE_CONSISTENCY_REFERENCE)
    )


def _volume_consistency_passed(policy: CrossSourceValidationPolicy) -> bool:
    if policy.asset == MarketAsset.EUR_USD:
        return (
            not policy.requires_volume_consistency_policy
            and not _has_role(policy, SourceValidationRole.VOLUME_CONSISTENCY_REFERENCE)
        )

    return (
        policy.requires_volume_consistency_policy
        and _has_role(policy, SourceValidationRole.VOLUME_CONSISTENCY_REFERENCE)
    )


def _asset_specific_references_passed(policy: CrossSourceValidationPolicy) -> bool:
    if policy.asset == MarketAsset.US_EQUITIES_ETFS:
        return _us_equities_etfs_references_passed(policy)

    if policy.asset in {MarketAsset.GOLD, MarketAsset.OIL}:
        return _futures_references_passed(policy)

    if policy.asset == MarketAsset.BITCOIN:
        return _bitcoin_references_passed(policy)

    if policy.asset == MarketAsset.EUR_USD:
        return _eur_usd_references_passed(policy)

    return False


def _us_equities_etfs_references_passed(policy: CrossSourceValidationPolicy) -> bool:
    return (
        _shared_source_controls_passed(policy)
        and policy.requires_corporate_action_reference
        and _has_role(policy, SourceValidationRole.CORPORATE_ACTIONS_REFERENCE)
        and policy.requires_volume_consistency_policy
        and not policy.requires_contract_specification_reference
        and not policy.requires_roll_policy_reference
        and not policy.requires_fx_quote_validation
        and not policy.requires_crypto_exchange_cross_check
        and not policy.requires_liquidity_proxy_reference
    )


def _futures_references_passed(policy: CrossSourceValidationPolicy) -> bool:
    return (
        _shared_source_controls_passed(policy)
        and policy.requires_volume_consistency_policy
        and policy.requires_contract_specification_reference
        and policy.requires_roll_policy_reference
        and _has_role(
            policy,
            SourceValidationRole.FUTURES_CONTRACT_SPECIFICATION_REFERENCE,
        )
        and _has_role(policy, SourceValidationRole.FUTURES_ROLL_POLICY_REFERENCE)
        and not policy.requires_corporate_action_reference
        and not policy.requires_fx_quote_validation
        and not policy.requires_crypto_exchange_cross_check
        and not policy.requires_liquidity_proxy_reference
    )


def _bitcoin_references_passed(policy: CrossSourceValidationPolicy) -> bool:
    return (
        _shared_source_controls_passed(policy)
        and policy.requires_volume_consistency_policy
        and policy.requires_crypto_exchange_cross_check
        and _has_role(policy, SourceValidationRole.CRYPTO_EXCHANGE_CROSS_CHECK_SOURCE)
        and not policy.requires_corporate_action_reference
        and not policy.requires_contract_specification_reference
        and not policy.requires_roll_policy_reference
        and not policy.requires_fx_quote_validation
        and not policy.requires_liquidity_proxy_reference
    )


def _eur_usd_references_passed(policy: CrossSourceValidationPolicy) -> bool:
    return (
        _shared_source_controls_passed(policy)
        and not policy.requires_volume_consistency_policy
        and not _has_role(policy, SourceValidationRole.VOLUME_CONSISTENCY_REFERENCE)
        and policy.requires_fx_quote_validation
        and policy.requires_liquidity_proxy_reference
        and _has_role(policy, SourceValidationRole.FX_QUOTE_REFERENCE)
        and _has_role(policy, SourceValidationRole.LIQUIDITY_PROXY_REFERENCE)
        and not policy.requires_corporate_action_reference
        and not policy.requires_contract_specification_reference
        and not policy.requires_roll_policy_reference
        and not policy.requires_crypto_exchange_cross_check
    )


def _shared_source_controls_passed(policy: CrossSourceValidationPolicy) -> bool:
    return (
        _independent_cross_check_passed(policy)
        and _calendar_validation_passed(policy)
        and _timestamp_alignment_passed(policy)
        and _price_consistency_passed(policy)
    )


def _non_approval_boundary_passed(policy: CrossSourceValidationPolicy) -> bool:
    return (
        policy.provider_selected is False
        and policy.provider_approved is False
        and policy.source_reliability_approved is False
        and policy.historical_reliability_verified is False
        and policy.production_approved is False
    )


def _planning_only_boundary_passed(policy: CrossSourceValidationPolicy) -> bool:
    return _non_approval_boundary_passed(policy)


def _flag_role_match(
    policy: CrossSourceValidationPolicy,
    flag: bool,
    role: SourceValidationRole,
) -> bool:
    return not flag or _has_role(policy, role)


def _has_role(
    policy: CrossSourceValidationPolicy,
    role: SourceValidationRole,
) -> bool:
    return role in policy.required_source_roles
