from dataclasses import FrozenInstanceError, replace
import inspect
from pathlib import Path
import re

import pytest

from app.data.cross_source_validation_policy_evaluation import (
    evaluate_cross_source_validation_policy,
    is_cross_source_policy_ready_for_data_source_planning,
)
from app.domain.asset_data_requirements import MarketAsset
from app.domain.cross_source_validation_policy import (
    CrossSourceValidationPolicy,
    build_cross_source_validation_policies,
    SourceValidationRole,
)
from app.domain.cross_source_validation_policy_evaluation import (
    CrossSourceValidationPolicyEvaluationCheck,
    CrossSourceValidationPolicyEvaluationResult,
)


DOMAIN_FILE = Path("app/domain/cross_source_validation_policy_evaluation.py")
EVALUATOR_FILE = Path("app/data/cross_source_validation_policy_evaluation.py")
NEW_SOURCE_FILES = [DOMAIN_FILE, EVALUATOR_FILE]
EXPECTED_CHECK_ORDER = [
    CrossSourceValidationPolicyEvaluationCheck.POLICY_SHAPE_CHECK,
    CrossSourceValidationPolicyEvaluationCheck.REQUIRED_ROLES_CHECK,
    CrossSourceValidationPolicyEvaluationCheck.INDEPENDENT_CROSS_CHECK_REQUIRED_CHECK,
    CrossSourceValidationPolicyEvaluationCheck.CALENDAR_VALIDATION_CHECK,
    CrossSourceValidationPolicyEvaluationCheck.TIMESTAMP_ALIGNMENT_CHECK,
    CrossSourceValidationPolicyEvaluationCheck.PRICE_CONSISTENCY_POLICY_CHECK,
    CrossSourceValidationPolicyEvaluationCheck.VOLUME_CONSISTENCY_POLICY_CHECK,
    CrossSourceValidationPolicyEvaluationCheck.ASSET_SPECIFIC_REFERENCE_CHECK,
    CrossSourceValidationPolicyEvaluationCheck.NON_APPROVAL_BOUNDARY_CHECK,
    CrossSourceValidationPolicyEvaluationCheck.PLANNING_ONLY_BOUNDARY_CHECK,
]
NON_APPROVAL_FIELDS = [
    "provider_selected",
    "provider_approved",
    "source_reliability_approved",
    "historical_reliability_verified",
    "production_approved",
]


def _valid_result(**overrides: object) -> CrossSourceValidationPolicyEvaluationResult:
    values = {
        "asset": MarketAsset.US_EQUITIES_ETFS,
        "check": CrossSourceValidationPolicyEvaluationCheck.POLICY_SHAPE_CHECK,
        "passed": True,
        "details": "Metadata-only cross-source policy planning check.",
        "planning_ready_only": True,
        "provider_selected": False,
        "provider_approved": False,
        "source_reliability_approved": False,
        "historical_reliability_verified": False,
        "production_approved": False,
    }
    values.update(overrides)
    return CrossSourceValidationPolicyEvaluationResult(**values)


def _result_for(
    results: list[CrossSourceValidationPolicyEvaluationResult],
    check: CrossSourceValidationPolicyEvaluationCheck,
) -> CrossSourceValidationPolicyEvaluationResult:
    return next(result for result in results if result.check == check)


def _policy(asset: MarketAsset) -> CrossSourceValidationPolicy:
    return build_cross_source_validation_policies()[asset]


def _roles(policy: CrossSourceValidationPolicy) -> set[SourceValidationRole]:
    return set(policy.required_source_roles)


def test_evaluation_result_contract_valid_case() -> None:
    result = _valid_result()

    assert result.asset is MarketAsset.US_EQUITIES_ETFS
    assert result.check is CrossSourceValidationPolicyEvaluationCheck.POLICY_SHAPE_CHECK
    assert result.passed is True
    assert result.planning_ready_only is True
    assert result.provider_selected is False
    assert result.provider_approved is False
    assert result.source_reliability_approved is False
    assert result.historical_reliability_verified is False
    assert result.production_approved is False


def test_evaluation_result_contract_is_immutable() -> None:
    result = _valid_result()

    with pytest.raises(FrozenInstanceError):
        result.details = "changed"


