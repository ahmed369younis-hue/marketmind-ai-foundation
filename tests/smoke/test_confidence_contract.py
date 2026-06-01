from datetime import date, timedelta

import pytest

from app.domain.confidence_contract import DailyConfidence


def valid_daily_confidence(**overrides: object) -> dict[str, object]:
    confidence: dict[str, object] = {
        "date": date.today(),
        "symbol": "MMAI",
        "confidence": 0.75,
    }
    confidence.update(overrides)
    return confidence


def test_valid_daily_confidence_passes() -> None:
    confidence = DailyConfidence(**valid_daily_confidence())

    assert confidence.confidence == 0.75


@pytest.mark.parametrize(
    ("overrides", "expected_error"),
    [
        ({"date": date.today() + timedelta(days=1)}, "date must not be in the future"),
        ({"symbol": ""}, "symbol must not be empty"),
        ({"confidence": -0.1}, "confidence must be within \\[0,1\\]"),
        ({"confidence": 1.1}, "confidence must be within \\[0,1\\]"),
    ],
    ids=[
        "future-date",
        "empty-symbol",
        "confidence-below-zero",
        "confidence-above-one",
    ],
)
def test_invalid_daily_confidence_raises_explicit_errors(
    overrides: dict[str, object],
    expected_error: str,
) -> None:
    with pytest.raises(ValueError, match=expected_error):
        DailyConfidence(**valid_daily_confidence(**overrides))
