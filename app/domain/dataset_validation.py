"""Dataset-level validation for daily market data records."""

from datetime import timedelta

from app.domain.data_contract import DailyMarketData


def validate_daily_dataset(data: list[DailyMarketData]) -> None:
    """Validate an in-memory daily dataset and raise ValueError on failure."""

    if not data:
        raise ValueError("dataset must not be empty")

    expected_symbol: str | None = None
    previous_date = None
    seen_dates = set()

    for record in data:
        for field_name in ("date", "open", "high", "low", "close", "volume", "symbol"):
            if not hasattr(record, field_name):
                raise ValueError(f"{field_name} must be present")

            if getattr(record, field_name) is None:
                raise ValueError(f"{field_name} must not be None")

        if expected_symbol is None:
            expected_symbol = record.symbol
        elif record.symbol != expected_symbol:
            raise ValueError("all records must have the same symbol")

        if record.date in seen_dates:
            raise ValueError("dataset must not contain duplicate dates")

        if previous_date is not None:
            if record.date <= previous_date:
                raise ValueError("records must be strictly increasing by date")

            if record.date != previous_date + timedelta(days=1):
                raise ValueError("dataset must not skip dates")

        seen_dates.add(record.date)
        previous_date = record.date
