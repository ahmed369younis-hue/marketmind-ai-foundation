import pytest

from app.engine.normalization import min_max_normalize


def test_min_value_returns_zero() -> None:
    assert min_max_normalize(10.0, 10.0, 20.0) == 0.0


def test_max_value_returns_one() -> None:
    assert min_max_normalize(20.0, 10.0, 20.0) == 1.0


def test_midpoint_returns_half() -> None:
    assert min_max_normalize(15.0, 10.0, 20.0) == 0.5


def test_below_min_clamps_to_zero() -> None:
    assert min_max_normalize(5.0, 10.0, 20.0) == 0.0


def test_above_max_clamps_to_one() -> None:
    assert min_max_normalize(25.0, 10.0, 20.0) == 1.0


def test_equal_min_and_max_raises_explicit_error() -> None:
    with pytest.raises(ValueError, match="max_value must be greater than min_value"):
        min_max_normalize(10.0, 10.0, 10.0)


def test_max_less_than_min_raises_explicit_error() -> None:
    with pytest.raises(ValueError, match="max_value must be greater than min_value"):
        min_max_normalize(10.0, 20.0, 10.0)
