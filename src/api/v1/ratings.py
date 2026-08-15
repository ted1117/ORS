from datetime import date

from fastapi import APIRouter, HTTPException

from src.core.config import settings
from src.ors.client import ORSClient
from src.ors.exceptions import ORSHTTPError, ORSResponseError, ORSTimeoutError
from src.ors.schemas import VideoRatingPage

router = APIRouter()


@router.get("", response_model=VideoRatingPage)
async def get_video_ratings(
    company_name: str,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 100,
) -> VideoRatingPage:
    async with ORSClient(
        api_key=settings.ors_api_key,
        base_url=settings.ors_api_base_url,
        timeout=settings.ors_api_timeout,
    ) as client:
        try:
            return await client.fetch(
                company_name=company_name,
                start_date=start_date,
                end_date=end_date,
                page=page,
                page_size=page_size,
            )
        except (ORSHTTPError, ORSResponseError, ORSTimeoutError) as e:
            raise HTTPException(
                status_code=502, detail="ORS API request failed."
            ) from e
