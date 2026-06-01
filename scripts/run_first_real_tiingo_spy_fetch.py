"""Run the first controlled real Tiingo SPY EOD fetch once."""

from datetime import date
import sys

sys.path.insert(0, ".")

from app.data.managed_api_credentials import read_managed_api_credential
from app.data.tiingo_eod_adapter import TiingoEodAdapter
from app.data.tiingo_eod_network_transport import TiingoEodNetworkTransport
from app.data.tiingo_provider_metadata_factory import (
    build_tiingo_provider_contract_from_documentation_evidence,
)
from app.domain.managed_api_fetch_request import (
    ManagedApiEodFetchRequest,
    ManagedApiFetchPricePreference,
)
from app.domain.managed_api_fetch_result import ManagedApiFetchStatus
from app.domain.managed_api_provider_documentation_evidence import (
    ManagedApiDocumentationEvidenceStatus,
    ManagedApiProviderDocumentationEvidence,
)


PROVIDER_NAME = "Tiingo"
SYMBOL = "SPY"
START_DATE_TEXT = "2024-01-02"
END_DATE_TEXT = "2024-01-05"
PRICE_PREFERENCE_TEXT = "ADJUSTED"


def main() -> int:
    try:
        provider = build_tiingo_provider_contract_from_documentation_evidence(
            _documentation_evidence()
        )
        credential_access = read_managed_api_credential(provider)
        if credential_access.status.name != "AVAILABLE":
            _print_failed_summary("Managed API credential is not available")
            return 1

        request = ManagedApiEodFetchRequest(
            provider=provider,
            credential_access=credential_access,
            symbol=SYMBOL,
            start_date=date.fromisoformat(START_DATE_TEXT),
            end_date=date.fromisoformat(END_DATE_TEXT),
            price_preference=ManagedApiFetchPricePreference.ADJUSTED,
            timezone=provider.source.timezone,
            purpose=(
                "First controlled real Tiingo SPY fetch; no ingestion, "
                "persistence, engine execution, or financial conclusions."
            ),
        )
        adapter = TiingoEodAdapter(
            provider,
            TiingoEodNetworkTransport(timeout_seconds=10),
        )
        result = adapter.fetch_eod(request)

        if result.status is ManagedApiFetchStatus.SUCCESS:
            _print_success_summary(result)
            return 0

        _print_failed_summary("Tiingo SPY fetch failed safely")
        return 1
    except Exception:
        _print_failed_summary("Tiingo SPY fetch could not complete safely")
        return 1


def _documentation_evidence() -> ManagedApiProviderDocumentationEvidence:
    return ManagedApiProviderDocumentationEvidence(
        provider_name=PROVIDER_NAME,
        evidence_status=ManagedApiDocumentationEvidenceStatus.DOCUMENTED,
        documentation_reference=(
            "In-memory documentation evidence for the first controlled Tiingo "
            "SPY fetch runner; not provider production approval."
        ),
        documentation_retrieved_date=date(2026, 4, 28),
        supports_eod_ohlcv_evidence=(
            "Evidence text for EOD OHLCV planning metadata only."
        ),
        supports_adjusted_prices_evidence=(
            "Evidence text for adjusted price planning metadata only."
        ),
        supports_corporate_actions_evidence=(
            "Evidence text for corporate action planning metadata only."
        ),
        supported_asset_classes_evidence=(
            "Evidence text for US equities and ETFs planning metadata only."
        ),
        rate_limit_evidence=(
            "Rate-limit evidence text for one controlled SPY request only."
        ),
        legal_access_evidence=(
            "User stated legal Tiingo API access is available through the "
            "configured environment variable for this single controlled run."
        ),
        notes=(
            "Documentation evidence record is used only to construct Tiingo "
            "metadata for this one controlled fetch runner."
        ),
    )


def _print_success_summary(result) -> None:
    print("FIRST_REAL_TIINGO_SPY_FETCH_STATUS=SUCCESS")
    print(f"PROVIDER={PROVIDER_NAME}")
    print(f"SYMBOL={SYMBOL}")
    print(f"START_DATE={START_DATE_TEXT}")
    print(f"END_DATE={END_DATE_TEXT}")
    print(f"PRICE_PREFERENCE={PRICE_PREFERENCE_TEXT}")
    print(f"RECORDS_COUNT={result.records_count}")
    print(f"FIRST_RECORD_DATE={result.first_record_date.isoformat()}")
    print(f"LAST_RECORD_DATE={result.last_record_date.isoformat()}")
    print("NO_RECORD_VALUES_PRINTED=True")
    print("NO_RAW_PAYLOAD_PRINTED=True")
    print("NO_DATA_PERSISTED=True")
    print("NO_DAILYMARKETDATA_CONVERSION=True")
    print("NO_INGESTION=True")
    print("NO_ENGINE_EXECUTION=True")
    print("NO_FINANCIAL_CONCLUSIONS=True")


def _print_failed_summary(error_message: str) -> None:
    safe_message = error_message.replace("\n", " ").replace("\r", " ")
    print("FIRST_REAL_TIINGO_SPY_FETCH_STATUS=FAILED")
    print(f"PROVIDER={PROVIDER_NAME}")
    print(f"SYMBOL={SYMBOL}")
    print(f"START_DATE={START_DATE_TEXT}")
    print(f"END_DATE={END_DATE_TEXT}")
    print(f"ERROR_MESSAGE={safe_message}")
    print("NO_DATA_PERSISTED=True")
    print("NO_FINANCIAL_CONCLUSIONS=True")


if __name__ == "__main__":
    raise SystemExit(main())
