"""Metadata-only cross-source validation policy contracts for asset planning."""

from dataclasses import dataclass
from enum import Enum

from app.domain.asset_data_requirements import MarketAsset


class SourceValidationRole(Enum):
    """Allowed source roles for future cross-source validation planning."""

    PRIMARY_MARKET_DATA_SOURCE = "PRIMARY_MARKET_DATA_SOURCE"
    INDEPENDENT_CROSS_CHECK_SOURCE = "INDEPENDENT_CROSS_CHECK_SOURCE"
    MARKET_CALENDAR_REFERENCE = "MARKET_CALENDAR_REFERENCE"
    TIMESTAMP_ALIGNMENT_REFERENCE = "TIMESTAMP_ALIGNMENT_REFERENCE"
    PRICE_CONSISTENCY_REFERENCE = "PRICE_CONSISTENCY_REFERENCE"
    VOLUME_CONSISTENCY_REFERENCE = "VOLUME_CONSISTENCY_REFERENCE"
    CORPORATE_ACTIONS_REFERENCE = "CORPORATE_ACTIONS_REFERENCE"
    FUTURES_CONTRACT_SPECIFICATION_REFERENCE = (
        "FUTURES_CONTRACT_SPECIFICATION_REFERENCE"
    )
    FUTURES_ROLL_POLICY_REFERENCE = "FUTURES_ROLL_POLICY_REFERENCE"
    FX_QUOTE_REFERENCE = "FX_QUOTE_REFERENCE"
    CRYPTO_EXCHANGE_CROSS_CHECK_SOURCE = "CRYPTO_EXCHANGE_CROSS_CHECK_SOURCE"
    LIQUIDITY_PROXY_REFERENCE = "LIQUIDITY_PROXY_REFERENCE"


