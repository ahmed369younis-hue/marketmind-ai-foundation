from datetime import date, timedelta

import pytest

from app.domain.data_contract import DailyMarketData
from app.domain.dataset_validation import validate_daily_dataset


def daily_record(day: date, symbol: str = "MMAI") -> DailyMarketData:
    return DailyMarketData(
        date=day,
        open=100.0,
        high=110.0,
        low=95.0,
        close=105.0,
        volume=1_000_000.0,
        symbol=symbol,
    )


def test_valid_daily_dataset_passes() -> None:
    start = date(2026, 1, 1)
    dataset = [
        daily_record(start),
        daily_record(start + timedelta(days=1)),
        daily_record(start + timedelta(days=2)),
    ]

    assert validate_daily_dataset(dataset) is None


@pytest.mark.parametrize(
    ("dataset", "expected_error"),
    [
        ([], "dataset must not be empty"),
        (
            [daily_record(date(2026, 1, 1)), daily_record(date(2026, 1, 2), "OTHER")],
            "all records must have the same symbol",
        ),
        (
            [daily_record(date(2026, 1, 1)), daily_record(date(2026, 1, 1))],
            "dataset must not contain duplicate dates",
        ),
        (
            [daily_record(date(2026, 1, 2)), daily_record(date(2026, 1, 1))],
            "records must be strictly increasing by date",
        ),
        (
            [daily_record(date(2026, 1, 1)), daily_record(date(2026, 1, 3))],
            "dataset must not skip dates",
        ),
    ],
    ids=[
        "empty-dataset",
        "different-symbols",
        "duplicate-date",
        "out-of-order-dates",
        "missing-date-gap",
    ],
)
def test_invalid_daily_datasets_raise_explicit_errors(
    dataset: list[DailyMarketData],
    expected_error: str,
) -> None:
    with pytest.raises(ValueError, match=expected_error):
        validate_daily_dataset(dataset)


def test_daily_dataset_with_none_field_raises_explicit_error() -> None:
    record = daily_record(date(2026, 1, 1))
    object.__setattr__(record, "close", None)

    with pytest.raises(ValueError, match="close must not be None"):
        validate_daily_dataset([record])
