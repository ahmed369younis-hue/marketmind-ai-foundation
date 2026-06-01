from datetime import date, timedelta

import pytest

from app.domain.confidence_contract import DailyConfidence
from app.domain.confidence_parameters import ConfidenceParameters
from app.domain.signal_contract import DailySignals
from app.engine.confidence import compute_daily_confidence


def _daily_signals(
    day_offset: int,
    symbol: str = "MM",
    accumulation_strength: float = 0.0,
    distribution_strength: float = 0.0,
    liquidity_inflow: float = 0.0,
    liquidity_outflow: float = 0.0,
    absorption_score: float = 0.0,
    fake_move_score: float = 0.0,
) -> DailySignals:
    return DailySignals(
        date=date(2024, 1, 1) + timedelta(days=day_offset),
        symbol=symbol,
        accumulation_strength=accumulation_strength,
        distribution_strength=distribution_strength,
        liquidity_inflow=liquidity_inflow,
        liquidity_outflow=liquidity_outflow,
        absorption_score=absorption_score,
        fake_move_score=fake_move_score,
    )


def _confidence_parameters(**overrides: object) -> ConfidenceParameters:
    values: dict[str, object] = {
        "consistency_window": 3,
        "signal_active_threshold": 0.5,
    }
    values.update(overrides)
    return ConfidenceParameters(**values)


def test_daily_confidence_empty_signals_returns_empty_list() -> None:
    assert compute_daily_confidence([], _confidence_parameters()) == []


def test_daily_confidence_insufficient_history_returns_empty_list() -> None:
    signals = [_daily_signals(0), _daily_signals(1)]

    result = compute_daily_confidence(signals, _confidence_parameters())

    assert result == []


def test_daily_confidence_valid_signals_return_daily_confidence_objects_after_enough_history() -> None:
    signals = [
        _daily_signals(0, accumulation_strength=0.8),
        _daily_signals(1, accumulation_strength=0.8),
    ]

    result = compute_daily_confidence(
        signals,
        _confidence_parameters(consistency_window=2),
    )

    assert len(result) == 1
    assert isinstance(result[0], DailyConfidence)


def test_daily_confidence_output_preserves_date_and_symbol() -> None:
    signals = [
        _daily_signals(0, symbol="MMAI", accumulation_strength=0.8),
        _daily_signals(1, symbol="MMAI", accumulation_strength=0.8),
    ]

    result = compute_daily_confidence(
        signals,
        _confidence_parameters(consistency_window=2),
    )

    assert result[0].date == signals[1].date
    assert result[0].symbol == signals[1].symbol


def test_daily_confidence_constructive_consistency_and_agreement_case() -> None:
    signals = [
        _daily_signals(0, accumulation_strength=0.8, liquidity_inflow=0.8),
        _daily_signals(1, accumulation_strength=0.8, absorption_score=0.8),
        _daily_signals(
            2,
            accumulation_strength=0.8,
            liquidity_inflow=0.8,
            absorption_score=0.8,
        ),
    ]

    result = compute_daily_confidence(signals, _confidence_parameters())

    assert result[0].confidence == 1.0


def test_daily_confidence_opposing_consistency_and_agreement_case() -> None:
    signals = [
        _daily_signals(0, accumulation_strength=0.8, liquidity_inflow=0.8),
        _daily_signals(1, distribution_strength=0.8, liquidity_outflow=0.8),
        _daily_signals(
            2,
            accumulation_strength=0.8,
            distribution_strength=0.8,
            liquidity_outflow=0.8,
        ),
    ]

    result = compute_daily_confidence(signals, _confidence_parameters())

    assert result[0].confidence == pytest.approx(4 / 9)


def test_daily_confidence_tie_only_window_produces_zero_confidence() -> None:
    signals = [
        _daily_signals(0, accumulation_strength=0.8, distribution_strength=0.8),
        _daily_signals(1, liquidity_inflow=0.8, liquidity_outflow=0.8),
    ]

    result = compute_daily_confidence(
        signals,
        _confidence_parameters(consistency_window=2),
    )

    assert result[0].confidence == 0.0


def test_daily_confidence_zero_active_signals_produce_zero_confidence() -> None:
    signals = [
        _daily_signals(0, accumulation_strength=0.8),
        _daily_signals(1),
    ]

    result = compute_daily_confidence(
        signals,
        _confidence_parameters(consistency_window=2),
    )

    assert result[0].confidence == 0.0


def test_daily_confidence_values_are_always_within_unit_range() -> None:
    signals = [
        _daily_signals(0, accumulation_strength=0.8),
        _daily_signals(1, distribution_strength=0.8),
        _daily_signals(2, accumulation_strength=0.8, liquidity_inflow=0.8),
        _daily_signals(3, distribution_strength=0.8, fake_move_score=0.8),
    ]

    result = compute_daily_confidence(
        signals,
        _confidence_parameters(consistency_window=2),
    )

    assert all(0 <= confidence.confidence <= 1 for confidence in result)


def test_daily_confidence_input_list_is_not_mutated() -> None:
    signals = [
        _daily_signals(0, accumulation_strength=0.8),
        _daily_signals(1, accumulation_strength=0.8),
    ]
    original_signals = signals.copy()

    compute_daily_confidence(signals, _confidence_parameters(consistency_window=2))

    assert signals == original_signals


def test_daily_confidence_invalid_confidence_parameters_raise_value_error() -> None:
    with pytest.raises(ValueError, match="consistency_window must be > 1"):
        _confidence_parameters(consistency_window=1)


def test_daily_confidence_does_not_return_raw_dicts() -> None:
    signals = [
        _daily_signals(0, accumulation_strength=0.8),
        _daily_signals(1, accumulation_strength=0.8),
    ]

    result = compute_daily_confidence(
        signals,
        _confidence_parameters(consistency_window=2),
    )

    assert all(isinstance(value, DailyConfidence) for value in result)
    assert not any(isinstance(value, dict) for value in result)


def test_daily_confidence_does_not_compute_score_or_market_phase() -> None:
    signals = [
        _daily_signals(0, accumulation_strength=0.8),
        _daily_signals(1, accumulation_strength=0.8),
    ]

    result = compute_daily_confidence(
        signals,
        _confidence_parameters(consistency_window=2),
    )

    assert not hasattr(result[0], "smart_money_score")
    assert not hasattr(result[0], "phase")
