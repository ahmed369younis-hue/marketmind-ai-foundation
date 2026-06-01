"""Data source metadata evaluation utilities."""

from app.domain.data_source_contract import (
    DataGranularity,
    DataSourceContract,
    DataSourceReliability,
    DataSourceType,
)
from app.domain.data_source_evaluation_contract import (
    DataSourceEvaluationCheck,
    DataSourceEvaluationResult,
)


def evaluate_data_source_metadata(
    source: DataSourceContract,
) -> list[DataSourceEvaluationResult]:
    """Evaluate declared source metadata without ingesting or verifying real data."""

    def reliability_after(passed: bool) -> DataSourceReliability:
        if passed:
            return DataSourceReliability.VERIFIED_STRUCTURE_ONLY
        return DataSourceReliability.UNVERIFIED

    results: list[DataSourceEvaluationResult] = []

    source_type_passed = source.source_type == DataSourceType.REAL
    results.append(
        DataSourceEvaluationResult(
            source_name=source.name,
            check=DataSourceEvaluationCheck.SOURCE_TYPE_CHECK,
            passed=source_type_passed,
            reliability_after_check=reliability_after(source_type_passed),
            details=(
                "Only REAL sources are acceptable for future production validation; "
                "MOCK and SYNTHETIC sources are allowed only for tests."
            ),
        )
    )

    granularity_passed = source.granularity == DataGranularity.DAILY
    results.append(
        DataSourceEvaluationResult(
            source_name=source.name,
            check=DataSourceEvaluationCheck.GRANULARITY_CHECK,
            passed=granularity_passed,
            reliability_after_check=reliability_after(granularity_passed),
            details="Phase 2 allows DAILY granularity only.",
        )
    )

    ohlcv_passed = source.supports_ohlcv is True
    results.append(
        DataSourceEvaluationResult(
            source_name=source.name,
            check=DataSourceEvaluationCheck.OHLCV_SUPPORT_CHECK,
            passed=ohlcv_passed,
            reliability_after_check=reliability_after(ohlcv_passed),
            details="OHLCV support is mandatory for MarketMind AI engine inputs.",
        )
    )

    adjusted_prices_passed = source.supports_adjusted_prices is True
    results.append(
        DataSourceEvaluationResult(
            source_name=source.name,
            check=DataSourceEvaluationCheck.ADJUSTED_PRICE_SUPPORT_CHECK,
            passed=adjusted_prices_passed,
            reliability_after_check=reliability_after(adjusted_prices_passed),
            details="Adjusted prices are required for safer historical evaluation.",
        )
    )

    corporate_actions_passed = source.supports_corporate_actions is True
    results.append(
        DataSourceEvaluationResult(
            source_name=source.name,
            check=DataSourceEvaluationCheck.CORPORATE_ACTIONS_SUPPORT_CHECK,
            passed=corporate_actions_passed,
            reliability_after_check=reliability_after(corporate_actions_passed),
            details=(
                "Corporate actions support is required to reduce distorted "
                "historical interpretation."
            ),
        )
    )

    timezone_passed = source.timezone.strip() != ""
    results.append(
        DataSourceEvaluationResult(
            source_name=source.name,
            check=DataSourceEvaluationCheck.TIMEZONE_CHECK,
            passed=timezone_passed,
            reliability_after_check=reliability_after(timezone_passed),
            details="Timezone metadata is required for date alignment.",
        )
    )

    previous_checks_passed = all(result.passed for result in results)
    reliability_passed = (
        previous_checks_passed
        and source.reliability == DataSourceReliability.VERIFIED_STRUCTURE_ONLY
    )
    results.append(
        DataSourceEvaluationResult(
            source_name=source.name,
            check=DataSourceEvaluationCheck.RELIABILITY_CLASSIFICATION_CHECK,
            passed=reliability_passed,
            reliability_after_check=reliability_after(reliability_passed),
            details=(
                "VERIFIED_STRUCTURE_ONLY is the maximum reliability allowed at "
                "metadata-evaluation stage; VERIFIED_HISTORICAL must not be "
                "assigned without real historical data validation."
            ),
        )
    )

    return results


def is_data_source_eligible_for_ingestion(
    source: DataSourceContract,
) -> bool:
    """Return whether source metadata passes the structure-only ingestion gate."""

    results = evaluate_data_source_metadata(source)
    return all(result.passed for result in results) and all(
        result.reliability_after_check != DataSourceReliability.VERIFIED_HISTORICAL
        for result in results
    )
