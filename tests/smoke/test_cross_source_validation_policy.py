from dataclasses import FrozenInstanceError
import inspect
from pathlib import Path
import re

import pytest

from app.domain.asset_data_requirements import MarketAsset
from app.domain.cross_source_validation_policy import (
    CrossSourceValidationPolicy,
    build_cross_source_validation_policies,
    build_cross_source_validation_policy,
    SourceValidationRole,
)


CONTRACT_PATH = Path("app/domain/cross_source_validation_policy.py")
ALL_ROLES = tuple(SourceValidationRole)
NON_APPROVAL_FIELDS = [
    "provider_selected",
    "provider_approved",
    "source_reliability_approved",
    "historical_reliability_verified",
    "production_approved",
]


def _valid_policy(**overrides: object) -> CrossSourceValidationPolicy:
    values = {
        "asset": MarketAsset.US_EQUITIES_ETFS,
        "required_source_roles": ALL_ROLES,
        "requires_independent_cross_source_check": True,
        "requires_calendar_validation": True,
        "requires_timestamp_alignment": True,
        "requires_price_consistency_policy": True,
        "requires_volume_consistency_policy": True,
        "requires_corporate_action_reference": True,
        "requires_contract_specification_reference": False,
        "requires_roll_policy_reference": False,
        "requires_fx_quote_validation": False,
        "requires_crypto_exchange_cross_check": False,
        "requires_liquidity_proxy_reference": False,
        "notes": "Strict metadata-only cross-source validation policy.",
        "provider_selected": False,
        "provider_approved": False,
        "source_reliability_approved": False,
        "historical_reliability_verified": False,
        "production_approved": False,
    }
    values.update(overrides)
    return CrossSourceValidationPolicy(**values)


def _roles(policy: CrossSourceValidationPolicy) -> set[SourceValidationRole]:
    return set(policy.required_source_roles)


def test_valid_cross_source_validation_policy_contract_creation() -> None:
    policy = _valid_policy()

    assert policy.asset is MarketAsset.US_EQUITIES_ETFS
    assert policy.requires_independent_cross_source_check is True
    assert SourceValidationRole.PRIMARY_MARKET_DATA_SOURCE in policy.required_source_roles


def test_role_lists_are_normalized_to_immutable_tuple() -> None:
    policy = _valid_policy(required_source_roles=list(ALL_ROLES))

    assert type(policy.required_source_roles) is tuple
    assert policy.required_source_roles == ALL_ROLES


def test_contract_is_immutable() -> None:
    policy = _valid_policy()

    with pytest.raises(FrozenInstanceError):
        policy.notes = "changed"


def test_constructor_has_no_default_values() -> None:
    signature = inspect.signature(CrossSourceValidationPolicy)

    for parameter in signature.parameters.values():
        assert parameter.default is inspect.Parameter.empty


def test_constructor_requires_all_fields() -> None:
    with pytest.raises(TypeError):
        CrossSourceValidationPolicy()


def test_invalid_asset_role_and_note_values_raise_value_error() -> None:
    invalid_cases = [
        {"asset": "US_EQUITIES_ETFS"},
        {"required_source_roles": ()},
        {"required_source_roles": ["PRIMARY_MARKET_DATA_SOURCE"]},
        {
            "required_source_roles": (
                SourceValidationRole.PRIMARY_MARKET_DATA_SOURCE,
                SourceValidationRole.PRIMARY_MARKET_DATA_SOURCE,
            )
        },
        {
            "required_source_roles": tuple(
                role
                for role in ALL_ROLES
                if role is not SourceValidationRole.PRIMARY_MARKET_DATA_SOURCE
            )
        },
        {"notes": " "},
        {"notes": object()},
    ]

    for overrides in invalid_cases:
        with pytest.raises(ValueError):
            _valid_policy(**overrides)


def test_invalid_bool_values_raise_value_error() -> None:
    bool_fields = [
        "requires_independent_cross_source_check",
        "requires_calendar_validation",
        "requires_timestamp_alignment",
        "requires_price_consistency_policy",
        "requires_volume_consistency_policy",
        "requires_corporate_action_reference",
        "requires_contract_specification_reference",
        "requires_roll_policy_reference",
        "requires_fx_quote_validation",
        "requires_crypto_exchange_cross_check",
        "requires_liquidity_proxy_reference",
        *NON_APPROVAL_FIELDS,
    ]

    for field_name in bool_fields:
        with pytest.raises(ValueError, match=f"{field_name} must be bool"):
            _valid_policy(**{field_name: "yes"})


