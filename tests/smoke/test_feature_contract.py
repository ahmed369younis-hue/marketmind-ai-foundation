from datetime import date, timedelta

import pytest

from app.domain.feature_contract import DailyFeatures


def valid_daily_features(**overrides: object) -> dict[str, object]:
    features: dict[str, object] = {
        "date": date.today(),
        "symbol": "MMAI",
        "range_compression": 0.5,
        "volume_trend": 0.6,
        "price_momentum": 0.4,
        "volume_spike": 2.5,
    }
    features.update(overrides)
    return features


def test_valid_daily_features_passes() -> None:
    features = DailyFeatures(**valid_daily_features())

    assert features.volume_spike == 2.5


@pytest.mark.parametrize(
    ("overrides", "expected_error"),
    [
        ({"date": date.today() + timedelta(days=1)}, "date must not be in the future"),
        ({"symbol": ""}, "symbol must not be empty"),
        ({"range_compression": -0.1}, "range_compression must be within \\[0,1\\]"),
        ({"range_compression": 1.1}, "range_compression must be within \\[0,1\\]"),
        ({"volume_trend": 1.1}, "volume_trend must be within \\[0,1\\]"),
        ({"price_momentum": -0.1}, "price_momentum must be within \\[0,1\\]"),
        ({"volume_spike": -0.1}, "volume_spike must be >= 0"),
    ],
    ids=[
        "future-date",
        "empty-symbol",
        "range-compression-below-zero",
        "range-compression-above-one",
        "volume-trend-above-one",
        "price-momentum-below-zero",
        "negative-volume-spike",
    ],
)
def test_invalid_daily_features_raise_explicit_errors(
    overrides: dict[str, object],
    expected_error: str,
) -> None:
    with pytest.raises(ValueError, match=expected_error):
        DailyFeatures(**valid_daily_features(**overrides))
