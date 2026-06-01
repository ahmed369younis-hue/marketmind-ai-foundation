import pytest

from app.domain.market_phase_parameters import MarketPhaseParameters


def valid_market_phase_parameters(**overrides: object) -> dict[str, object]:
    parameters: dict[str, object] = {
        "accumulation_high_threshold": 0.7,
        "liquidity_inflow_high_threshold": 0.7,
        "distribution_high_threshold": 0.7,
        "liquidity_outflow_high_threshold": 0.7,
        "trend_window": 3,
        "markup_trend_threshold": 0.01,
        "markdown_trend_threshold": -0.01,
    }
    parameters.update(overrides)
    return parameters


def test_valid_market_phase_parameters_passes() -> None:
    parameters = MarketPhaseParameters(**valid_market_phase_parameters())

    assert parameters.trend_window == 3


@pytest.mark.parametrize(
    "value",
    [-0.1, 1.1],
    ids=["below-zero", "above-one"],
)
def test_accumulation_high_threshold_outside_unit_range_raises_value_error(value: float) -> None:
    with pytest.raises(ValueError, match="accumulation_high_threshold must be within \\[0,1\\]"):
        MarketPhaseParameters(**valid_market_phase_parameters(accumulation_high_threshold=value))


@pytest.mark.parametrize(
    "value",
    [-0.1, 1.1],
    ids=["below-zero", "above-one"],
)
def test_liquidity_inflow_high_threshold_outside_unit_range_raises_value_error(value: float) -> None:
    with pytest.raises(ValueError, match="liquidity_inflow_high_threshold must be within \\[0,1\\]"):
        MarketPhaseParameters(**valid_market_phase_parameters(liquidity_inflow_high_threshold=value))


@pytest.mark.parametrize(
    "value",
    [-0.1, 1.1],
    ids=["below-zero", "above-one"],
)
def test_distribution_high_threshold_outside_unit_range_raises_value_error(value: float) -> None:
    with pytest.raises(ValueError, match="distribution_high_threshold must be within \\[0,1\\]"):
        MarketPhaseParameters(**valid_market_phase_parameters(distribution_high_threshold=value))


@pytest.mark.parametrize(
    "value",
    [-0.1, 1.1],
    ids=["below-zero", "above-one"],
)
def test_liquidity_outflow_high_threshold_outside_unit_range_raises_value_error(value: float) -> None:
    with pytest.raises(ValueError, match="liquidity_outflow_high_threshold must be within \\[0,1\\]"):
        MarketPhaseParameters(**valid_market_phase_parameters(liquidity_outflow_high_threshold=value))


@pytest.mark.parametrize(
    "value",
    [1, 0],
    ids=["one", "zero"],
)
def test_trend_window_less_than_or_equal_to_one_raises_value_error(value: int) -> None:
    with pytest.raises(ValueError, match="trend_window must be > 1"):
        MarketPhaseParameters(**valid_market_phase_parameters(trend_window=value))


@pytest.mark.parametrize(
    "value",
    [0.0, -0.1],
    ids=["zero", "negative"],
)
def test_markup_trend_threshold_less_than_or_equal_to_zero_raises_value_error(value: float) -> None:
    with pytest.raises(ValueError, match="markup_trend_threshold must be > 0"):
        MarketPhaseParameters(**valid_market_phase_parameters(markup_trend_threshold=value))


@pytest.mark.parametrize(
    "value",
    [0.0, 0.1],
    ids=["zero", "positive"],
)
def test_markdown_trend_threshold_greater_than_or_equal_to_zero_raises_value_error(
    value: float,
) -> None:
    with pytest.raises(ValueError, match="markdown_trend_threshold must be < 0"):
        MarketPhaseParameters(**valid_market_phase_parameters(markdown_trend_threshold=value))


def test_market_phase_parameters_constructor_requires_explicit_values() -> None:
    with pytest.raises(TypeError):
        MarketPhaseParameters()