def test_non_approval_flags_must_remain_false() -> None:
    for field_name in NON_APPROVAL_FIELDS:
        with pytest.raises(ValueError, match=f"{field_name} must be False"):
            _valid_policy(**{field_name: True})


def test_true_requirement_flags_must_have_matching_source_roles() -> None:
    required_role_by_field = {
        "requires_independent_cross_source_check": (
            SourceValidationRole.INDEPENDENT_CROSS_CHECK_SOURCE
        ),
        "requires_calendar_validation": SourceValidationRole.MARKET_CALENDAR_REFERENCE,
        "requires_timestamp_alignment": (
            SourceValidationRole.TIMESTAMP_ALIGNMENT_REFERENCE
        ),
        "requires_price_consistency_policy": (
            SourceValidationRole.PRICE_CONSISTENCY_REFERENCE
        ),
        "requires_volume_consistency_policy": (
            SourceValidationRole.VOLUME_CONSISTENCY_REFERENCE
        ),
        "requires_corporate_action_reference": (
            SourceValidationRole.CORPORATE_ACTIONS_REFERENCE
        ),
        "requires_contract_specification_reference": (
            SourceValidationRole.FUTURES_CONTRACT_SPECIFICATION_REFERENCE
        ),
        "requires_roll_policy_reference": (
            SourceValidationRole.FUTURES_ROLL_POLICY_REFERENCE
        ),
        "requires_fx_quote_validation": SourceValidationRole.FX_QUOTE_REFERENCE,
        "requires_crypto_exchange_cross_check": (
            SourceValidationRole.CRYPTO_EXCHANGE_CROSS_CHECK_SOURCE
        ),
        "requires_liquidity_proxy_reference": (
            SourceValidationRole.LIQUIDITY_PROXY_REFERENCE
        ),
    }

    for field_name, role in required_role_by_field.items():
        roles_without_required = tuple(item for item in ALL_ROLES if item is not role)

        with pytest.raises(ValueError, match=field_name):
            _valid_policy(
                required_source_roles=roles_without_required,
                **{field_name: True},
            )


def test_default_policies_include_every_planning_asset() -> None:
    policies = build_cross_source_validation_policies()

    assert set(policies) == set(MarketAsset)
    assert all(isinstance(item, CrossSourceValidationPolicy) for item in policies.values())
    assert all(asset is item.asset for asset, item in policies.items())
    for asset, policy in policies.items():
        assert build_cross_source_validation_policy(asset) == policy

    with pytest.raises(ValueError, match="asset must be"):
        build_cross_source_validation_policy("US_EQUITIES_ETFS")


def test_us_equities_etfs_require_equity_and_etf_cross_source_controls_only() -> None:
    policy = build_cross_source_validation_policies()[MarketAsset.US_EQUITIES_ETFS]

    assert policy.requires_independent_cross_source_check is True
    assert policy.requires_calendar_validation is True
    assert policy.requires_timestamp_alignment is True
    assert policy.requires_price_consistency_policy is True
    assert policy.requires_volume_consistency_policy is True
    assert policy.requires_corporate_action_reference is True
    assert policy.requires_contract_specification_reference is False
    assert policy.requires_roll_policy_reference is False
    assert policy.requires_fx_quote_validation is False
    assert policy.requires_crypto_exchange_cross_check is False
    assert policy.requires_liquidity_proxy_reference is False
    assert SourceValidationRole.CORPORATE_ACTIONS_REFERENCE in _roles(policy)
    assert SourceValidationRole.FX_QUOTE_REFERENCE not in _roles(policy)
    assert SourceValidationRole.CRYPTO_EXCHANGE_CROSS_CHECK_SOURCE not in _roles(policy)


