from dataclasses import FrozenInstanceError, replace
import inspect
from pathlib import Path

import pytest

from app.data.asset_data_requirements_evaluation import (
    evaluate_asset_data_requirements,
    is_asset_ready_for_data_source_planning,
)
from app.domain.asset_data_requirements import (
    AssetDataRequirements,
    build_default_asset_data_requirements,
    MarketAsset,
    MarketSessionModel,
    VolumeModel,
)
from app.domain.asset_data_requirements_evaluation import (
    AssetDataRequirementsEvaluationCheck,
    AssetDataRequirementsEvaluationResult,
)


DOMAIN_FILE = Path("app/domain/asset_data_requirements_evaluation.py")
EVALUATOR_FILE = Path("app/data/asset_data_requirements_evaluation.py")

EXPECTED_CHECK_ORDER = [
    AssetDataRequirementsEvaluationCheck.ASSET_PROFILE_CHECK,
    AssetDataRequirementsEvaluationCheck.SESSION_POLICY_CHECK,
    AssetDataRequirementsEvaluationCheck.VOLUME_MODEL_CHECK,
    AssetDataRequirementsEvaluationCheck.CALENDAR_POLICY_CHECK,
    AssetDataRequirementsEvaluationCheck.SOURCE_POLICY_CHECK,
    AssetDataRequirementsEvaluationCheck.CROSS_SOURCE_VALIDATION_CHECK,
    AssetDataRequirementsEvaluationCheck.LIQUIDITY_PROXY_CHECK,
    AssetDataRequirementsEvaluationCheck.FUTURES_ROLL_POLICY_CHECK,
    AssetDataRequirementsEvaluationCheck.FIRST_MARKET_PRIORITY_CHECK,
    AssetDataRequirementsEvaluationCheck.NON_APPROVAL_BOUNDARY_CHECK,
]


def _valid_result(**overrides: object) -> AssetDataRequirementsEvaluationResult:
    values = {
        "asset": MarketAsset.US_EQUITIES_ETFS,
        "check": AssetDataRequirementsEvaluationCheck.ASSET_PROFILE_CHECK,
        "passed": True,
        "details": "Metadata-only planning readiness check.",
        "planning_ready_only": True,
        "source_approved": False,
        "provider_approved": False,
        "historical_reliability_verified": False,
        "production_approved": False,
    }
    values.update(overrides)
    return AssetDataRequirementsEvaluationResult(**values)


def test_evaluation_result_contract_valid_case() -> None:
    result = _valid_result()

    assert result.asset is MarketAsset.US_EQUITIES_ETFS
    assert result.check is AssetDataRequirementsEvaluationCheck.ASSET_PROFILE_CHECK
    assert result.passed is True
    assert result.planning_ready_only is True
    assert result.source_approved is False
    assert result.provider_approved is False
    assert result.historical_reliability_verified is False
    assert result.production_approved is False


def test_evaluation_result_contract_is_immutable() -> None:
    result = _valid_result()

    with pytest.raises(FrozenInstanceError):
        result.details = "changed"


def test_evaluation_result_constructor_has_no_defaults() -> None:
    signature = inspect.signature(AssetDataRequirementsEvaluationResult)

    for parameter in signature.parameters.values():
        assert parameter.default is inspect.Parameter.empty


def test_evaluation_result_constructor_requires_all_fields() -> None:
    with pytest.raises(TypeError):
        AssetDataRequirementsEvaluationResult()


def test_evaluation_result_rejects_invalid_types_and_empty_details() -> None:
    invalid_cases = [
        {"asset": "US_EQUITIES_ETFS"},
        {"check": "ASSET_PROFILE_CHECK"},
        {"passed": "yes"},
        {"details": " "},
        {"planning_ready_only": "yes"},
        {"source_approved": "no"},
        {"provider_approved": "no"},
        {"historical_reliability_verified": "no"},
        {"production_approved": "no"},
    ]

    for overrides in invalid_cases:
        with pytest.raises(ValueError):
            _valid_result(**overrides)


def test_evaluation_result_requires_non_approval_flags_to_remain_false() -> None:
    for flag_name in [
        "source_approved",
        "provider_approved",
        "historical_reliability_verified",
        "production_approved",
    ]:
        with pytest.raises(ValueError, match=f"{flag_name} must be False"):
            _valid_result(**{flag_name: True})


def test_planning_ready_only_cannot_be_true_when_check_fails() -> None:
    with pytest.raises(ValueError, match="planning_ready_only may be True"):
        _valid_result(passed=False, planning_ready_only=True)


def test_evaluator_returns_deterministic_ordered_checks() -> None:
    requirements = build_default_asset_data_requirements()[MarketAsset.US_EQUITIES_ETFS]
    results = evaluate_asset_data_requirements(requirements)

    assert [result.check for result in results] == EXPECTED_CHECK_ORDER
    assert [result.check for result in evaluate_asset_data_requirements(requirements)] == EXPECTED_CHECK_ORDER


def test_all_default_asset_profiles_evaluate_as_planning_ready_only() -> None:
    requirements_by_asset = build_default_asset_data_requirements()

    for asset, requirements in requirements_by_asset.items():
        results = evaluate_asset_data_requirements(requirements)
        assert {result.asset for result in results} == {asset}
        assert all(result.passed for result in results)
        assert all(result.planning_ready_only for result in results)
        assert is_asset_ready_for_data_source_planning(requirements) is True


