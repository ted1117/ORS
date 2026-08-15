import httpx


class OrsClient:
    def __init__(self, api_key: str, base_url: str, timeout: float = 10.0):
        self.api_key = api_key
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
        )

    async def fetch(self, company_name: str, page: int = 1, page_size: int = 100):
        response = await self._client.get(
            "/video_search_v2",
            paraps={
                "service_key": self.api_key,
                "pageNo": page,
                "numOfRows": page_size,
                "aplcName": company_name,
            },
        )

        response.raise_for_status()

        return parse_response(response.text)

    async def close(self):
        await self._client.aclose()
