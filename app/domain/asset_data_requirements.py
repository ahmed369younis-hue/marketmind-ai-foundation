"""Asset-specific data requirement contracts for future multi-asset planning."""

from dataclasses import dataclass
from enum import Enum


class MarketAsset(Enum):
    """Supported market assets for future data requirement planning."""

    US_EQUITIES_ETFS = "US_EQUITIES_ETFS"
    GOLD = "GOLD"
    OIL = "OIL"
    BITCOIN = "BITCOIN"
    EUR_USD = "EUR_USD"


class MarketSessionModel(Enum):
    """Allowed market session models for future data requirements."""

    EXCHANGE_SESSION = "EXCHANGE_SESSION"
    FUTURES_SESSION = "FUTURES_SESSION"
    TWENTY_FOUR_SEVEN = "TWENTY_FOUR_SEVEN"
    FX_SESSION = "FX_SESSION"


class VolumeModel(Enum):
    """Allowed volume models for future data requirements."""

    CENTRALIZED_EXCHANGE_VOLUME = "CENTRALIZED_EXCHANGE_VOLUME"
    ETF_REPORTED_VOLUME = "ETF_REPORTED_VOLUME"
    FUTURES_CONTRACT_VOLUME = "FUTURES_CONTRACT_VOLUME"
    FRAGMENTED_EXCHANGE_VOLUME = "FRAGMENTED_EXCHANGE_VOLUME"
    NO_CENTRALIZED_VOLUME = "NO_CENTRALIZED_VOLUME"


