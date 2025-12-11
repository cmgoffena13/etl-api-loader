import asyncio
import random
from typing import Optional

import httpx
import pendulum
import structlog

logger = structlog.getLogger(__name__)

RETRIABLE_STATUS_CODES = {
    104: "Connection Reset",
    408: "Request Timeout",
    429: "Too Many Requests (rate limited)",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
}

HTTPX_EXCEPTIONS = {
    httpx.TimeoutException: "Timeout",
    httpx.NetworkError: "Network error",
    httpx.ConnectError: "Connection error",
    httpx.ConnectTimeout: "Connection timeout",
    httpx.ReadTimeout: "Read timeout",
    httpx.PoolTimeout: "Pool timeout",
    httpx.LocalProtocolError: "Local protocol error",
}

HTTPX_EXCEPTIONS_KEYS = tuple(HTTPX_EXCEPTIONS.keys())


def _parse_retry_after(retry_after_header: Optional[str]) -> Optional[float]:
    """Parse the Retry-After header value."""
    if not retry_after_header:
        return None

    try:
        seconds = int(retry_after_header.strip())
        return float(seconds)
    except ValueError:
        try:
            retry_date = pendulum.parse(retry_after_header.strip())
            now = pendulum.now()
            seconds = (retry_date - now).total_seconds()
            # If date is in the past or invalid, fall back to None
            if seconds <= 0:
                return None
            return seconds
        except Exception:
            logger.warning(f"Could not parse Retry-After header: {retry_after_header}")
            return None


def _calculate_backoff(attempt: int, backoff_starting_delay: float = 1) -> float:
    """Calculate exponential backoff delay with jitter."""
    start_delay = backoff_starting_delay - 0.2
    end_delay = backoff_starting_delay + 0.2
    return random.uniform(start_delay, end_delay) * (2**attempt)


def _calculate_backoff_for_response(
    status_code: int,
    headers: httpx.Headers,
    attempt: int,
    backoff_starting_delay: float = 1,
) -> float:
    """Calculate backoff delay for a response with retry logic."""
    # Respect Retry-After header for 429 (rate limiting) and 503 (service unavailable)
    if status_code in (429, 503):
        retry_after = _parse_retry_after(headers.get("Retry-After"))
        if retry_after is not None:
            return retry_after

    return _calculate_backoff(attempt, backoff_starting_delay)


class AsyncProductionHTTPClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        connect_timeout: float = 5.0,
        read_timeout: float = 10.0,
        write_timeout: float = 5.0,
        pool_timeout: float = 2.0,
        max_connections: int = 50,
        max_keepalive_connections: int = 20,
        keepalive_expiry: float = 30.0,
        max_attempts: int = 5,  # Total number of attempts (initial + retries)
        default_headers: Optional[dict] = None,
    ):
        self.base_url = base_url
        self.max_attempts = max_attempts

        # Configure timeout with individual timeout controls
        httpx_timeout = httpx.Timeout(
            connect=connect_timeout,  # Max seconds to wait while establishing the TCP connection
            read=read_timeout,  # Max seconds to wait to receive data (response body reading)
            write=write_timeout,  # Max seconds to wait to send data (request body sending)
            pool=pool_timeout,  # Max seconds to wait when trying to acquire a connection from the pool
        )

        client_kwargs = {
            "timeout": httpx_timeout,
            "headers": default_headers,
            "limits": httpx.Limits(
                max_keepalive_connections=max_keepalive_connections,
                max_connections=max_connections,
                keepalive_expiry=keepalive_expiry,
            ),
            "http2": True,  # Enable HTTP/2 for better connection reuse
        }
        if base_url is not None:
            client_kwargs["base_url"] = base_url

        self.client = httpx.AsyncClient(**client_kwargs)

    async def close(self):
        """Clean up the client and close all connections."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def request_with_retry(
        self, method: str, url: str, backoff_starting_delay: float = 1, **kwargs
    ) -> httpx.Response:
        """Make an HTTP request with automatic retry for transient errors."""
        last_exception = None

        for attempt in range(self.max_attempts):
            try:
                response = await self.client.request(method, url, **kwargs)

                if response.status_code in RETRIABLE_STATUS_CODES:
                    if attempt < self.max_attempts - 1:
                        error_desc = RETRIABLE_STATUS_CODES[response.status_code]
                        backoff = _calculate_backoff_for_response(
                            response.status_code,
                            response.headers,
                            attempt,
                            backoff_starting_delay,
                        )
                        logger.warning(
                            f"{error_desc} on {method} {url}, retrying in {backoff:.2f}s (attempt {attempt + 1}/{self.max_attempts})"
                        )
                        await asyncio.sleep(backoff)
                        continue
                    else:
                        response.raise_for_status()

                elif 400 <= response.status_code < 500:
                    response.raise_for_status()

                return response

            except HTTPX_EXCEPTIONS_KEYS as e:
                last_exception = e
                error_desc = HTTPX_EXCEPTIONS[type(e)]
                if attempt < self.max_attempts - 1:
                    backoff = _calculate_backoff(attempt, backoff_starting_delay)
                    logger.warning(
                        f"{error_desc} on {method} {url}, retrying in {backoff:.2f}s (attempt {attempt + 1}/{self.max_attempts})"
                    )
                    await asyncio.sleep(backoff)
                else:
                    raise

        if last_exception:
            raise last_exception
        raise RuntimeError("Unexpected error in request_with_retry")

    async def get(
        self, url: str, backoff_starting_delay: float = 1, **kwargs
    ) -> httpx.Response:
        """GET request with retry logic."""
        return await self.request_with_retry(
            "GET", url, backoff_starting_delay, **kwargs
        )

    async def post(
        self, url: str, backoff_starting_delay: float = 1, **kwargs
    ) -> httpx.Response:
        """POST request with retry logic."""
        return await self.request_with_retry(
            "POST", url, backoff_starting_delay, **kwargs
        )

    async def put(
        self, url: str, backoff_starting_delay: float = 1, **kwargs
    ) -> httpx.Response:
        """PUT request with retry logic."""
        return await self.request_with_retry(
            "PUT", url, backoff_starting_delay, **kwargs
        )

    async def delete(
        self, url: str, backoff_starting_delay: float = 1, **kwargs
    ) -> httpx.Response:
        """DELETE request with retry logic."""
        return await self.request_with_retry(
            "DELETE", url, backoff_starting_delay, **kwargs
        )
