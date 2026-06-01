from datetime import date, timedelta

import pytest

from app.domain.data_contract import DailyMarketData


def valid_daily_record(**overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
        "date": date.today(),
        "open": 100.0,
        "high": 110.0,
        "low": 95.0,
        "close": 105.0,
        "volume": 1_000_000.0,
        "symbol": "MMAI",
    }
    record.update(overrides)
    return record


def test_valid_daily_market_data_record_passes() -> None:
    record = DailyMarketData(**valid_daily_record())

    assert record.symbol == "MMAI"


@pytest.mark.parametrize(
    ("overrides", "expected_error"),
    [
        ({"open": -1.0}, "open must be > 0"),
        ({"high": 90.0, "low": 95.0}, "high must be >= low"),
        ({"date": date.today() + timedelta(days=1)}, "date must not be in the future"),
        ({"symbol": ""}, "symbol must not be empty"),
        ({"volume": -1.0}, "volume must be >= 0"),
    ],
    ids=[
        "negative-price",
        "high-below-low",
        "future-date",
        "empty-symbol",
        "negative-volume",
    ],
)
def test_invalid_daily_market_data_records_raise_explicit_errors(
    overrides: dict[str, object],
    expected_error: str,
) -> None:
    with pytest.raises(ValueError, match=expected_error):
        DailyMarketData(**valid_daily_record(**overrides))
