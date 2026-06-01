from datetime import date, timedelta

import pytest

from app.domain.market_phase_contract import DailyMarketPhase, MarketPhase


def valid_daily_market_phase(**overrides: object) -> dict[str, object]:
    market_phase: dict[str, object] = {
        "date": date.today(),
        "symbol": "MMAI",
        "phase": MarketPhase.ACCUMULATION,
    }
    market_phase.update(overrides)
    return market_phase


def test_valid_daily_market_phase_passes() -> None:
    market_phase = DailyMarketPhase(**valid_daily_market_phase())

    assert market_phase.phase is MarketPhase.ACCUMULATION


@pytest.mark.parametrize(
    ("overrides", "expected_error"),
    [
        ({"date": date.today() + timedelta(days=1)}, "date must not be in the future"),
        ({"symbol": ""}, "symbol must not be empty"),
        ({"phase": "INVALID"}, "phase must be a valid MarketPhase value"),
        ({"phase": None}, "phase must be a valid MarketPhase value"),
    ],
    ids=[
        "future-date",
        "empty-symbol",
        "invalid-phase-string",
        "none-phase",
    ],
)
def test_invalid_daily_market_phase_raises_explicit_errors(
    overrides: dict[str, object],
    expected_error: str,
) -> None:
    with pytest.raises(ValueError, match=expected_error):
        DailyMarketPhase(**valid_daily_market_phase(**overrides))
