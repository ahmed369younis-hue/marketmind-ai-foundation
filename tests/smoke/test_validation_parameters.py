import inspect

import pytest

from app.domain.validation_parameters import ValidationParameters


def valid_validation_parameters(**overrides: object) -> dict[str, object]:
    parameters: dict[str, object] = {
        "high_score_threshold": 75.0,
        "forward_window": 5,
        "forward_return_threshold": 0.02,
        "stability_window": 3,
        "stability_min_persistence_ratio": 0.6,
        "false_signal_window": 4,
        "false_signal_reversal_threshold": 0.03,
    }
    parameters.update(overrides)
    return parameters


def test_valid_validation_parameters_passes() -> None:
    parameters = ValidationParameters(**valid_validation_parameters())

    assert parameters.high_score_threshold == 75.0
    assert parameters.forward_window == 5


def test_high_score_threshold_below_zero_raises_value_error() -> None:
    with pytest.raises(ValueError, match="high_score_threshold must be within \\[0,100\\]"):
        ValidationParameters(**valid_validation_parameters(high_score_threshold=-0.1))


def test_high_score_threshold_above_one_hundred_raises_value_error() -> None:
    with pytest.raises(ValueError, match="high_score_threshold must be within \\[0,100\\]"):
        ValidationParameters(**valid_validation_parameters(high_score_threshold=100.1))


def test_forward_window_less_than_or_equal_to_zero_raises_value_error() -> None:
    with pytest.raises(ValueError, match="forward_window must be > 0"):
        ValidationParameters(**valid_validation_parameters(forward_window=0))


def test_forward_return_threshold_below_zero_raises_value_error() -> None:
    with pytest.raises(ValueError, match="forward_return_threshold must be >= 0"):
        ValidationParameters(**valid_validation_parameters(forward_return_threshold=-0.01))


def test_stability_window_less_than_or_equal_to_one_raises_value_error() -> None:
    with pytest.raises(ValueError, match="stability_window must be > 1"):
        ValidationParameters(**valid_validation_parameters(stability_window=1))


def test_stability_min_persistence_ratio_below_zero_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="stability_min_persistence_ratio must be within \\[0,1\\]",
    ):
        ValidationParameters(
            **valid_validation_parameters(stability_min_persistence_ratio=-0.1)
        )


def test_stability_min_persistence_ratio_above_one_raises_value_error() -> None:
    with pytest.raises(
        ValueError,
        match="stability_min_persistence_ratio must be within \\[0,1\\]",
    ):
        ValidationParameters(
            **valid_validation_parameters(stability_min_persistence_ratio=1.1)
        )


def test_false_signal_window_less_than_or_equal_to_zero_raises_value_error() -> None:
    with pytest.raises(ValueError, match="false_signal_window must be > 0"):
        ValidationParameters(**valid_validation_parameters(false_signal_window=0))


def test_false_signal_reversal_threshold_below_zero_raises_value_error() -> None:
    with pytest.raises(ValueError, match="false_signal_reversal_threshold must be >= 0"):
        ValidationParameters(
            **valid_validation_parameters(false_signal_reversal_threshold=-0.01)
        )


def test_validation_parameters_constructor_requires_explicit_values() -> None:
    signature = inspect.signature(ValidationParameters)

    assert all(
        parameter.default is inspect.Parameter.empty
        for parameter in signature.parameters.values()
    )

    with pytest.raises(TypeError):
        ValidationParameters()