def test_non_approval_flags_are_always_false_for_default_profiles() -> None:
    for requirements in build_default_asset_data_requirements().values():
        results = evaluate_asset_data_requirements(requirements)
        assert all(result.source_approved is False for result in results)
        assert all(result.provider_approved is False for result in results)
        assert all(result.historical_reliability_verified is False for result in results)
        assert all(result.production_approved is False for result in results)


def test_us_equities_etfs_is_only_first_execution_market() -> None:
    requirements_by_asset = build_default_asset_data_requirements()

    assert requirements_by_asset[MarketAsset.US_EQUITIES_ETFS].is_first_execution_market is True
    assert (
        requirements_by_asset[MarketAsset.US_EQUITIES_ETFS].requires_cross_source_validation
        is True
    )
    assert is_asset_ready_for_data_source_planning(
        requirements_by_asset[MarketAsset.US_EQUITIES_ETFS]
    ) is True

    broken = replace(
        requirements_by_asset[MarketAsset.US_EQUITIES_ETFS],
        requires_cross_source_validation=False,
    )
    cross_source_result = _result_for(
        evaluate_asset_data_requirements(broken),
        AssetDataRequirementsEvaluationCheck.CROSS_SOURCE_VALIDATION_CHECK,
    )
    assert cross_source_result.passed is False
    assert is_asset_ready_for_data_source_planning(broken) is False

    for asset in [
        MarketAsset.GOLD,
        MarketAsset.OIL,
        MarketAsset.BITCOIN,
        MarketAsset.EUR_USD,
    ]:
        assert requirements_by_asset[asset].is_first_execution_market is False


def test_gold_and_oil_require_futures_roll_and_contract_policy() -> None:
    requirements_by_asset = build_default_asset_data_requirements()

    for asset in [MarketAsset.GOLD, MarketAsset.OIL]:
        requirements = requirements_by_asset[asset]
        assert requirements.market_session_model is MarketSessionModel.FUTURES_SESSION
        assert requirements.volume_model is VolumeModel.FUTURES_CONTRACT_VOLUME
        assert requirements.requires_roll_logic is True
        assert requirements.requires_contract_selection_policy is True

        broken = replace(requirements, requires_roll_logic=False)
        results = evaluate_asset_data_requirements(broken)
        roll_result = _result_for(
            results,
            AssetDataRequirementsEvaluationCheck.FUTURES_ROLL_POLICY_CHECK,
        )
        assert roll_result.passed is False
        assert is_asset_ready_for_data_source_planning(broken) is False


def test_bitcoin_requires_24_7_exchange_fragmentation_and_cross_source_validation() -> None:
    requirements = build_default_asset_data_requirements()[MarketAsset.BITCOIN]

    assert requirements.market_session_model is MarketSessionModel.TWENTY_FOUR_SEVEN
    assert requirements.volume_model is VolumeModel.FRAGMENTED_EXCHANGE_VOLUME
    assert requirements.requires_twenty_four_seven_calendar is True
    assert requirements.requires_exchange_source_policy is True
    assert requirements.requires_cross_source_validation is True

    broken = replace(requirements, requires_exchange_source_policy=False)
    source_result = _result_for(
        evaluate_asset_data_requirements(broken),
        AssetDataRequirementsEvaluationCheck.SOURCE_POLICY_CHECK,
    )
    assert source_result.passed is False


def test_eur_usd_requires_fx_session_and_liquidity_proxy_or_non_centralized_volume() -> None:
    requirements = build_default_asset_data_requirements()[MarketAsset.EUR_USD]

    assert requirements.market_session_model is MarketSessionModel.FX_SESSION
    assert requirements.volume_model is VolumeModel.NO_CENTRALIZED_VOLUME
    assert requirements.requires_liquidity_proxy is True
    assert requirements.requires_quote_timestamp_validation is True

    broken = replace(requirements, requires_liquidity_proxy=False)
    liquidity_result = _result_for(
        evaluate_asset_data_requirements(broken),
        AssetDataRequirementsEvaluationCheck.LIQUIDITY_PROXY_CHECK,
    )
    assert liquidity_result.passed is False


def test_evaluator_rejects_unknown_input_type() -> None:
    with pytest.raises(ValueError, match="requirements must be"):
        evaluate_asset_data_requirements("not requirements")


def test_evaluator_does_not_execute_data_quality_gate() -> None:
    source = EVALUATOR_FILE.read_text(encoding="utf-8")

    assert "quality_gate" not in source
    assert "can_pass_data_quality_gate" not in source
    assert "DataQuality" not in source


def test_new_files_have_no_engine_imports_or_forbidden_dependencies() -> None:
    for path in [DOMAIN_FILE, EVALUATOR_FILE]:
        source = path.read_text(encoding="utf-8")

        assert "app.engine" not in source
        assert "from app.engine" not in source
        assert "import app.engine" not in source
        for package_name in ["pandas", "numpy", "yfinance", "requests", "sqlalchemy"]:
            assert f"import {package_name}" not in source
            assert f"from {package_name}" not in source


def test_new_files_do_not_access_network_files_or_environment() -> None:
    for path in [DOMAIN_FILE, EVALUATOR_FILE]:
        source = path.read_text(encoding="utf-8")
        forbidden_runtime_terms = [
            "open(",
            ".write(",
            "Path(",
            "urlopen",
            "socket",
            "os.environ",
            "getenv",
            "load_dotenv",
            "pickle",
            "shelve",
            "sqlite",
        ]

        for term in forbidden_runtime_terms:
            assert term not in source


def _result_for(
    results: list[AssetDataRequirementsEvaluationResult],
    check: AssetDataRequirementsEvaluationCheck,
) -> AssetDataRequirementsEvaluationResult:
    return next(result for result in results if result.check == check)
