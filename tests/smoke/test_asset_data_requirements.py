from dataclasses import FrozenInstanceError
import inspect
from pathlib import Path

import pytest

from app.domain.asset_data_requirements import (
    AssetDataRequirements,
    build_default_asset_data_requirements,
    MarketAsset,
    MarketSessionModel,
    VolumeModel,
)


CONTRACT_PATH = Path("app/domain/asset_data_requirements.py")


def _valid_requirements(**overrides: object) -> AssetDataRequirements:
    values = {
        "asset": MarketAsset.US_EQUITIES_ETFS,
        "is_first_execution_market": True,
        "market_session_model": MarketSessionModel.EXCHANGE_SESSION,
        "volume_model": VolumeModel.ETF_REPORTED_VOLUME,
        "allows_etf_proxy_planning": False,
        "requires_adjusted_price_policy": True,
        "requires_corporate_action_policy": True,
        "requires_roll_logic": False,
        "requires_contract_selection_policy": False,
        "requires_twenty_four_seven_calendar": False,
        "requires_exchange_source_policy": False,
        "requires_cross_source_validation": True,
        "requires_liquidity_proxy": False,
        "requires_timezone_policy": True,
        "requires_session_policy": True,
        "requires_quote_timestamp_validation": False,
        "notes": "Strict metadata-only asset data requirements.",
    }
    values.update(overrides)
    return AssetDataRequirements(**values)


def test_valid_asset_data_requirements_contract_creation() -> None:
    requirements = _valid_requirements()

    assert requirements.asset is MarketAsset.US_EQUITIES_ETFS
    assert requirements.market_session_model is MarketSessionModel.EXCHANGE_SESSION
    assert requirements.volume_model is VolumeModel.ETF_REPORTED_VOLUME
    assert requirements.is_first_execution_market is True


def test_contract_is_immutable() -> None:
    requirements = _valid_requirements()

    with pytest.raises(FrozenInstanceError):
        requirements.notes = "changed"


def test_constructor_has_no_default_values() -> None:
    signature = inspect.signature(AssetDataRequirements)

    for parameter in signature.parameters.values():
        assert parameter.default is inspect.Parameter.empty


def test_constructor_requires_all_fields() -> None:
    with pytest.raises(TypeError):
        AssetDataRequirements()


def test_invalid_enum_values_raise_value_error() -> None:
    invalid_cases = [
        {"asset": "US_EQUITIES_ETFS"},
        {"market_session_model": "EXCHANGE_SESSION"},
        {"volume_model": "ETF_REPORTED_VOLUME"},
    ]

    for overrides in invalid_cases:
        with pytest.raises(ValueError):
            _valid_requirements(**overrides)


def test_invalid_bool_values_raise_value_error() -> None:
    bool_fields = [
        "is_first_execution_market",
        "allows_etf_proxy_planning",
        "requires_adjusted_price_policy",
        "requires_corporate_action_policy",
        "requires_roll_logic",
        "requires_contract_selection_policy",
        "requires_twenty_four_seven_calendar",
        "requires_exchange_source_policy",
        "requires_cross_source_validation",
        "requires_liquidity_proxy",
        "requires_timezone_policy",
        "requires_session_policy",
        "requires_quote_timestamp_validation",
    ]

    for field_name in bool_fields:
        with pytest.raises(ValueError, match=f"{field_name} must be bool"):
            _valid_requirements(**{field_name: "yes"})


def test_empty_or_non_string_notes_raise_value_error() -> None:
    with pytest.raises(ValueError, match="notes must not be empty"):
        _valid_requirements(notes=" ")

    with pytest.raises(ValueError, match="notes must be a string"):
        _valid_requirements(notes=123)


def test_default_requirements_include_every_planning_asset() -> None:
    requirements = build_default_asset_data_requirements()

    assert set(requirements) == set(MarketAsset)
    assert all(isinstance(item, AssetDataRequirements) for item in requirements.values())
    assert all(asset is item.asset for asset, item in requirements.items())


def test_us_equities_etfs_is_only_first_execution_market() -> None:
    requirements = build_default_asset_data_requirements()

    assert requirements[MarketAsset.US_EQUITIES_ETFS].is_first_execution_market is True
    for asset in [
        MarketAsset.GOLD,
        MarketAsset.OIL,
        MarketAsset.BITCOIN,
        MarketAsset.EUR_USD,
    ]:
        assert requirements[asset].is_first_execution_market is False


def test_us_equities_etfs_require_equity_style_policies_without_futures_or_fx_assumptions() -> None:
    requirements = build_default_asset_data_requirements()[MarketAsset.US_EQUITIES_ETFS]

    assert requirements.market_session_model is MarketSessionModel.EXCHANGE_SESSION
    assert requirements.volume_model is VolumeModel.ETF_REPORTED_VOLUME
    assert requirements.requires_adjusted_price_policy is True
    assert requirements.requires_corporate_action_policy is True
    assert requirements.requires_cross_source_validation is True
    assert requirements.requires_roll_logic is False
    assert requirements.requires_twenty_four_seven_calendar is False
    assert requirements.requires_liquidity_proxy is False


def test_gold_and_oil_require_futures_roll_and_contract_policy_for_futures_path() -> None:
    requirements = build_default_asset_data_requirements()

    for asset in [MarketAsset.GOLD, MarketAsset.OIL]:
        profile = requirements[asset]
        assert profile.market_session_model is MarketSessionModel.FUTURES_SESSION
        assert profile.volume_model is VolumeModel.FUTURES_CONTRACT_VOLUME
        assert profile.allows_etf_proxy_planning is True
        assert profile.requires_roll_logic is True
        assert profile.requires_contract_selection_policy is True
        assert profile.requires_session_policy is True
        assert profile.requires_timezone_policy is True


def test_bitcoin_requires_24_7_exchange_fragmentation_and_cross_source_controls() -> None:
    requirements = build_default_asset_data_requirements()[MarketAsset.BITCOIN]

    assert requirements.market_session_model is MarketSessionModel.TWENTY_FOUR_SEVEN
    assert requirements.volume_model is VolumeModel.FRAGMENTED_EXCHANGE_VOLUME
    assert requirements.requires_twenty_four_seven_calendar is True
    assert requirements.requires_exchange_source_policy is True
    assert requirements.requires_cross_source_validation is True
    assert requirements.requires_quote_timestamp_validation is True


def test_eur_usd_requires_fx_session_and_liquidity_proxy_policy() -> None:
    requirements = build_default_asset_data_requirements()[MarketAsset.EUR_USD]

    assert requirements.market_session_model is MarketSessionModel.FX_SESSION
    assert requirements.volume_model is VolumeModel.NO_CENTRALIZED_VOLUME
    assert requirements.requires_liquidity_proxy is True
    assert requirements.requires_session_policy is True
    assert requirements.requires_quote_timestamp_validation is True
    assert requirements.requires_roll_logic is False


def test_contract_exposes_no_provider_or_reliability_approval_flags() -> None:
    fields = set(AssetDataRequirements.__dataclass_fields__)

    forbidden_fields = {
        "provider",
        "provider_name",
        "provider_approved",
        "selected_provider",
        "source_reliability_approved",
        "historical_reliability",
        "verified_historical",
        "production_approved",
    }
    assert fields.isdisjoint(forbidden_fields)


def test_contract_does_not_produce_verified_historical_or_source_approval() -> None:
    source = CONTRACT_PATH.read_text(encoding="utf-8")

    assert "VERIFIED_HISTORICAL" not in source
    assert "source_reliability_approved" not in source
    assert "provider_approved" not in source
    assert "production_approved" not in source


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
