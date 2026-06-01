"""Tiingo EOD fixture payload parser."""

import json
from datetime import datetime

from app.domain.managed_api_eod_record import (
    ManagedApiEodRecord,
    ManagedApiPriceMode,
)
from app.domain.managed_api_fetch_request import (
    ManagedApiEodFetchRequest,
    ManagedApiFetchPricePreference,
)


_RAW_FIELDS = ("date", "open", "high", "low", "close", "volume")
_ADJUSTED_FIELDS = ("adjOpen", "adjHigh", "adjLow", "adjClose", "adjVolume")
_FIXTURE_NOTE = (
    "Parsed from a documented Tiingo fixture payload; not fetched API data."
)


def parse_tiingo_eod_prices_response(
    payload_json: str,
    request: ManagedApiEodFetchRequest,
) -> list[ManagedApiEodRecord]:
    if type(payload_json) is not str:
        raise ValueError("payload_json must be a string")

    if not isinstance(request, ManagedApiEodFetchRequest):
        raise ValueError("request must be a ManagedApiEodFetchRequest instance")

    rows = _load_payload_rows(payload_json)
    records: list[ManagedApiEodRecord] = []
    seen_dates = set()

    for row_index, row in enumerate(rows, start=1):
        if type(row) is not dict:
            raise ValueError(f"row {row_index} must be a JSON object")

        record_date = _parse_row_date(row, row_index)
        if record_date < request.start_date or record_date > request.end_date:
            raise ValueError(f"row {row_index} date is outside requested range")

        if record_date in seen_dates:
            raise ValueError(f"row {row_index} has a duplicate date")
        seen_dates.add(record_date)

        if request.price_preference is ManagedApiFetchPricePreference.RAW:
            record = _build_raw_record(row, row_index, record_date, request)
        elif request.price_preference is ManagedApiFetchPricePreference.ADJUSTED:
            record = _build_adjusted_record(row, row_index, record_date, request)
        else:
            raise ValueError(
                "request.price_preference must be a valid "
                "ManagedApiFetchPricePreference value"
            )

        records.append(record)

    return records


def _load_payload_rows(payload_json: str) -> list[object]:
    try:
        parsed_payload = json.loads(payload_json)
    except json.JSONDecodeError as exc:
        raise ValueError("payload_json must be valid JSON") from exc

    if type(parsed_payload) is not list:
        raise ValueError("payload_json must be a JSON array")

    if not parsed_payload:
        raise ValueError("payload_json must not be an empty array")

    return parsed_payload


def _parse_row_date(row: dict[object, object], row_index: int):
    _require_fields(row, ("date",), row_index)

    raw_value = row["date"]
    if type(raw_value) is not str or not raw_value.strip():
        raise ValueError(f"row {row_index} date must be a non-empty string")

    normalized_value = raw_value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized_value).date()
    except ValueError as exc:
        raise ValueError(f"row {row_index} date is malformed") from exc


def _build_raw_record(
    row: dict[object, object],
    row_index: int,
    record_date,
    request: ManagedApiEodFetchRequest,
) -> ManagedApiEodRecord:
    _require_fields(row, _RAW_FIELDS, row_index)

    return ManagedApiEodRecord(
        provider_name=request.provider.provider_name,
        symbol=request.symbol,
        date=record_date,
        open=_parse_float(row["open"], "open", row_index),
        high=_parse_float(row["high"], "high", row_index),
        low=_parse_float(row["low"], "low", row_index),
        close=_parse_float(row["close"], "close", row_index),
        volume=_parse_float(row["volume"], "volume", row_index),
        price_mode=ManagedApiPriceMode.RAW,
        timezone=request.timezone,
        adjusted_close=None,
        corporate_action_adjusted=False,
        source_timestamp_utc=None,
        provider_record_id=None,
        notes=_FIXTURE_NOTE,
    )


def _build_adjusted_record(
    row: dict[object, object],
    row_index: int,
    record_date,
    request: ManagedApiEodFetchRequest,
) -> ManagedApiEodRecord:
    _require_fields(row, _RAW_FIELDS + _ADJUSTED_FIELDS, row_index)
    adjusted_close = _parse_float(row["adjClose"], "adjClose", row_index)

    return ManagedApiEodRecord(
        provider_name=request.provider.provider_name,
        symbol=request.symbol,
        date=record_date,
        open=_parse_float(row["adjOpen"], "adjOpen", row_index),
        high=_parse_float(row["adjHigh"], "adjHigh", row_index),
        low=_parse_float(row["adjLow"], "adjLow", row_index),
        close=adjusted_close,
        volume=_parse_float(row["adjVolume"], "adjVolume", row_index),
        price_mode=ManagedApiPriceMode.ADJUSTED,
        timezone=request.timezone,
        adjusted_close=adjusted_close,
        corporate_action_adjusted=True,
        source_timestamp_utc=None,
        provider_record_id=None,
        notes=_FIXTURE_NOTE,
    )


def _require_fields(
    row: dict[object, object],
    field_names: tuple[str, ...],
    row_index: int,
) -> None:
    for field_name in field_names:
        if field_name not in row:
            raise ValueError(f"row {row_index} missing required field: {field_name}")


def _parse_float(value: object, field_name: str, row_index: int) -> float:
    if type(value) not in (int, float):
        raise ValueError(f"row {row_index} field {field_name} must be numeric")

    return float(value)