@dataclass(frozen=True, slots=True)
class AssetDataRequirements:
    """Strict metadata-only requirements for future asset-specific data planning."""

    asset: MarketAsset
    is_first_execution_market: bool
    market_session_model: MarketSessionModel
    volume_model: VolumeModel
    allows_etf_proxy_planning: bool
    requires_adjusted_price_policy: bool
    requires_corporate_action_policy: bool
    requires_roll_logic: bool
    requires_contract_selection_policy: bool
    requires_twenty_four_seven_calendar: bool
    requires_exchange_source_policy: bool
    requires_cross_source_validation: bool
    requires_liquidity_proxy: bool
    requires_timezone_policy: bool
    requires_session_policy: bool
    requires_quote_timestamp_validation: bool
    notes: str

    def __post_init__(self) -> None:
        self._validate_enum("asset", MarketAsset)
        self._validate_bool("is_first_execution_market")
        self._validate_enum("market_session_model", MarketSessionModel)
        self._validate_enum("volume_model", VolumeModel)

        for field_name in (
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
        ):
            self._validate_bool(field_name)

        self._validate_non_empty_string("notes")

    def _validate_enum(self, field_name: str, enum_type: type[Enum]) -> None:
        if not isinstance(getattr(self, field_name), enum_type):
            raise ValueError(f"{field_name} must be a valid {enum_type.__name__} value")

    def _validate_bool(self, field_name: str) -> None:
        if type(getattr(self, field_name)) is not bool:
            raise ValueError(f"{field_name} must be bool")

    def _validate_non_empty_string(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not str:
            raise ValueError(f"{field_name} must be a string")

        if not value.strip():
            raise ValueError(f"{field_name} must not be empty")


def build_default_asset_data_requirements() -> dict[MarketAsset, AssetDataRequirements]:
    """Return deterministic metadata-only requirements for approved planning assets."""

    requirements = {
        MarketAsset.US_EQUITIES_ETFS: AssetDataRequirements(
            asset=MarketAsset.US_EQUITIES_ETFS,
            is_first_execution_market=True,
            market_session_model=MarketSessionModel.EXCHANGE_SESSION,
            volume_model=VolumeModel.ETF_REPORTED_VOLUME,
            allows_etf_proxy_planning=False,
            requires_adjusted_price_policy=True,
            requires_corporate_action_policy=True,
            requires_roll_logic=False,
            requires_contract_selection_policy=False,
            requires_twenty_four_seven_calendar=False,
            requires_exchange_source_policy=False,
            requires_cross_source_validation=True,
            requires_liquidity_proxy=False,
            requires_timezone_policy=True,
            requires_session_policy=True,
            requires_quote_timestamp_validation=False,
            notes="First execution market for local CSV, data quality governance, and cross-source planning.",
        ),
        MarketAsset.GOLD: AssetDataRequirements(
            asset=MarketAsset.GOLD,
            is_first_execution_market=False,
            market_session_model=MarketSessionModel.FUTURES_SESSION,
            volume_model=VolumeModel.FUTURES_CONTRACT_VOLUME,
            allows_etf_proxy_planning=True,
            requires_adjusted_price_policy=False,
            requires_corporate_action_policy=False,
            requires_roll_logic=True,
            requires_contract_selection_policy=True,
            requires_twenty_four_seven_calendar=False,
            requires_exchange_source_policy=False,
            requires_cross_source_validation=True,
            requires_liquidity_proxy=False,
            requires_timezone_policy=True,
            requires_session_policy=True,
            requires_quote_timestamp_validation=True,
            notes="Future market; ETF-style proxy planning may precede direct spot or futures complexity.",
        ),
        MarketAsset.OIL: AssetDataRequirements(
            asset=MarketAsset.OIL,
            is_first_execution_market=False,
            market_session_model=MarketSessionModel.FUTURES_SESSION,
            volume_model=VolumeModel.FUTURES_CONTRACT_VOLUME,
            allows_etf_proxy_planning=True,
            requires_adjusted_price_policy=False,
            requires_corporate_action_policy=False,
            requires_roll_logic=True,
            requires_contract_selection_policy=True,
            requires_twenty_four_seven_calendar=False,
            requires_exchange_source_policy=False,
            requires_cross_source_validation=True,
            requires_liquidity_proxy=False,
            requires_timezone_policy=True,
            requires_session_policy=True,
            requires_quote_timestamp_validation=True,
            notes="Future market; ETF or energy proxy planning may precede futures complexity.",
        ),
        MarketAsset.BITCOIN: AssetDataRequirements(
            asset=MarketAsset.BITCOIN,
            is_first_execution_market=False,
            market_session_model=MarketSessionModel.TWENTY_FOUR_SEVEN,
            volume_model=VolumeModel.FRAGMENTED_EXCHANGE_VOLUME,
            allows_etf_proxy_planning=False,
            requires_adjusted_price_policy=False,
            requires_corporate_action_policy=False,
            requires_roll_logic=False,
            requires_contract_selection_policy=False,
            requires_twenty_four_seven_calendar=True,
            requires_exchange_source_policy=True,
            requires_cross_source_validation=True,
            requires_liquidity_proxy=False,
            requires_timezone_policy=True,
            requires_session_policy=True,
            requires_quote_timestamp_validation=True,
            notes="Future market requiring exchange-source policy and fragmented-volume handling.",
        ),
        MarketAsset.EUR_USD: AssetDataRequirements(
            asset=MarketAsset.EUR_USD,
            is_first_execution_market=False,
            market_session_model=MarketSessionModel.FX_SESSION,
            volume_model=VolumeModel.NO_CENTRALIZED_VOLUME,
            allows_etf_proxy_planning=False,
            requires_adjusted_price_policy=False,
            requires_corporate_action_policy=False,
            requires_roll_logic=False,
            requires_contract_selection_policy=False,
            requires_twenty_four_seven_calendar=False,
            requires_exchange_source_policy=False,
            requires_cross_source_validation=True,
            requires_liquidity_proxy=True,
            requires_timezone_policy=True,
            requires_session_policy=True,
            requires_quote_timestamp_validation=True,
            notes="Future market requiring FX session and non-centralized-volume policy.",
        ),
    }

    return requirements
