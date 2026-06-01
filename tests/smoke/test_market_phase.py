from datetime import date, timedelta

import pytest

from app.domain.data_contract import DailyMarketData
from app.domain.market_phase_contract import DailyMarketPhase, MarketPhase
from app.domain.market_phase_parameters import MarketPhaseParameters
from app.domain.market_phase_policy import MarketPhasePriority, MarketPhaseResolutionPolicy
from app.domain.signal_contract import DailySignals
from app.engine.market_phase import compute_daily_market_phases, compute_price_trend


def _daily_record(
    day_offset: int,
    close: float,
    symbol: str = "MM",
) -> DailyMarketData:
    return DailyMarketData(
        date=date(2024, 1, 1) + timedelta(days=day_offset),
        open=close,
        high=close + 1.0,
        low=close - 1.0,
        close=close,
        volume=100.0,
        symbol=symbol,
    )


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


def _market_phase_parameters(**overrides: object) -> MarketPhaseParameters:
    values: dict[str, object] = {
        "accumulation_high_threshold": 0.7,
        "liquidity_inflow_high_threshold": 0.7,
        "distribution_high_threshold": 0.7,
        "liquidity_outflow_high_threshold": 0.7,
        "trend_window": 3,
        "markup_trend_threshold": 1.0,
        "markdown_trend_threshold": -1.0,
    }
    values.update(overrides)
    return MarketPhaseParameters(**values)


def _market_phase_policy(priority: MarketPhasePriority) -> MarketPhaseResolutionPolicy:
    return MarketPhaseResolutionPolicy(priority=priority)


def test_price_trend_empty_closes_returns_empty_list() -> None:
    assert compute_price_trend([], _market_phase_parameters()) == []


def test_price_trend_insufficient_trend_window_returns_none_values() -> None:
    result = compute_price_trend([1.0, 2.0], _market_phase_parameters())

    assert result == [None, None]


def test_price_trend_upward_slope_at_or_above_markup_threshold_returns_up() -> None:
    result = compute_price_trend([1.0, 2.0, 3.0], _market_phase_parameters())

    assert result == [None, None, "UP"]


def test_price_trend_downward_slope_at_or_below_markdown_threshold_returns_down() -> None:
    result = compute_price_trend([3.0, 2.0, 1.0], _market_phase_parameters())

    assert result == [None, None, "DOWN"]


def test_price_trend_slope_between_thresholds_returns_neutral() -> None:
    result = compute_price_trend([1.0, 1.5, 2.0], _market_phase_parameters())

    assert result == [None, None, "NEUTRAL"]


def test_price_trend_none_inside_rolling_window_returns_none() -> None:
    result = compute_price_trend([1.0, None, 3.0], _market_phase_parameters())

    assert result == [None, None, None]


def test_price_trend_input_closes_list_is_not_mutated() -> None:
    closes = [1.0, 2.0, 3.0]
    original_closes = closes.copy()

    compute_price_trend(closes, _market_phase_parameters())

    assert closes == original_closes


def test_price_trend_invalid_market_phase_parameters_raise_value_error() -> None:
    with pytest.raises(ValueError, match="trend_window must be > 1"):
        _market_phase_parameters(trend_window=1)


def test_price_trend_does_not_return_daily_market_phase_objects() -> None:
    result = compute_price_trend([1.0, 2.0, 3.0], _market_phase_parameters())

    assert not any(isinstance(value, DailyMarketPhase) for value in result)


def test_price_trend_outputs_are_only_allowed_values() -> None:
    result = compute_price_trend(
        [1.0, 2.0, 3.0, 2.0, 1.0, 1.5, 2.0],
        _market_phase_parameters(),
    )
    allowed_outputs = {"UP", "DOWN", "NEUTRAL", None}

    assert set(result).issubset(allowed_outputs)


def test_daily_market_phases_empty_signals_returns_empty_list() -> None:
    data = [
        _daily_record(0, 10.0),
        _daily_record(1, 11.0),
        _daily_record(2, 12.0),
    ]

    result = compute_daily_market_phases(
        data,
        [],
        _market_phase_parameters(),
        _market_phase_policy(MarketPhasePriority.SIGNAL_FIRST),
    )

    assert result == []


def test_daily_market_phases_signal_first_resolves_accumulation_before_markup() -> None:
    data = [
        _daily_record(0, 10.0),
        _daily_record(1, 11.0),
        _daily_record(2, 12.0),
    ]
    signals = [
        _daily_signals(
            2,
            accumulation_strength=0.7,
            liquidity_inflow=0.7,
        )
    ]

    result = compute_daily_market_phases(
        data,
        signals,
        _market_phase_parameters(),
        _market_phase_policy(MarketPhasePriority.SIGNAL_FIRST),
    )

    assert result[0].phase is MarketPhase.ACCUMULATION


def test_daily_market_phases_signal_first_resolves_distribution_before_markdown() -> None:
    data = [
        _daily_record(0, 12.0),
        _daily_record(1, 11.0),
        _daily_record(2, 10.0),
    ]
    signals = [
        _daily_signals(
            2,
            distribution_strength=0.7,
            liquidity_outflow=0.7,
        )
    ]

    result = compute_daily_market_phases(
        data,
        signals,
        _market_phase_parameters(),
        _market_phase_policy(MarketPhasePriority.SIGNAL_FIRST),
    )

    assert result[0].phase is MarketPhase.DISTRIBUTION


def test_daily_market_phases_trend_first_resolves_markup_before_accumulation() -> None:
    data = [
        _daily_record(0, 10.0),
        _daily_record(1, 11.0),
        _daily_record(2, 12.0),
    ]
    signals = [
        _daily_signals(
            2,
            accumulation_strength=0.7,
            liquidity_inflow=0.7,
        )
    ]

    result = compute_daily_market_phases(
        data,
        signals,
        _market_phase_parameters(),
        _market_phase_policy(MarketPhasePriority.TREND_FIRST),
    )

    assert result[0].phase is MarketPhase.MARKUP


