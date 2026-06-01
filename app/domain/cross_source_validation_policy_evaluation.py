"""Evaluation result contracts for cross-source validation policy planning."""

from dataclasses import dataclass
from enum import Enum

from app.domain.asset_data_requirements import MarketAsset


class CrossSourceValidationPolicyEvaluationCheck(Enum):
    """Allowed checks for metadata-only cross-source policy evaluation."""

    POLICY_SHAPE_CHECK = "POLICY_SHAPE_CHECK"
    REQUIRED_ROLES_CHECK = "REQUIRED_ROLES_CHECK"
    INDEPENDENT_CROSS_CHECK_REQUIRED_CHECK = (
        "INDEPENDENT_CROSS_CHECK_REQUIRED_CHECK"
    )
    CALENDAR_VALIDATION_CHECK = "CALENDAR_VALIDATION_CHECK"
    TIMESTAMP_ALIGNMENT_CHECK = "TIMESTAMP_ALIGNMENT_CHECK"
    PRICE_CONSISTENCY_POLICY_CHECK = "PRICE_CONSISTENCY_POLICY_CHECK"
    VOLUME_CONSISTENCY_POLICY_CHECK = "VOLUME_CONSISTENCY_POLICY_CHECK"
    ASSET_SPECIFIC_REFERENCE_CHECK = "ASSET_SPECIFIC_REFERENCE_CHECK"
    NON_APPROVAL_BOUNDARY_CHECK = "NON_APPROVAL_BOUNDARY_CHECK"
    PLANNING_ONLY_BOUNDARY_CHECK = "PLANNING_ONLY_BOUNDARY_CHECK"


@dataclass(frozen=True, slots=True)
class CrossSourceValidationPolicyEvaluationResult:
    """Strict metadata-only result for future source-planning readiness."""

    asset: MarketAsset
    check: CrossSourceValidationPolicyEvaluationCheck
    passed: bool
    details: str
    planning_ready_only: bool
    provider_selected: bool
    provider_approved: bool
    source_reliability_approved: bool
    historical_reliability_verified: bool
    production_approved: bool

    def __post_init__(self) -> None:
        self._validate_enum("asset", MarketAsset)
        self._validate_enum("check", CrossSourceValidationPolicyEvaluationCheck)
        self._validate_bool("passed")
        self._validate_non_empty_string("details")
        self._validate_bool("planning_ready_only")

        for field_name in (
            "provider_selected",
            "provider_approved",
            "source_reliability_approved",
            "historical_reliability_verified",
            "production_approved",
        ):
            self._validate_false_flag(field_name)

        if self.planning_ready_only and not self.passed:
            raise ValueError("planning_ready_only may be True only when passed is True")

    def _validate_enum(self, field_name: str, enum_type: type[Enum]) -> None:
        if not isinstance(getattr(self, field_name), enum_type):
            raise ValueError(f"{field_name} must be a valid {enum_type.__name__} value")

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
