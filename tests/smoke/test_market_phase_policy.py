import pytest

from app.domain.market_phase_policy import MarketPhasePriority, MarketPhaseResolutionPolicy


def test_market_phase_resolution_policy_signal_first_passes() -> None:
    policy = MarketPhaseResolutionPolicy(priority=MarketPhasePriority.SIGNAL_FIRST)

    assert policy.priority is MarketPhasePriority.SIGNAL_FIRST


def test_market_phase_resolution_policy_trend_first_passes() -> None:
    policy = MarketPhaseResolutionPolicy(priority=MarketPhasePriority.TREND_FIRST)

    assert policy.priority is MarketPhasePriority.TREND_FIRST


def test_market_phase_resolution_policy_invalid_priority_string_raises_value_error() -> None:
    with pytest.raises(ValueError, match="priority must be a valid MarketPhasePriority value"):
        MarketPhaseResolutionPolicy(priority="SIGNAL_FIRST")


def test_market_phase_resolution_policy_none_priority_raises_value_error() -> None:
    with pytest.raises(ValueError, match="priority must be a valid MarketPhasePriority value"):
        MarketPhaseResolutionPolicy(priority=None)


def test_market_phase_resolution_policy_constructor_requires_explicit_priority() -> None:
    with pytest.raises(TypeError):
        MarketPhaseResolutionPolicy()
