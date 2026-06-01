import inspect

import pytest

from app.domain.confidence_parameters import ConfidenceParameters


def valid_confidence_parameters(**overrides: object) -> dict[str, object]:
    parameters: dict[str, object] = {
        "consistency_window": 3,
        "signal_active_threshold": 0.6,
    }
    parameters.update(overrides)
    return parameters


def test_valid_confidence_parameters_passes() -> None:
    parameters = ConfidenceParameters(**valid_confidence_parameters())

    assert parameters.consistency_window == 3
    assert parameters.signal_active_threshold == 0.6


def test_consistency_window_less_than_or_equal_to_one_raises_value_error() -> None:
    with pytest.raises(ValueError, match="consistency_window must be > 1"):
        ConfidenceParameters(**valid_confidence_parameters(consistency_window=1))


def test_signal_active_threshold_below_zero_raises_value_error() -> None:
    with pytest.raises(ValueError, match="signal_active_threshold must be within \\[0,1\\]"):
        ConfidenceParameters(**valid_confidence_parameters(signal_active_threshold=-0.1))


def test_signal_active_threshold_above_one_raises_value_error() -> None:
    with pytest.raises(ValueError, match="signal_active_threshold must be within \\[0,1\\]"):
        ConfidenceParameters(**valid_confidence_parameters(signal_active_threshold=1.1))


def test_confidence_parameters_constructor_requires_explicit_values() -> None:
    signature = inspect.signature(ConfidenceParameters)

    assert all(
        parameter.default is inspect.Parameter.empty
        for parameter in signature.parameters.values()
    )

    with pytest.raises(TypeError):
        ConfidenceParameters()
