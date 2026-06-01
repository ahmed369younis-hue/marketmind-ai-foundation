import inspect

import pytest

from app.domain.signal_parameters import SignalParameters


def valid_signal_parameters(**overrides: object) -> dict[str, object]:
    parameters: dict[str, object] = {
        "rolling_window": 3,
        "threshold_std": 0.5,
        "support_level": 10.0,
        "breakout_level": 15.0,
        "high_volume_threshold": 1000.0,
        "low_volume_threshold": 100.0,
        "low_price_movement_threshold": 0.2,
        "reversal_candles": 2,
    }
    parameters.update(overrides)
    return parameters


def test_valid_signal_parameters_passes() -> None:
    parameters = SignalParameters(**valid_signal_parameters())

    assert parameters.rolling_window == 3


@pytest.mark.parametrize(
    ("overrides", "expected_error"),
    [
        ({"rolling_window": 1}, "rolling_window must be > 1"),
        ({"threshold_std": 0.0}, "threshold_std must be > 0"),
        ({"support_level": 0.0}, "support_level must be > 0"),
        ({"breakout_level": 0.0}, "breakout_level must be > 0"),
        ({"high_volume_threshold": 0.0}, "high_volume_threshold must be > 0"),
        ({"low_volume_threshold": -0.1}, "low_volume_threshold must be >= 0"),
        (
            {"low_price_movement_threshold": -0.1},
            "low_price_movement_threshold must be >= 0",
        ),
        ({"reversal_candles": 0}, "reversal_candles must be > 0"),
    ],
    ids=[
        "rolling-window-too-small",
        "threshold-std-not-positive",
        "support-level-not-positive",
        "breakout-level-not-positive",
        "high-volume-threshold-not-positive",
        "low-volume-threshold-negative",
        "low-price-movement-threshold-negative",
        "reversal-candles-not-positive",
    ],
)
def test_invalid_signal_parameters_raise_explicit_value_errors(
    overrides: dict[str, object],
    expected_error: str,
) -> None:
    with pytest.raises(ValueError, match=expected_error):
        SignalParameters(**valid_signal_parameters(**overrides))


def test_signal_parameters_constructor_requires_explicit_values() -> None:
    signature = inspect.signature(SignalParameters)

    assert all(
        parameter.default is inspect.Parameter.empty
        for parameter in signature.parameters.values()
    )

    with pytest.raises(TypeError):
        SignalParameters()
