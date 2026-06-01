"""Data quality gate utilities."""

from app.domain.data_quality_result import DataQualityCheck, DataQualityResult


_REQUIRED_CHECKS = (
    DataQualityCheck.RECORD_COUNT_CHECK,
    DataQualityCheck.DATE_RANGE_COVERAGE_CHECK,
    DataQualityCheck.SYMBOL_CONSISTENCY_CHECK,
    DataQualityCheck.OHLCV_VALIDITY_CHECK,
    DataQualityCheck.DAILY_CONTINUITY_CHECK,
    DataQualityCheck.MISSING_VALUE_CHECK,
)


def can_pass_data_quality_gate(
    results: list[DataQualityResult],
) -> bool:
    """Return whether existing quality audit records satisfy the gate."""

    if type(results) is not list:
        raise ValueError("results must be a list")

    if not results:
        return False

    if any(not isinstance(result, DataQualityResult) for result in results):
        raise ValueError("all results must be DataQualityResult instances")

    checks = [result.check for result in results]
    required_checks = set(_REQUIRED_CHECKS)

    if set(checks) != required_checks:
        return False

    if len(checks) != len(set(checks)):
        return False

    return all(result.passed for result in results)
