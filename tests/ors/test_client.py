from datetime import date
from pathlib import Path

import httpx
import pytest

from src.ors.client import ORSClient
from src.ors.exceptions import ORSHTTPError, ORSResponseError

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.mark.anyio
async def test_fetch():
    xml = (FIXTURES_DIR / "video_search_success.xml").read_text()

    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/video_search_v2"

        params = request.url.params

        assert params["serviceKey"] == "test-api-key"
        assert params["aplcName"] == "크런치롤코리아 유한회사"
        assert params["pageNo"] == "1"
        assert params["numOfRows"] == "1000"
        assert params["stDate"] == "20260701"
        assert params["edDate"] == "20260814"

        return httpx.Response(
            status_code=200,
            text=xml,
        )

    transport = httpx.MockTransport(handler)

    async with ORSClient(
        api_key="test-api-key",
        base_url="https://example.com",
    ) as client:
        await client._client.aclose()
        client._client = httpx.AsyncClient(
            base_url="https://example.com",
            transport=transport,
        )

        result = await client.fetch(
            company_name="크런치롤코리아 유한회사",
            page=1,
            page_size=1000,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 8, 14),
        )

    assert result.page == 1
    assert result.page_size == 1000
    assert result.total_count == 45
    assert len(result.items) == 45
    assert result.items[0].rating_number == "2026-VF02770"


@pytest.mark.anyio
async def test_fetch_http_error():
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=500,
            request=request,
        )

    transport = httpx.MockTransport(handler)

    async with ORSClient(
        api_key="test-api-key",
        base_url="https://example.com",
    ) as client:
        await client._client.aclose()
        client._client = httpx.AsyncClient(
            base_url="https://example.com",
            transport=transport,
        )

        with pytest.raises(
            ORSHTTPError, match="ORS API request failed with status code 500"
        ):
            await client.fetch(
                company_name="크런치롤코리아 유한회사",
            )


@pytest.mark.anyio
async def test_fetch_ors_error():
    xml = """
    <response>
      <header>
        <resultCode>99</resultCode>
        <resultMsg>INVALID_REQUEST</resultMsg>
      </header>
      <body/>
    </response>
    """

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            text=xml,
            request=request,
        )

    transport = httpx.MockTransport(handler)

    async with ORSClient(
        api_key="test-api-key",
        base_url="https://example.com",
    ) as client:
        await client._client.aclose()
        client._client = httpx.AsyncClient(
            base_url="https://example.com",
            transport=transport,
        )

        with pytest.raises(
            ORSResponseError,
            match="ORS API error: 99 INVALID_REQUEST",
        ):
            await client.fetch(
                company_name="크런치롤코리아 유한회사",
            )