@dataclass(frozen=True, slots=True)
class CrossSourceValidationPolicy:
    """Strict metadata-only source comparison policy for future planning."""

    asset: MarketAsset
    required_source_roles: tuple[SourceValidationRole, ...]
    requires_independent_cross_source_check: bool
    requires_calendar_validation: bool
    requires_timestamp_alignment: bool
    requires_price_consistency_policy: bool
    requires_volume_consistency_policy: bool
    requires_corporate_action_reference: bool
    requires_contract_specification_reference: bool
    requires_roll_policy_reference: bool
    requires_fx_quote_validation: bool
    requires_crypto_exchange_cross_check: bool
    requires_liquidity_proxy_reference: bool
    notes: str
    provider_selected: bool
    provider_approved: bool
    source_reliability_approved: bool
    historical_reliability_verified: bool
    production_approved: bool

    def __post_init__(self) -> None:
        self._validate_enum("asset", MarketAsset)
        self._validate_roles()

        for field_name in (
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
        ):
            self._validate_bool(field_name)

        self._validate_non_empty_string("notes")

        for field_name in (
            "provider_selected",
            "provider_approved",
            "source_reliability_approved",
            "historical_reliability_verified",
            "production_approved",
        ):
            self._validate_false_flag(field_name)

        self._validate_role_presence(
            "requires_independent_cross_source_check",
            SourceValidationRole.INDEPENDENT_CROSS_CHECK_SOURCE,
        )
        self._validate_role_presence(
            "requires_calendar_validation",
            SourceValidationRole.MARKET_CALENDAR_REFERENCE,
        )
        self._validate_role_presence(
            "requires_timestamp_alignment",
            SourceValidationRole.TIMESTAMP_ALIGNMENT_REFERENCE,
        )
        self._validate_role_presence(
            "requires_price_consistency_policy",
            SourceValidationRole.PRICE_CONSISTENCY_REFERENCE,
        )
        self._validate_role_presence(
            "requires_volume_consistency_policy",
            SourceValidationRole.VOLUME_CONSISTENCY_REFERENCE,
        )
        self._validate_role_presence(
            "requires_corporate_action_reference",
            SourceValidationRole.CORPORATE_ACTIONS_REFERENCE,
        )
        self._validate_role_presence(
            "requires_contract_specification_reference",
            SourceValidationRole.FUTURES_CONTRACT_SPECIFICATION_REFERENCE,
        )
        self._validate_role_presence(
            "requires_roll_policy_reference",
            SourceValidationRole.FUTURES_ROLL_POLICY_REFERENCE,
        )
        self._validate_role_presence(
            "requires_fx_quote_validation",
            SourceValidationRole.FX_QUOTE_REFERENCE,
        )
        self._validate_role_presence(
            "requires_crypto_exchange_cross_check",
            SourceValidationRole.CRYPTO_EXCHANGE_CROSS_CHECK_SOURCE,
        )
        self._validate_role_presence(
            "requires_liquidity_proxy_reference",
            SourceValidationRole.LIQUIDITY_PROXY_REFERENCE,
        )

    def _validate_enum(self, field_name: str, enum_type: type[Enum]) -> None:
        if not isinstance(getattr(self, field_name), enum_type):
            raise ValueError(f"{field_name} must be a valid {enum_type.__name__} value")

    def _validate_roles(self) -> None:
        value = self.required_source_roles

        if type(value) is list:
            roles = tuple(value)
            object.__setattr__(self, "required_source_roles", roles)
        elif type(value) is tuple:
            roles = value
        else:
            raise ValueError("required_source_roles must be a tuple or list")

        if not roles:
            raise ValueError("required_source_roles must not be empty")

        if any(not isinstance(role, SourceValidationRole) for role in roles):
            raise ValueError(
                "required_source_roles must contain SourceValidationRole values"
            )

        if len(set(roles)) != len(roles):
            raise ValueError("required_source_roles must not contain duplicate roles")

        if SourceValidationRole.PRIMARY_MARKET_DATA_SOURCE not in roles:
            raise ValueError("required_source_roles must include a primary source role")

    def _validate_bool(self, field_name: str) -> None:
        if type(getattr(self, field_name)) is not bool:
            raise ValueError(f"{field_name} must be bool")

    def _validate_false_flag(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not bool:
            raise ValueError(f"{field_name} must be bool")

        if value is not False:
            raise ValueError(f"{field_name} must be False")

    def _validate_non_empty_string(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if type(value) is not str:
            raise ValueError(f"{field_name} must be a string")

        if not value.strip():
            raise ValueError(f"{field_name} must not be empty")

    def _validate_role_presence(
        self,
        field_name: str,
        role: SourceValidationRole,
    ) -> None:
        if getattr(self, field_name) and role not in self.required_source_roles:
            raise ValueError(f"{field_name} requires {role.value}")


def build_cross_source_validation_policy(
    asset: MarketAsset,
) -> CrossSourceValidationPolicy:
    """Return one metadata-only cross-source policy for a supported asset."""

    if not isinstance(asset, MarketAsset):
        raise ValueError("asset must be a valid MarketAsset value")

    return build_cross_source_validation_policies()[asset]


def build_cross_source_validation_policies() -> dict[MarketAsset, CrossSourceValidationPolicy]:
    """Return deterministic metadata-only cross-source policies for planning assets."""

    return {
        MarketAsset.US_EQUITIES_ETFS: CrossSourceValidationPolicy(
            asset=MarketAsset.US_EQUITIES_ETFS,
            required_source_roles=(
                SourceValidationRole.PRIMARY_MARKET_DATA_SOURCE,
                SourceValidationRole.INDEPENDENT_CROSS_CHECK_SOURCE,
                SourceValidationRole.MARKET_CALENDAR_REFERENCE,
                SourceValidationRole.TIMESTAMP_ALIGNMENT_REFERENCE,
                SourceValidationRole.PRICE_CONSISTENCY_REFERENCE,
                SourceValidationRole.VOLUME_CONSISTENCY_REFERENCE,
                SourceValidationRole.CORPORATE_ACTIONS_REFERENCE,
            ),
            requires_independent_cross_source_check=True,
            requires_calendar_validation=True,
            requires_timestamp_alignment=True,
            requires_price_consistency_policy=True,
            requires_volume_consistency_policy=True,
            requires_corporate_action_reference=True,
            requires_contract_specification_reference=False,
            requires_roll_policy_reference=False,
            requires_fx_quote_validation=False,
            requires_crypto_exchange_cross_check=False,
            requires_liquidity_proxy_reference=False,
            notes="Equity and ETF planning requires independent source, calendar, timestamp, price, volume, and corporate action checks.",
            provider_selected=False,
            provider_approved=False,
            source_reliability_approved=False,
            historical_reliability_verified=False,
            production_approved=False,
        ),
        MarketAsset.GOLD: CrossSourceValidationPolicy(
            asset=MarketAsset.GOLD,
            required_source_roles=(
                SourceValidationRole.PRIMARY_MARKET_DATA_SOURCE,
                SourceValidationRole.INDEPENDENT_CROSS_CHECK_SOURCE,
                SourceValidationRole.MARKET_CALENDAR_REFERENCE,
                SourceValidationRole.TIMESTAMP_ALIGNMENT_REFERENCE,
                SourceValidationRole.PRICE_CONSISTENCY_REFERENCE,
                SourceValidationRole.VOLUME_CONSISTENCY_REFERENCE,
                SourceValidationRole.FUTURES_CONTRACT_SPECIFICATION_REFERENCE,
                SourceValidationRole.FUTURES_ROLL_POLICY_REFERENCE,
            ),
            requires_independent_cross_source_check=True,
            requires_calendar_validation=True,
            requires_timestamp_alignment=True,
            requires_price_consistency_policy=True,
            requires_volume_consistency_policy=True,
            requires_corporate_action_reference=False,
            requires_contract_specification_reference=True,
            requires_roll_policy_reference=True,
            requires_fx_quote_validation=False,
            requires_crypto_exchange_cross_check=False,
            requires_liquidity_proxy_reference=False,
            notes="Gold planning requires independent source, calendar, timestamp, price, volume, contract, and roll checks.",
            provider_selected=False,
            provider_approved=False,
            source_reliability_approved=False,
            historical_reliability_verified=False,
            production_approved=False,
        ),
        MarketAsset.OIL: CrossSourceValidationPolicy(
            asset=MarketAsset.OIL,
            required_source_roles=(
                SourceValidationRole.PRIMARY_MARKET_DATA_SOURCE,
                SourceValidationRole.INDEPENDENT_CROSS_CHECK_SOURCE,
                SourceValidationRole.MARKET_CALENDAR_REFERENCE,
                SourceValidationRole.TIMESTAMP_ALIGNMENT_REFERENCE,
                SourceValidationRole.PRICE_CONSISTENCY_REFERENCE,
                SourceValidationRole.VOLUME_CONSISTENCY_REFERENCE,
                SourceValidationRole.FUTURES_CONTRACT_SPECIFICATION_REFERENCE,
                SourceValidationRole.FUTURES_ROLL_POLICY_REFERENCE,
            ),
            requires_independent_cross_source_check=True,
            requires_calendar_validation=True,
            requires_timestamp_alignment=True,
            requires_price_consistency_policy=True,
            requires_volume_consistency_policy=True,
            requires_corporate_action_reference=False,
            requires_contract_specification_reference=True,
            requires_roll_policy_reference=True,
            requires_fx_quote_validation=False,
            requires_crypto_exchange_cross_check=False,
            requires_liquidity_proxy_reference=False,
            notes="Oil planning requires independent source, calendar, timestamp, price, volume, contract, and roll checks.",
            provider_selected=False,
            provider_approved=False,
            source_reliability_approved=False,
            historical_reliability_verified=False,
            production_approved=False,
        ),
        MarketAsset.BITCOIN: CrossSourceValidationPolicy(
            asset=MarketAsset.BITCOIN,
            required_source_roles=(
                SourceValidationRole.PRIMARY_MARKET_DATA_SOURCE,
                SourceValidationRole.INDEPENDENT_CROSS_CHECK_SOURCE,
                SourceValidationRole.MARKET_CALENDAR_REFERENCE,
                SourceValidationRole.TIMESTAMP_ALIGNMENT_REFERENCE,
                SourceValidationRole.PRICE_CONSISTENCY_REFERENCE,
                SourceValidationRole.VOLUME_CONSISTENCY_REFERENCE,
                SourceValidationRole.CRYPTO_EXCHANGE_CROSS_CHECK_SOURCE,
            ),
            requires_independent_cross_source_check=True,
            requires_calendar_validation=True,
            requires_timestamp_alignment=True,
            requires_price_consistency_policy=True,
            requires_volume_consistency_policy=True,
            requires_corporate_action_reference=False,
            requires_contract_specification_reference=False,
            requires_roll_policy_reference=False,
            requires_fx_quote_validation=False,
            requires_crypto_exchange_cross_check=True,
            requires_liquidity_proxy_reference=False,
            notes="Bitcoin planning requires independent source, calendar, timestamp, price, volume, and crypto exchange checks.",
            provider_selected=False,
            provider_approved=False,
            source_reliability_approved=False,
            historical_reliability_verified=False,
            production_approved=False,
        ),
        MarketAsset.EUR_USD: CrossSourceValidationPolicy(
            asset=MarketAsset.EUR_USD,
            required_source_roles=(
                SourceValidationRole.PRIMARY_MARKET_DATA_SOURCE,
                SourceValidationRole.INDEPENDENT_CROSS_CHECK_SOURCE,
                SourceValidationRole.MARKET_CALENDAR_REFERENCE,
                SourceValidationRole.TIMESTAMP_ALIGNMENT_REFERENCE,
                SourceValidationRole.PRICE_CONSISTENCY_REFERENCE,
                SourceValidationRole.FX_QUOTE_REFERENCE,
                SourceValidationRole.LIQUIDITY_PROXY_REFERENCE,
            ),
            requires_independent_cross_source_check=True,
            requires_calendar_validation=True,
            requires_timestamp_alignment=True,
            requires_price_consistency_policy=True,
            requires_volume_consistency_policy=False,
            requires_corporate_action_reference=False,
            requires_contract_specification_reference=False,
            requires_roll_policy_reference=False,
            requires_fx_quote_validation=True,
            requires_crypto_exchange_cross_check=False,
            requires_liquidity_proxy_reference=True,
            notes="EUR USD planning requires independent source, calendar, timestamp, price, FX quote, and liquidity proxy checks.",
            provider_selected=False,
            provider_approved=False,
            source_reliability_approved=False,
            historical_reliability_verified=False,
            production_approved=False,
        ),
    }