def test_evaluation_result_constructor_has_no_defaults() -> None:
    signature = inspect.signature(CrossSourceValidationPolicyEvaluationResult)

    for parameter in signature.parameters.values():
        assert parameter.default is inspect.Parameter.empty


def test_evaluation_result_constructor_requires_all_fields() -> None:
    with pytest.raises(TypeError):
        CrossSourceValidationPolicyEvaluationResult()


def test_evaluation_result_rejects_invalid_types_and_empty_details() -> None:
    invalid_cases = [
        {"asset": "US_EQUITIES_ETFS"},
        {"check": "POLICY_SHAPE_CHECK"},
        {"passed": "yes"},
        {"details": " "},
        {"details": object()},
        {"planning_ready_only": "yes"},
        {"provider_selected": "no"},
        {"provider_approved": "no"},
        {"source_reliability_approved": "no"},
        {"historical_reliability_verified": "no"},
        {"production_approved": "no"},
    ]

    for overrides in invalid_cases:
        with pytest.raises(ValueError):
            _valid_result(**overrides)


def test_evaluation_result_requires_non_approval_flags_to_remain_false() -> None:
    for field_name in NON_APPROVAL_FIELDS:
        with pytest.raises(ValueError, match=f"{field_name} must be False"):
            _valid_result(**{field_name: True})


def test_planning_ready_only_cannot_be_true_when_check_fails() -> None:
    with pytest.raises(ValueError, match="planning_ready_only may be True"):
        _valid_result(passed=False, planning_ready_only=True)


def test_evaluator_returns_deterministic_ordered_checks() -> None:
    policy = _policy(MarketAsset.US_EQUITIES_ETFS)
    results = evaluate_cross_source_validation_policy(policy)

    assert [result.check for result in results] == EXPECTED_CHECK_ORDER
    assert [result.check for result in evaluate_cross_source_validation_policy(policy)] == (
        EXPECTED_CHECK_ORDER
    )


def test_evaluator_rejects_unknown_input_type() -> None:
    with pytest.raises(ValueError, match="policy must be"):
        evaluate_cross_source_validation_policy("not a policy")


def test_all_builtin_policy_profiles_evaluate_as_planning_ready_only() -> None:
    policies = build_cross_source_validation_policies()

    for asset, policy in policies.items():
        results = evaluate_cross_source_validation_policy(policy)
        assert {result.asset for result in results} == {asset}
        assert all(result.passed for result in results)
        assert all(result.planning_ready_only for result in results)
        assert is_cross_source_policy_ready_for_data_source_planning(policy) is True


def test_default_evaluation_results_never_select_or_approve_anything() -> None:
    for policy in build_cross_source_validation_policies().values():
        results = evaluate_cross_source_validation_policy(policy)
        assert all(result.provider_selected is False for result in results)
        assert all(result.provider_approved is False for result in results)
        assert all(result.source_reliability_approved is False for result in results)
        assert all(result.historical_reliability_verified is False for result in results)
        assert all(result.production_approved is False for result in results)


def test_readiness_is_false_when_any_required_check_fails() -> None:
    policy = replace(
        _policy(MarketAsset.US_EQUITIES_ETFS),
        requires_independent_cross_source_check=False,
    )
    results = evaluate_cross_source_validation_policy(policy)

    assert _result_for(
        results,
        CrossSourceValidationPolicyEvaluationCheck.INDEPENDENT_CROSS_CHECK_REQUIRED_CHECK,
    ).passed is False
    assert is_cross_source_policy_ready_for_data_source_planning(policy) is False


