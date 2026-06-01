"""Market phase resolution policy contract definitions."""

from dataclasses import dataclass
from enum import Enum


class MarketPhasePriority(Enum):
    """Allowed market phase condition resolution priorities."""

    SIGNAL_FIRST = "SIGNAL_FIRST"
    TREND_FIRST = "TREND_FIRST"


@dataclass(frozen=True, slots=True)
class MarketPhaseResolutionPolicy:
    """Required resolution policy contract for future market phase computation."""

    # SIGNAL_FIRST means future phase logic must evaluate accumulation/distribution
    # conditions before markup/markdown trend conditions.
    # TREND_FIRST means future phase logic must evaluate markup/markdown trend
    # conditions before accumulation/distribution conditions.
    priority: MarketPhasePriority

    def __post_init__(self) -> None:
        if not isinstance(self.priority, MarketPhasePriority):
            raise ValueError("priority must be a valid MarketPhasePriority value")
