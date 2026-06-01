"""Market phase support utilities."""

from app.domain.data_contract import DailyMarketData
from app.domain.dataset_validation import validate_daily_dataset
from app.domain.market_phase_contract import DailyMarketPhase, MarketPhase
from app.domain.market_phase_parameters import MarketPhaseParameters
from app.domain.market_phase_policy import (
    MarketPhasePriority,
    MarketPhaseResolutionPolicy,
)
from app.domain.signal_contract import DailySignals
from app.engine.time_series import rolling_slope


def compute_price_trend(
    closes: list[float],
    parameters: MarketPhaseParameters,
) -> list[str | None]:
    """Compute narrow price trend labels from close-price rolling slope."""

    slopes = rolling_slope(closes, parameters.trend_window)

    results: list[str | None] = []
    for slope in slopes:
        if slope is None:
            results.append(None)
        elif slope >= parameters.markup_trend_threshold:
            results.append("UP")
        elif slope <= parameters.markdown_trend_threshold:
            results.append("DOWN")
        else:
            results.append("NEUTRAL")

    return results


def compute_daily_market_phases(
    data: list[DailyMarketData],
    signals: list[DailySignals],
    parameters: MarketPhaseParameters,
    policy: MarketPhaseResolutionPolicy,
) -> list[DailyMarketPhase]:
    """Compute DailyMarketPhase objects from data, signals, parameters, and policy."""

    validate_daily_dataset(data)

    if not signals:
        return []

    closes = [record.close for record in data]
    trends = compute_price_trend(closes, parameters)
    date_to_trend = {
        record.date: trend
        for record, trend in zip(data, trends)
    }
    dataset_symbol = data[0].symbol

    daily_market_phases: list[DailyMarketPhase] = []
    for signal in signals:
        if signal.symbol != dataset_symbol:
            raise ValueError("signal symbol must match dataset symbol")

        if signal.date not in date_to_trend:
            raise ValueError("signal date must exist in dataset")

        trend = date_to_trend[signal.date]
        if trend is None:
            continue

        accumulation_condition = (
            signal.accumulation_strength >= parameters.accumulation_high_threshold
            and signal.liquidity_inflow >= parameters.liquidity_inflow_high_threshold
        )
        distribution_condition = (
            signal.distribution_strength >= parameters.distribution_high_threshold
            and signal.liquidity_outflow >= parameters.liquidity_outflow_high_threshold
        )
        markup_condition = trend == "UP"
        markdown_condition = trend == "DOWN"

        phase: MarketPhase | None = None
        if policy.priority is MarketPhasePriority.SIGNAL_FIRST:
            if accumulation_condition:
                phase = MarketPhase.ACCUMULATION
            elif distribution_condition:
                phase = MarketPhase.DISTRIBUTION
            elif markup_condition:
                phase = MarketPhase.MARKUP
            elif markdown_condition:
                phase = MarketPhase.MARKDOWN
        elif policy.priority is MarketPhasePriority.TREND_FIRST:
            if markup_condition:
                phase = MarketPhase.MARKUP
            elif markdown_condition:
                phase = MarketPhase.MARKDOWN
            elif accumulation_condition:
                phase = MarketPhase.ACCUMULATION
            elif distribution_condition:
                phase = MarketPhase.DISTRIBUTION

        if phase is None:
            continue

        daily_market_phases.append(
            DailyMarketPhase(
                date=signal.date,
                symbol=signal.symbol,
                phase=phase,
            )
        )

    return daily_market_phases
