from datetime import date

import pytest

from app.domain.score_contract import DailyScore
from app.domain.signal_contract import DailySignals
from app.engine.scoring import compute_daily_scores


def _daily_signals(**overrides: object) -> DailySignals:
    values: dict[str, object] = {
        "date": date(2024, 1, 1),
        "symbol": "MM",
        "accumulation_strength": 0.0,
        "distribution_strength": 0.0,
        "liquidity_inflow": 0.0,
        "liquidity_outflow": 0.0,
        "absorption_score": 0.0,
        "fake_move_score": 0.0,
    }
    values.update(overrides)
    return DailySignals(**values)


def test_daily_scores_empty_input_returns_empty_list() -> None:
    assert compute_daily_scores([]) == []


def test_daily_scores_valid_daily_signals_returns_daily_score_object() -> None:
    result = compute_daily_scores([_daily_signals(accumulation_strength=1.0)])

    assert len(result) == 1
    assert isinstance(result[0], DailyScore)


def test_daily_scores_output_preserves_date_and_symbol() -> None:
    signal = _daily_signals(date=date(2024, 2, 3), symbol="MMAI")

    result = compute_daily_scores([signal])

    assert result[0].date == signal.date
    assert result[0].symbol == signal.symbol


def test_daily_scores_known_formula_case_computes_expected_score() -> None:
    signal = _daily_signals(
        accumulation_strength=1.0,
        distribution_strength=0.5,
        liquidity_inflow=0.25,
        liquidity_outflow=0.2,
        absorption_score=0.75,
        fake_move_score=0.5,
    )

    result = compute_daily_scores([signal])

    assert result[0].smart_money_score == pytest.approx(45.5)


def test_daily_scores_fake_move_score_reduces_score_by_fixed_penalty() -> None:
    without_fake_move = _daily_signals(accumulation_strength=1.0, fake_move_score=0.0)
    with_fake_move = _daily_signals(accumulation_strength=1.0, fake_move_score=1.0)

    result = compute_daily_scores([without_fake_move, with_fake_move])

    assert result[0].smart_money_score - result[1].smart_money_score == pytest.approx(10.0)


def test_daily_scores_negative_raw_score_clamps_to_zero() -> None:
    result = compute_daily_scores([_daily_signals(fake_move_score=1.0)])

    assert result[0].smart_money_score == 0.0


def test_daily_scores_never_exceeds_one_hundred() -> None:
    signal = _daily_signals(
        accumulation_strength=1.0,
        distribution_strength=1.0,
        liquidity_inflow=1.0,
        liquidity_outflow=1.0,
        absorption_score=1.0,
        fake_move_score=0.0,
    )

    result = compute_daily_scores([signal])

    assert result[0].smart_money_score <= 100.0


def test_daily_scores_input_list_is_not_mutated() -> None:
    signals = [_daily_signals(accumulation_strength=1.0)]
    original_signals = signals.copy()

    compute_daily_scores(signals)

    assert signals == original_signals


def test_daily_scores_does_not_return_raw_dicts() -> None:
    result = compute_daily_scores([_daily_signals(accumulation_strength=1.0)])

    assert not any(isinstance(value, dict) for value in result)


def test_daily_scores_does_not_compute_confidence_or_market_phase() -> None:
    result = compute_daily_scores([_daily_signals(accumulation_strength=1.0)])
    score = result[0]

    assert not hasattr(score, "confidence")
    assert not hasattr(score, "phase")
