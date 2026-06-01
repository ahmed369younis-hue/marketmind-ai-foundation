"""Tiingo EOD prices transport using standard-library urllib."""

from collections.abc import Callable
import urllib.error
import urllib.parse
import urllib.request

from app.domain.managed_api_fetch_request import ManagedApiEodFetchRequest


TIINGO_EOD_PRICES_BASE_URL = "https://api.tiingo.com/tiingo/daily"


def build_tiingo_eod_prices_url(request: ManagedApiEodFetchRequest) -> str:
    """Build a Tiingo EOD prices URL without credential material."""
    if not isinstance(request, ManagedApiEodFetchRequest):
        raise ValueError("request must be a ManagedApiEodFetchRequest instance")

    symbol_path = urllib.parse.quote(request.symbol, safe="")
    query = urllib.parse.urlencode(
        {
            "startDate": request.start_date.isoformat(),
            "endDate": request.end_date.isoformat(),
            "resampleFreq": "daily",
        }
    )
    return f"{TIINGO_EOD_PRICES_BASE_URL}/{symbol_path}/prices?{query}"


class TiingoEodNetworkTransport:
    """Callable Tiingo EOD prices transport with injectable opener."""

    def __init__(
        self,
        urlopen: Callable | None = None,
        timeout_seconds: int = 10,
    ) -> None:
        if urlopen is not None and not callable(urlopen):
            raise ValueError("urlopen must be callable")

        if type(timeout_seconds) is not int or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be a positive integer")

        self._urlopen = urlopen or urllib.request.urlopen
        self._timeout_seconds = timeout_seconds

    def __call__(
        self,
        request: ManagedApiEodFetchRequest,
        raw_credential: str,
    ) -> str:
        if not isinstance(request, ManagedApiEodFetchRequest):
            raise ValueError("request must be a ManagedApiEodFetchRequest instance")

        if type(raw_credential) is not str or not raw_credential.strip():
            raise ValueError("raw_credential must be a non-empty string")

        url = build_tiingo_eod_prices_url(request)
        network_request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "Authorization": f"Token {raw_credential}",
            },
            method="GET",
        )

        try:
            response = self._urlopen(
                network_request,
                timeout=self._timeout_seconds,
            )
        except urllib.error.HTTPError as exc:
            raise ValueError("Tiingo EOD request failed with HTTP error") from exc
        except urllib.error.URLError as exc:
            raise ValueError("Tiingo EOD request failed with URL error") from exc

        status = self._response_status(response)
        if status is not None and status != 200:
            raise ValueError("Tiingo EOD request returned non-200 status")

        response_body = response.read().decode("utf-8")
        if raw_credential in response_body:
            raise ValueError("Tiingo EOD response body must not contain raw credential")

        return response_body

    def _response_status(self, response: object) -> object | None:
        status = getattr(response, "status", None)
        if status is not None:
            return status

        getcode = getattr(response, "getcode", None)
        if callable(getcode):
            return getcode()

        return None
