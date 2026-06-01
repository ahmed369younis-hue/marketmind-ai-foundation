from datetime import date, timedelta

import pytest

from app.domain.signal_contract import DailySignals


def valid_daily_signals(**overrides: object) -> dict[str, object]:
    signals: dict[str, object] = {
        "date": date.today(),
        "symbol": "MMAI",
        "accumulation_strength": 0.4,
        "distribution_strength": 0.3,
        "liquidity_inflow": 0.6,
        "liquidity_outflow": 0.2,
        "absorption_score": 0.5,
        "fake_move_score": 0.1,
    }
    signals.update(overrides)
    return signals


def test_valid_daily_signals_passes() -> None:
    signals = DailySignals(**valid_daily_signals())

    assert signals.accumulation_strength == 0.4


@pytest.mark.parametrize(
    ("overrides", "expected_error"),
    [
        ({"date": date.today() + timedelta(days=1)}, "date must not be in the future"),
        ({"symbol": ""}, "symbol must not be empty"),
        (
            {"accumulation_strength": -0.1},
            "accumulation_strength must be within \\[0,1\\]",
        ),
        (
            {"distribution_strength": 1.1},
            "distribution_strength must be within \\[0,1\\]",
        ),
        ({"liquidity_inflow": -0.1}, "liquidity_inflow must be within \\[0,1\\]"),
        ({"liquidity_outflow": 1.1}, "liquidity_outflow must be within \\[0,1\\]"),
        ({"absorption_score": -0.1}, "absorption_score must be within \\[0,1\\]"),
        ({"fake_move_score": 1.1}, "fake_move_score must be within \\[0,1\\]"),
    ],
    ids=[
        "future-date",
        "empty-symbol",
        "accumulation-strength-below-zero",
        "distribution-strength-above-one",
        "liquidity-inflow-below-zero",
        "liquidity-outflow-above-one",
        "absorption-score-below-zero",
        "fake-move-score-above-one",
    ],
)
def test_invalid_daily_signals_raise_explicit_errors(
    overrides: dict[str, object],
    expected_error: str,
) -> None:
    with pytest.raises(ValueError, match=expected_error):
        DailySignals(**valid_daily_signals(**overrides))
