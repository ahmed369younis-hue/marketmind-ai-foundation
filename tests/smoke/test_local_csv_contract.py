from pathlib import Path

import pytest

from app.domain.local_csv_contract import CsvPriceMode, LocalCsvIngestionContract


def _contract(**overrides: object) -> LocalCsvIngestionContract:
    values = {
        "file_path": "data/raw/sample.csv",
        "delimiter": ",",
        "date_format": "%Y-%m-%d",
        "symbol_column": "symbol",
        "date_column": "date",
        "open_column": "open",
        "high_column": "high",
        "low_column": "low",
        "close_column": "close",
        "volume_column": "volume",
        "price_mode": CsvPriceMode.RAW,
        "timezone": "UTC",
    }
    values.update(overrides)
    return LocalCsvIngestionContract(**values)


def test_valid_raw_csv_contract_passes() -> None:
    contract = _contract(price_mode=CsvPriceMode.RAW)

    assert isinstance(contract, LocalCsvIngestionContract)


def test_valid_adjusted_csv_contract_passes() -> None:
    contract = _contract(price_mode=CsvPriceMode.ADJUSTED)

    assert isinstance(contract, LocalCsvIngestionContract)


def test_empty_file_path_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _contract(file_path=" ")


def test_non_csv_file_path_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _contract(file_path="data/raw/sample.txt")


def test_empty_delimiter_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _contract(delimiter="")


def test_delimiter_longer_than_one_character_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _contract(delimiter="||")


def test_empty_date_format_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _contract(date_format=" ")


def test_empty_symbol_column_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _contract(symbol_column=" ")


def test_empty_date_column_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _contract(date_column=" ")


def test_empty_open_column_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _contract(open_column=" ")


def test_empty_high_column_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _contract(high_column=" ")


def test_empty_low_column_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _contract(low_column=" ")


def test_empty_close_column_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _contract(close_column=" ")


def test_empty_volume_column_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _contract(volume_column=" ")


def test_duplicate_column_names_raise_value_error() -> None:
    with pytest.raises(ValueError):
        _contract(open_column="close")


def test_invalid_price_mode_string_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _contract(price_mode="RAW")


def test_empty_timezone_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _contract(timezone=" ")


def test_constructor_requires_explicit_values_and_has_no_defaults() -> None:
    with pytest.raises(TypeError):
        LocalCsvIngestionContract()


def test_no_external_dependency_imports_are_introduced() -> None:
    source = Path("app/domain/local_csv_contract.py").read_text(encoding="utf-8")

    for package_name in ["pandas", "numpy", "yfinance", "requests", "sqlalchemy"]:
        assert f"import {package_name}" not in source
        assert f"from {package_name}" not in source


def test_no_csv_pathlib_or_file_reading_imports_are_introduced() -> None:
    source = Path("app/domain/local_csv_contract.py").read_text(encoding="utf-8")

    for forbidden_text in [
        "import csv",
        "from csv",
        "import pathlib",
        "from pathlib",
        "open(",
        "read_text",
        "read_csv",
    ]:
        assert forbidden_text not in source
