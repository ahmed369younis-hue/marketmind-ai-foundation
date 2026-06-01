"""Evaluation result contracts for asset data requirements planning."""

from dataclasses import dataclass
from enum import Enum

from app.domain.asset_data_requirements import MarketAsset


class AssetDataRequirementsEvaluationCheck(Enum):
    """Allowed checks for metadata-only asset data requirements evaluation."""

    ASSET_PROFILE_CHECK = "ASSET_PROFILE_CHECK"
    SESSION_POLICY_CHECK = "SESSION_POLICY_CHECK"
    VOLUME_MODEL_CHECK = "VOLUME_MODEL_CHECK"
    CALENDAR_POLICY_CHECK = "CALENDAR_POLICY_CHECK"
    SOURCE_POLICY_CHECK = "SOURCE_POLICY_CHECK"
    CROSS_SOURCE_VALIDATION_CHECK = "CROSS_SOURCE_VALIDATION_CHECK"
    LIQUIDITY_PROXY_CHECK = "LIQUIDITY_PROXY_CHECK"
    FUTURES_ROLL_POLICY_CHECK = "FUTURES_ROLL_POLICY_CHECK"
    FIRST_MARKET_PRIORITY_CHECK = "FIRST_MARKET_PRIORITY_CHECK"
    NON_APPROVAL_BOUNDARY_CHECK = "NON_APPROVAL_BOUNDARY_CHECK"


@dataclass(frozen=True, slots=True)
class AssetDataRequirementsEvaluationResult:
    """Strict metadata-only result for future data-source planning readiness."""

    asset: MarketAsset
    check: AssetDataRequirementsEvaluationCheck
    passed: bool
    details: str
    planning_ready_only: bool
    source_approved: bool
    provider_approved: bool
    historical_reliability_verified: bool
    production_approved: bool

    def __post_init__(self) -> None:
        if not isinstance(self.asset, MarketAsset):
            raise ValueError("asset must be a valid MarketAsset value")

        if not isinstance(self.check, AssetDataRequirementsEvaluationCheck):
            raise ValueError(
                "check must be a valid AssetDataRequirementsEvaluationCheck value"
            )

        self._validate_bool("passed")
        self._validate_non_empty_string("details")
        self._validate_bool("planning_ready_only")
        self._validate_false_flag("source_approved")
        self._validate_false_flag("provider_approved")
        self._validate_false_flag("historical_reliability_verified")
        self._validate_false_flag("production_approved")

        if self.planning_ready_only and not self.passed:
            raise ValueError("planning_ready_only may be True only when passed is True")

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