def test_us_equities_etfs_role_requirements_are_enforced() -> None:
    policy = _policy(MarketAsset.US_EQUITIES_ETFS)
    results = evaluate_cross_source_validation_policy(policy)

    assert _result_for(
        results,
        CrossSourceValidationPolicyEvaluationCheck.ASSET_SPECIFIC_REFERENCE_CHECK,
    ).passed is True
    assert SourceValidationRole.PRIMARY_MARKET_DATA_SOURCE in _roles(policy)
    assert SourceValidationRole.INDEPENDENT_CROSS_CHECK_SOURCE in _roles(policy)
    assert SourceValidationRole.MARKET_CALENDAR_REFERENCE in _roles(policy)
    assert SourceValidationRole.CORPORATE_ACTIONS_REFERENCE in _roles(policy)
    assert SourceValidationRole.TIMESTAMP_ALIGNMENT_REFERENCE in _roles(policy)
    assert SourceValidationRole.PRICE_CONSISTENCY_REFERENCE in _roles(policy)
    assert SourceValidationRole.VOLUME_CONSISTENCY_REFERENCE in _roles(policy)
    assert policy.requires_roll_policy_reference is False
    assert policy.requires_fx_quote_validation is False
    assert policy.requires_crypto_exchange_cross_check is False

    broken = replace(policy, requires_corporate_action_reference=False)
    assert _result_for(
        evaluate_cross_source_validation_policy(broken),
        CrossSourceValidationPolicyEvaluationCheck.ASSET_SPECIFIC_REFERENCE_CHECK,
    ).passed is False


def test_gold_and_oil_contract_specification_and_roll_requirements_are_enforced() -> None:
    for asset in [MarketAsset.GOLD, MarketAsset.OIL]:
        policy = _policy(asset)
        assert is_cross_source_policy_ready_for_data_source_planning(policy) is True
        assert SourceValidationRole.PRIMARY_MARKET_DATA_SOURCE in _roles(policy)
        assert SourceValidationRole.INDEPENDENT_CROSS_CHECK_SOURCE in _roles(policy)
        assert SourceValidationRole.MARKET_CALENDAR_REFERENCE in _roles(policy)
        assert SourceValidationRole.TIMESTAMP_ALIGNMENT_REFERENCE in _roles(policy)
        assert SourceValidationRole.PRICE_CONSISTENCY_REFERENCE in _roles(policy)
        assert SourceValidationRole.FUTURES_CONTRACT_SPECIFICATION_REFERENCE in _roles(
            policy
        )
        assert SourceValidationRole.FUTURES_ROLL_POLICY_REFERENCE in _roles(policy)

        broken = replace(policy, requires_roll_policy_reference=False)
        assert _result_for(
            evaluate_cross_source_validation_policy(broken),
            CrossSourceValidationPolicyEvaluationCheck.ASSET_SPECIFIC_REFERENCE_CHECK,
        ).passed is False


def test_bitcoin_exchange_cross_check_and_fragmented_volume_requirements_are_enforced() -> None:
    policy = _policy(MarketAsset.BITCOIN)
    assert is_cross_source_policy_ready_for_data_source_planning(policy) is True
    assert SourceValidationRole.PRIMARY_MARKET_DATA_SOURCE in _roles(policy)
    assert SourceValidationRole.INDEPENDENT_CROSS_CHECK_SOURCE in _roles(policy)
    assert SourceValidationRole.CRYPTO_EXCHANGE_CROSS_CHECK_SOURCE in _roles(policy)
    assert SourceValidationRole.TIMESTAMP_ALIGNMENT_REFERENCE in _roles(policy)
    assert SourceValidationRole.PRICE_CONSISTENCY_REFERENCE in _roles(policy)
    assert SourceValidationRole.VOLUME_CONSISTENCY_REFERENCE in _roles(policy)

    broken = replace(policy, requires_crypto_exchange_cross_check=False)
    assert _result_for(
        evaluate_cross_source_validation_policy(broken),
        CrossSourceValidationPolicyEvaluationCheck.ASSET_SPECIFIC_REFERENCE_CHECK,
    ).passed is False

    broken_volume = replace(policy, requires_volume_consistency_policy=False)
    assert _result_for(
        evaluate_cross_source_validation_policy(broken_volume),
        CrossSourceValidationPolicyEvaluationCheck.VOLUME_CONSISTENCY_POLICY_CHECK,
    ).passed is False


