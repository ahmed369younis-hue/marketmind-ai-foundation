import pytest

from app.domain.data_source_contract import (
    DataGranularity,
    DataSourceContract,
    DataSourceReliability,
    DataSourceType,
)


def _data_source_contract(**overrides: object) -> DataSourceContract:
    values: dict[str, object] = {
        "name": "Example Source",
        "source_type": DataSourceType.REAL,
        "granularity": DataGranularity.DAILY,
        "reliability": DataSourceReliability.UNVERIFIED,
        "supports_ohlcv": True,
        "supports_adjusted_prices": False,
        "supports_corporate_actions": False,
        "timezone": "UTC",
        "notes": "Metadata-only source contract for future evaluation.",
    }
    values.update(overrides)
    return DataSourceContract(**values)


def test_data_source_contract_valid_real_daily_passes() -> None:
    contract = _data_source_contract(
        source_type=DataSourceType.REAL,
        reliability=DataSourceReliability.VERIFIED_HISTORICAL,
    )

    assert contract.source_type is DataSourceType.REAL
    assert contract.granularity is DataGranularity.DAILY


def test_data_source_contract_valid_mock_daily_passes() -> None:
    contract = _data_source_contract(
        source_type=DataSourceType.MOCK,
        reliability=DataSourceReliability.VERIFIED_STRUCTURE_ONLY,
    )

    assert contract.source_type is DataSourceType.MOCK
    assert contract.granularity is DataGranularity.DAILY


def test_data_source_contract_valid_synthetic_daily_passes() -> None:
    contract = _data_source_contract(
        source_type=DataSourceType.SYNTHETIC,
        reliability=DataSourceReliability.UNVERIFIED,
    )

    assert contract.source_type is DataSourceType.SYNTHETIC
    assert contract.granularity is DataGranularity.DAILY


def test_data_source_contract_empty_name_raises_value_error() -> None:
    with pytest.raises(ValueError, match="name must not be empty"):
        _data_source_contract(name=" ")


def test_data_source_contract_invalid_source_type_string_raises_value_error() -> None:
    with pytest.raises(ValueError, match="source_type must be a valid DataSourceType value"):
        _data_source_contract(source_type="REAL")


def test_data_source_contract_invalid_granularity_string_raises_value_error() -> None:
    with pytest.raises(ValueError, match="granularity must be a valid DataGranularity value"):
        _data_source_contract(granularity="DAILY")


def test_data_source_contract_invalid_reliability_string_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="reliability must be a valid DataSourceReliability value",
    ):
        _data_source_contract(reliability="UNVERIFIED")


def test_data_source_contract_non_bool_supports_ohlcv_raises_value_error() -> None:
    with pytest.raises(ValueError, match="supports_ohlcv must be bool"):
        _data_source_contract(supports_ohlcv="true")


def test_data_source_contract_non_bool_supports_adjusted_prices_raises_value_error() -> None:
    with pytest.raises(ValueError, match="supports_adjusted_prices must be bool"):
        _data_source_contract(supports_adjusted_prices=1)


def test_data_source_contract_non_bool_supports_corporate_actions_raises_value_error() -> None:
    with pytest.raises(ValueError, match="supports_corporate_actions must be bool"):
        _data_source_contract(supports_corporate_actions=None)


def test_data_source_contract_empty_timezone_raises_value_error() -> None:
    with pytest.raises(ValueError, match="timezone must not be empty"):
        _data_source_contract(timezone="")


def test_data_source_contract_empty_notes_raises_value_error() -> None:
    with pytest.raises(ValueError, match="notes must not be empty"):
        _data_source_contract(notes=" ")


def test_data_source_contract_constructor_requires_explicit_values() -> None:
    with pytest.raises(TypeError):
        DataSourceContract()
