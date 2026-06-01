"""Market phase parameter contract definitions."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MarketPhaseParameters:
    """Required parameter contract for future market phase computation."""

    accumulation_high_threshold: float
    liquidity_inflow_high_threshold: float
    distribution_high_threshold: float
    liquidity_outflow_high_threshold: float
    trend_window: int
    markup_trend_threshold: float
    markdown_trend_threshold: float

    def __post_init__(self) -> None:
        self._validate_float("accumulation_high_threshold")
        self._validate_float("liquidity_inflow_high_threshold")
        self._validate_float("distribution_high_threshold")
        self._validate_float("liquidity_outflow_high_threshold")
        self._validate_int("trend_window")
        self._validate_float("markup_trend_threshold")
        self._validate_float("markdown_trend_threshold")
        self._validate_ranges()

    def _validate_float(self, field_name: str) -> None:
        if type(getattr(self, field_name)) is not float:
            raise ValueError(f"{field_name} must be a float")

    def _validate_int(self, field_name: str) -> None:
        if type(getattr(self, field_name)) is not int:
            raise ValueError(f"{field_name} must be an int")

    def _validate_ranges(self) -> None:
        self._validate_unit_range("accumulation_high_threshold")
        self._validate_unit_range("liquidity_inflow_high_threshold")
        self._validate_unit_range("distribution_high_threshold")
        self._validate_unit_range("liquidity_outflow_high_threshold")

        if self.trend_window <= 1:
            raise ValueError("trend_window must be > 1")

        if self.markup_trend_threshold <= 0:
            raise ValueError("markup_trend_threshold must be > 0")

        if self.markdown_trend_threshold >= 0:
            raise ValueError("markdown_trend_threshold must be < 0")

    def _validate_unit_range(self, field_name: str) -> None:
        value = getattr(self, field_name)
        if not 0 <= value <= 1:
            raise ValueError(f"{field_name} must be within [0,1]")
