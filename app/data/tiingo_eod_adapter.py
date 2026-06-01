"""Tiingo EOD adapter using caller-injected in-memory transport."""

from collections.abc import Callable

from app.data.managed_api_fetch_preflight import (
    can_execute_managed_api_fetch_preflight,
)
from app.data.managed_api_runtime_credentials import (
    use_managed_api_runtime_credential,
)
from app.data.tiingo_eod_response_parser import parse_tiingo_eod_prices_response
from app.domain.managed_api_fetch_request import ManagedApiEodFetchRequest
from app.domain.managed_api_fetch_result import (
    ManagedApiEodFetchResult,
    ManagedApiFetchStatus,
)
from app.domain.managed_api_provider_adapter_port import (
    ManagedApiProviderAdapterCapability,
)
from app.domain.managed_api_provider_contract import ManagedApiProviderContract


class _UnsafeTransportPayloadError(ValueError):
    """Raised when injected transport output would expose raw credential data."""


class TiingoEodAdapter:
    """Tiingo EOD adapter boundary backed only by an injected transport callable."""

    def __init__(
        self,
        provider: ManagedApiProviderContract,
        transport: Callable[[ManagedApiEodFetchRequest, str], str],
    ) -> None:
        if not isinstance(provider, ManagedApiProviderContract):
            raise ValueError("provider must be a ManagedApiProviderContract instance")

        if not callable(transport):
            raise ValueError("transport must be callable")

        self._provider = provider
        self._transport = transport

    @property
    def capability(self) -> ManagedApiProviderAdapterCapability:
        return ManagedApiProviderAdapterCapability(
            provider=self._provider,
            adapter_name="TiingoEodAdapter",
            supports_fetch_eod=True,
            supports_raw_prices=True,
            supports_adjusted_prices=True,
            supports_single_symbol_fetch=True,
            supports_bulk_fetch=False,
            notes=(
                "Injected transport only; no real network call; "
                "no production approval."
            ),
        )

    def fetch_eod(
        self,
        request: ManagedApiEodFetchRequest,
    ) -> ManagedApiEodFetchResult:
        if not isinstance(request, ManagedApiEodFetchRequest):
            raise ValueError("request must be a ManagedApiEodFetchRequest instance")

        if request.provider is not self._provider:
            raise ValueError("request.provider must reference adapter provider")

        if not can_execute_managed_api_fetch_preflight(request, self.capability):
            raise ValueError("managed API fetch preflight failed")

        try:
            payload_json = use_managed_api_runtime_credential(
                request.provider,
                request.credential_access,
                lambda raw_credential: self._call_transport(
                    request,
                    raw_credential,
                ),
            )
        except _UnsafeTransportPayloadError:
            raise
        except ValueError:
            return self._failed_result(request)

        try:
            records = parse_tiingo_eod_prices_response(payload_json, request)
        except ValueError:
            return self._failed_result(request)

        return ManagedApiEodFetchResult(
            provider=request.provider,
            status=ManagedApiFetchStatus.SUCCESS,
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            records=records,
            records_count=len(records),
            first_record_date=records[0].date,
            last_record_date=records[-1].date,
            message=(
                "Injected transport fixture payload parsed successfully; "
                "no real API call was made"
            ),
        )

    def _call_transport(
        self,
        request: ManagedApiEodFetchRequest,
        raw_credential: str,
    ) -> str:
        payload_json = self._transport(request, raw_credential)
        if type(payload_json) is not str:
            raise _UnsafeTransportPayloadError(
                "injected transport must return a JSON payload string"
            )

        if payload_json != raw_credential and raw_credential in payload_json:
            raise _UnsafeTransportPayloadError(
                "injected transport payload must not contain raw credential"
            )

        return payload_json

    def _failed_result(
        self,
        request: ManagedApiEodFetchRequest,
    ) -> ManagedApiEodFetchResult:
        return ManagedApiEodFetchResult(
            provider=request.provider,
            status=ManagedApiFetchStatus.FAILED,
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            records=[],
            records_count=0,
            first_record_date=None,
            last_record_date=None,
            message=(
                "Injected transport fixture payload parsing failed; "
                "no real API call was made"
            ),
        )