def test_gold_and_oil_require_futures_contract_roll_price_volume_and_time_controls() -> None:
    policies = build_cross_source_validation_policies()

    for asset in [MarketAsset.GOLD, MarketAsset.OIL]:
        policy = policies[asset]
        assert policy.requires_independent_cross_source_check is True
        assert policy.requires_calendar_validation is True
        assert policy.requires_timestamp_alignment is True
        assert policy.requires_price_consistency_policy is True
        assert policy.requires_volume_consistency_policy is True
        assert policy.requires_contract_specification_reference is True
        assert policy.requires_roll_policy_reference is True
        assert policy.requires_corporate_action_reference is False
        assert policy.requires_fx_quote_validation is False
        assert policy.requires_crypto_exchange_cross_check is False
        assert policy.requires_liquidity_proxy_reference is False
        assert SourceValidationRole.FUTURES_CONTRACT_SPECIFICATION_REFERENCE in _roles(
            policy
        )
        assert SourceValidationRole.FUTURES_ROLL_POLICY_REFERENCE in _roles(policy)


def test_bitcoin_requires_crypto_exchange_cross_check_and_fragmented_volume_controls() -> None:
    policy = build_cross_source_validation_policies()[MarketAsset.BITCOIN]

    assert policy.requires_independent_cross_source_check is True
    assert policy.requires_calendar_validation is True
    assert policy.requires_timestamp_alignment is True
    assert policy.requires_price_consistency_policy is True
    assert policy.requires_volume_consistency_policy is True
    assert policy.requires_crypto_exchange_cross_check is True
    assert policy.requires_corporate_action_reference is False
    assert policy.requires_contract_specification_reference is False
    assert policy.requires_roll_policy_reference is False
    assert policy.requires_fx_quote_validation is False
    assert policy.requires_liquidity_proxy_reference is False
    assert SourceValidationRole.CRYPTO_EXCHANGE_CROSS_CHECK_SOURCE in _roles(policy)


def test_eur_usd_requires_fx_quote_timestamp_price_and_liquidity_proxy_controls() -> None:
    policy = build_cross_source_validation_policies()[MarketAsset.EUR_USD]

    assert policy.requires_independent_cross_source_check is True
    assert policy.requires_calendar_validation is True
    assert policy.requires_timestamp_alignment is True
    assert policy.requires_price_consistency_policy is True
    assert policy.requires_volume_consistency_policy is False
    assert policy.requires_fx_quote_validation is True
    assert policy.requires_liquidity_proxy_reference is True
    assert policy.requires_corporate_action_reference is False
    assert policy.requires_contract_specification_reference is False
    assert policy.requires_roll_policy_reference is False
    assert policy.requires_crypto_exchange_cross_check is False
    assert SourceValidationRole.FX_QUOTE_REFERENCE in _roles(policy)
    assert SourceValidationRole.LIQUIDITY_PROXY_REFERENCE in _roles(policy)
    assert SourceValidationRole.VOLUME_CONSISTENCY_REFERENCE not in _roles(policy)


def test_default_policies_never_select_or_approve_sources_or_production_use() -> None:
    for policy in build_cross_source_validation_policies().values():
        assert policy.provider_selected is False
        assert policy.provider_approved is False
        assert policy.source_reliability_approved is False
        assert policy.historical_reliability_verified is False
        assert policy.production_approved is False


def test_contract_file_has_no_forbidden_imports_or_runtime_surfaces() -> None:
    source = CONTRACT_PATH.read_text(encoding="utf-8")

    assert "app.engine" not in source
    assert "from app.engine" not in source
    assert "import app.engine" not in source
    assert "app.data" not in source
    assert "from app.data" not in source
    assert "import app.data" not in source

    for package_name in ["pandas", "numpy", "yfinance", "requests", "sqlalchemy"]:
        assert f"import {package_name}" not in source
        assert f"from {package_name}" not in source

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


def test_contract_file_has_no_provider_names_or_real_data_execution_terms() -> None:
    source = CONTRACT_PATH.read_text(encoding="utf-8")

    forbidden_terms = [
        "Tiingo",
        "Yahoo",
        "Polygon",
        "Alpha",
        "Binance",
        "MT5",
        "DailyMarketData",
        "DataQuality",
        "quality_gate",
        "ingestion",
        "persistence",
        "compute_",
        "buy",
        "sell",
        "VERIFIED_HISTORICAL",
    ]
    for term in forbidden_terms:
        assert term not in source


def test_contract_file_has_no_numeric_threshold_or_tolerance_values() -> None:
    source = CONTRACT_PATH.read_text(encoding="utf-8")

    assert re.search(r"\d", source) is None
    assert "threshold" not in source.lower()
    assert "tolerance" not in source.lower()