def test_daily_market_phases_trend_first_resolves_markdown_before_distribution() -> None:
    data = [
        _daily_record(0, 12.0),
        _daily_record(1, 11.0),
        _daily_record(2, 10.0),
    ]
    signals = [
        _daily_signals(
            2,
            distribution_strength=0.7,
            liquidity_outflow=0.7,
        )
    ]

    result = compute_daily_market_phases(
        data,
        signals,
        _market_phase_parameters(),
        _market_phase_policy(MarketPhasePriority.TREND_FIRST),
    )

    assert result[0].phase is MarketPhase.MARKDOWN


def test_daily_market_phases_row_with_trend_none_is_skipped() -> None:
    data = [
        _daily_record(0, 10.0),
        _daily_record(1, 11.0),
        _daily_record(2, 12.0),
    ]
    signals = [
        _daily_signals(
            0,
            accumulation_strength=0.7,
            liquidity_inflow=0.7,
        )
    ]

    result = compute_daily_market_phases(
        data,
        signals,
        _market_phase_parameters(),
        _market_phase_policy(MarketPhasePriority.SIGNAL_FIRST),
    )

    assert result == []


def test_daily_market_phases_row_with_no_true_condition_is_skipped() -> None:
    data = [
        _daily_record(0, 10.0),
        _daily_record(1, 10.2),
        _daily_record(2, 10.4),
    ]
    signals = [_daily_signals(2)]

    result = compute_daily_market_phases(
        data,
        signals,
        _market_phase_parameters(),
        _market_phase_policy(MarketPhasePriority.SIGNAL_FIRST),
    )

    assert result == []


def test_daily_market_phases_signal_symbol_mismatch_raises_value_error() -> None:
    data = [
        _daily_record(0, 10.0),
        _daily_record(1, 11.0),
        _daily_record(2, 12.0),
    ]
    signals = [_daily_signals(2, symbol="OTHER")]

    with pytest.raises(ValueError, match="signal symbol must match dataset symbol"):
        compute_daily_market_phases(
            data,
            signals,
            _market_phase_parameters(),
            _market_phase_policy(MarketPhasePriority.SIGNAL_FIRST),
        )


def test_daily_market_phases_signal_date_missing_from_dataset_raises_value_error() -> None:
    data = [
        _daily_record(0, 10.0),
        _daily_record(1, 11.0),
        _daily_record(2, 12.0),
    ]
    signals = [_daily_signals(3)]

    with pytest.raises(ValueError, match="signal date must exist in dataset"):
        compute_daily_market_phases(
            data,
            signals,
            _market_phase_parameters(),
            _market_phase_policy(MarketPhasePriority.SIGNAL_FIRST),
        )


def test_daily_market_phases_invalid_dataset_raises_value_error() -> None:
    data = [
        _daily_record(0, 10.0),
        _daily_record(2, 12.0),
    ]
    signals = [_daily_signals(2)]

    with pytest.raises(ValueError, match="dataset must not skip dates"):
        compute_daily_market_phases(
            data,
            signals,
            _market_phase_parameters(),
            _market_phase_policy(MarketPhasePriority.SIGNAL_FIRST),
        )


def test_daily_market_phases_output_preserves_date_and_symbol_from_daily_signals() -> None:
    data = [
        _daily_record(0, 10.0, symbol="MMAI"),
        _daily_record(1, 11.0, symbol="MMAI"),
        _daily_record(2, 12.0, symbol="MMAI"),
    ]
    signals = [_daily_signals(2, symbol="MMAI")]

    result = compute_daily_market_phases(
        data,
        signals,
        _market_phase_parameters(),
        _market_phase_policy(MarketPhasePriority.TREND_FIRST),
    )

    assert result[0].date == signals[0].date
    assert result[0].symbol == signals[0].symbol


def test_daily_market_phases_returns_daily_market_phase_objects_not_raw_dicts() -> None:
    data = [
        _daily_record(0, 10.0),
        _daily_record(1, 11.0),
        _daily_record(2, 12.0),
    ]
    signals = [_daily_signals(2)]

    result = compute_daily_market_phases(
        data,
        signals,
        _market_phase_parameters(),
        _market_phase_policy(MarketPhasePriority.TREND_FIRST),
    )

    assert all(isinstance(value, DailyMarketPhase) for value in result)
    assert not any(isinstance(value, dict) for value in result)


def test_daily_market_phases_does_not_compute_confidence_or_score() -> None:
    data = [
        _daily_record(0, 10.0),
        _daily_record(1, 11.0),
        _daily_record(2, 12.0),
    ]
    signals = [_daily_signals(2)]

    result = compute_daily_market_phases(
        data,
        signals,
        _market_phase_parameters(),
        _market_phase_policy(MarketPhasePriority.TREND_FIRST),
    )

    assert not hasattr(result[0], "confidence")
    assert not hasattr(result[0], "smart_money_score")


def test_daily_market_phases_does_not_create_unsupported_phase_values() -> None:
    data = [
        _daily_record(0, 10.0),
        _daily_record(1, 11.0),
        _daily_record(2, 12.0),
        _daily_record(3, 11.0),
        _daily_record(4, 10.0),
    ]
    signals = [_daily_signals(2), _daily_signals(4)]

    result = compute_daily_market_phases(
        data,
        signals,
        _market_phase_parameters(),
        _market_phase_policy(MarketPhasePriority.TREND_FIRST),
    )

    assert all(value.phase in MarketPhase for value in result)
