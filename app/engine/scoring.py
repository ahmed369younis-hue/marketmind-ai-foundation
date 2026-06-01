"""Smart Money score computation utilities."""

from app.domain.score_contract import DailyScore
from app.domain.signal_contract import DailySignals


def compute_daily_scores(signals: list[DailySignals]) -> list[DailyScore]:
    """Compute DailyScore objects from validated DailySignals."""

    daily_scores: list[DailyScore] = []
    for signal in signals:
        raw_score = (
            (signal.accumulation_strength * 0.25)
            + (signal.distribution_strength * 0.20)
            + (signal.liquidity_inflow * 0.20)
            + (signal.liquidity_outflow * 0.15)
            + (signal.absorption_score * 0.10)
            - (signal.fake_move_score * 0.10)
        )
        smart_money_score = min(max(raw_score * 100, 0.0), 100.0)

        daily_scores.append(
            DailyScore(
                date=signal.date,
                symbol=signal.symbol,
                smart_money_score=smart_money_score,
            )
        )

    return daily_scores
