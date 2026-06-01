from datetime import date, timedelta
from pathlib import Path

import pytest

from app.domain.data_ingestion_plan import DataIngestionPlan
from app.domain.data_source_contract import (
    DataGranularity,
    DataSourceContract,
    DataSourceReliability,
    DataSourceType,
)


def _source(**overrides: object) -> DataSourceContract:
    values = {
        "name": "Eligible Metadata Source",
        "source_type": DataSourceType.REAL,
        "granularity": DataGranularity.DAILY,
        "reliability": DataSourceReliability.VERIFIED_STRUCTURE_ONLY,
        "supports_ohlcv": True,
        "supports_adjusted_prices": True,
        "supports_corporate_actions": True,
        "timezone": "UTC",
        "notes": "Metadata-only source for ingestion planning tests.",
    }
    values.update(overrides)
    return DataSourceContract(**values)


def _plan(**overrides: object) -> DataIngestionPlan:
    values = {
        "source": _source(),
        "symbol": "AAPL",
        "start_date": date(2024, 1, 1),
        "end_date": date(2024, 1, 10),
        "use_adjusted_prices": True,
        "include_corporate_actions": True,
        "purpose": "Future ingestion planning test.",
    }
    values.update(overrides)
    return DataIngestionPlan(**values)


def test_valid_ingestion_plan_with_eligible_real_daily_source_passes() -> None:
    plan = _plan()

    assert isinstance(plan, DataIngestionPlan)


def test_non_data_source_contract_source_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _plan(source="not a data source")


def test_ineligible_mock_source_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _plan(source=_source(source_type=DataSourceType.MOCK))


def test_ineligible_synthetic_source_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _plan(source=_source(source_type=DataSourceType.SYNTHETIC))


def test_empty_symbol_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _plan(symbol=" ")


def test_future_start_date_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _plan(start_date=date.today() + timedelta(days=1))


def test_future_end_date_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _plan(end_date=date.today() + timedelta(days=1))


def test_end_date_before_start_date_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _plan(start_date=date(2024, 1, 10), end_date=date(2024, 1, 1))


def test_non_bool_use_adjusted_prices_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _plan(use_adjusted_prices="yes")


def test_non_bool_include_corporate_actions_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _plan(include_corporate_actions="yes")


def test_adjusted_prices_intent_requires_source_support() -> None:
    with pytest.raises(ValueError):
        _plan(
            source=_source(supports_adjusted_prices=False),
            use_adjusted_prices=True,
        )


def test_corporate_actions_intent_requires_source_support() -> None:
    with pytest.raises(ValueError):
        _plan(
            source=_source(supports_corporate_actions=False),
            include_corporate_actions=True,
        )


def test_empty_purpose_raises_value_error() -> None:
    with pytest.raises(ValueError):
        _plan(purpose=" ")


def test_constructor_requires_explicit_values_and_has_no_defaults() -> None:
    with pytest.raises(TypeError):
        DataIngestionPlan()


def test_no_external_dependency_imports_are_introduced() -> None:
    source = Path("app/domain/data_ingestion_plan.py").read_text(encoding="utf-8")

    for package_name in ["pandas", "numpy", "yfinance", "requests", "sqlalchemy"]:
        assert f"import {package_name}" not in source
        assert f"from {package_name}" not in source
