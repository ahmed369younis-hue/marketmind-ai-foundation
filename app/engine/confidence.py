"""Confidence computation utilities."""

from app.domain.confidence_contract import DailyConfidence
from app.domain.confidence_parameters import ConfidenceParameters
from app.domain.signal_contract import DailySignals


def compute_daily_confidence(
    signals: list[DailySignals],
    parameters: ConfidenceParameters,
) -> list[DailyConfidence]:
    """Compute DailyConfidence objects from signals and explicit parameters."""

    if not signals:
        return []

    constructive_fields = (
        "accumulation_strength",
        "liquidity_inflow",
        "absorption_score",
    )
    opposing_fields = (
        "distribution_strength",
        "liquidity_outflow",
        "fake_move_score",
    )

    dominant_groups: list[str] = []
    agreement_ratios: list[float] = []
    for signal in signals:
        constructive_count = sum(
            1
            for field_name in constructive_fields
            if getattr(signal, field_name) >= parameters.signal_active_threshold
        )
        opposing_count = sum(
            1
            for field_name in opposing_fields
            if getattr(signal, field_name) >= parameters.signal_active_threshold
        )

        if constructive_count > opposing_count:
            dominant_groups.append("CONSTRUCTIVE")
        elif opposing_count > constructive_count:
            dominant_groups.append("OPPOSING")
        else:
            dominant_groups.append("TIE")

        total_active = constructive_count + opposing_count
        if total_active == 0:
            agreement_ratios.append(0.0)
        else:
            agreement_ratios.append(
                max(constructive_count, opposing_count) / total_active
            )

    daily_confidence: list[DailyConfidence] = []
    window = parameters.consistency_window
    for index, signal in enumerate(signals):
        if index + 1 < window:
            continue

        window_groups = dominant_groups[index - window + 1 : index + 1]
        non_tie_groups = [group for group in window_groups if group != "TIE"]
        if not non_tie_groups:
            consistency = 0.0
        else:
            consistency = max(
                non_tie_groups.count("CONSTRUCTIVE"),
                non_tie_groups.count("OPPOSING"),
            ) / len(non_tie_groups)

        confidence = consistency * agreement_ratios[index]
        confidence = min(1.0, max(0.0, confidence))
        daily_confidence.append(
            DailyConfidence(
                date=signal.date,
                symbol=signal.symbol,
                confidence=float(confidence),
            )
        )

    return daily_confidence