def test_eur_usd_fx_quote_and_liquidity_proxy_requirements_are_enforced() -> None:
    policy = _policy(MarketAsset.EUR_USD)
    assert is_cross_source_policy_ready_for_data_source_planning(policy) is True
    assert SourceValidationRole.PRIMARY_MARKET_DATA_SOURCE in _roles(policy)
    assert SourceValidationRole.INDEPENDENT_CROSS_CHECK_SOURCE in _roles(policy)
    assert SourceValidationRole.FX_QUOTE_REFERENCE in _roles(policy)
    assert SourceValidationRole.TIMESTAMP_ALIGNMENT_REFERENCE in _roles(policy)
    assert SourceValidationRole.PRICE_CONSISTENCY_REFERENCE in _roles(policy)
    assert SourceValidationRole.LIQUIDITY_PROXY_REFERENCE in _roles(policy)
    assert SourceValidationRole.VOLUME_CONSISTENCY_REFERENCE not in _roles(policy)
    assert policy.requires_volume_consistency_policy is False

    broken = replace(policy, requires_liquidity_proxy_reference=False)
    assert _result_for(
        evaluate_cross_source_validation_policy(broken),
        CrossSourceValidationPolicyEvaluationCheck.ASSET_SPECIFIC_REFERENCE_CHECK,
    ).passed is False

    broken_volume = replace(
        policy,
        required_source_roles=policy.required_source_roles
        + (SourceValidationRole.VOLUME_CONSISTENCY_REFERENCE,),
        requires_volume_consistency_policy=True,
    )
    assert _result_for(
        evaluate_cross_source_validation_policy(broken_volume),
        CrossSourceValidationPolicyEvaluationCheck.VOLUME_CONSISTENCY_POLICY_CHECK,
    ).passed is False


def test_new_files_have_no_numerical_threshold_or_tolerance_values() -> None:
    for path in NEW_SOURCE_FILES:
        source = path.read_text(encoding="utf-8")

        assert re.search(r"\d", source) is None
        assert "threshold" not in source.lower()
        assert "tolerance" not in source.lower()


def test_domain_contract_has_no_data_imports_or_runtime_surfaces() -> None:
    source = DOMAIN_FILE.read_text(encoding="utf-8")

    assert "app.data" not in source
    assert "from app.data" not in source
    assert "import app.data" not in source
    assert "app.engine" not in source
    assert "from app.engine" not in source
    assert "import app.engine" not in source

    for package_name in ["pandas", "numpy", "yfinance", "requests", "sqlalchemy", "dotenv"]:
        assert f"import {package_name}" not in source
        assert f"from {package_name}" not in source

    for term in ["open(", "pathlib", "Path(", "os.environ", "urllib", "socket"]:
        assert term not in source


def test_new_files_have_no_forbidden_imports_runtime_access_or_engine_surfaces() -> None:
    for path in NEW_SOURCE_FILES:
        source = path.read_text(encoding="utf-8")

        assert "app.engine" not in source
        assert "from app.engine" not in source
        assert "import app.engine" not in source
        for package_name in ["pandas", "numpy", "yfinance", "requests", "sqlalchemy", "dotenv"]:
            assert f"import {package_name}" not in source
            assert f"from {package_name}" not in source

        forbidden_runtime_terms = [
            "open(",
            ".write(",
            "Path(",
            "pathlib",
            "os.environ",
            "getenv",
            "load_dotenv",
            "urllib",
            "socket",
            "pickle",
            "shelve",
            "sqlite",
        ]
        for term in forbidden_runtime_terms:
            assert term not in source


def test_evaluator_does_not_execute_data_quality_gate_or_engine_logic() -> None:
    source = EVALUATOR_FILE.read_text(encoding="utf-8")

    assert "quality_gate" not in source
    assert "can_pass_data_quality_gate" not in source
    assert "DataQuality" not in source
    assert "compute_" not in source
    assert "DailyMarketData" not in source


def test_new_files_do_not_select_provider_or_claim_reliability_or_production() -> None:
    for path in NEW_SOURCE_FILES:
        source = path.read_text(encoding="utf-8")

        forbidden_terms = [
            "Tiingo",
            "Yahoo",
            "Polygon",
            "Alpha",
            "Binance",
            "MT5",
            "VERIFIED_HISTORICAL",
            "historically reliable",
            "production approved",
            "provider approved",
            "source approved",
            "buy",
            "sell",
            "trading output",
            "financial conclusion",
        ]
        for term in forbidden_terms:
            assert term not in source
