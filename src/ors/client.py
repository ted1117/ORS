from datetime import date
from urllib.parse import unquote

import httpx

from src.ors.exceptions import ORSHTTPError, ORSTimeoutError
from src.ors.parser import parse_response
from src.ors.schemas import VideoRatingPage


class ORSClient:
    """영등위 비디오물 등급분류정보 조회 API 클라이언트"""

    def __init__(self, api_key: str, base_url: str, timeout: float = 10.0):
        self.api_key = unquote(api_key)
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._client.aclose()

    async def fetch(
        self,
        company_name: str,
        page: int = 1,
        page_size: int = 100,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> VideoRatingPage:

        params = {
            "serviceKey": self.api_key,
            "pageNo": page,
            "numOfRows": page_size,
            "aplcName": company_name,
        }

        if start_date is not None:
            params["stDate"] = start_date.strftime("%Y%m%d")
        if end_date is not None:
            params["edDate"] = end_date.strftime("%Y%m%d")

        try:
            response = await self._client.get("/video_search_v2", params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise ORSHTTPError(
                f"ORS API request failed with status code {e.response.status_code}"
            ) from e
        except httpx.TimeoutException as e:
            raise ORSTimeoutError("ORS API request timed out") from e

        return parse_response(response.text)

    async def close(self):
        await self._client.aclose()
