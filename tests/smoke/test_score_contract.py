from datetime import date, timedelta

import pytest

from app.domain.score_contract import DailyScore


def valid_daily_score(**overrides: object) -> dict[str, object]:
    score: dict[str, object] = {
        "date": date.today(),
        "symbol": "MMAI",
        "smart_money_score": 50.0,
    }
    score.update(overrides)
    return score


def test_valid_daily_score_passes() -> None:
    score = DailyScore(**valid_daily_score())

    assert score.smart_money_score == 50.0


@pytest.mark.parametrize(
    ("overrides", "expected_error"),
    [
        ({"date": date.today() + timedelta(days=1)}, "date must not be in the future"),
        ({"symbol": ""}, "symbol must not be empty"),
        ({"smart_money_score": -0.1}, "smart_money_score must be within \\[0,100\\]"),
        ({"smart_money_score": 100.1}, "smart_money_score must be within \\[0,100\\]"),
    ],
    ids=[
        "future-date",
        "empty-symbol",
        "smart-money-score-below-zero",
        "smart-money-score-above-one-hundred",
    ],
)
def test_invalid_daily_score_raises_explicit_errors(
    overrides: dict[str, object],
    expected_error: str,
) -> None:
    with pytest.raises(ValueError, match=expected_error):
        DailyScore(**valid_daily_score(**overrides))
