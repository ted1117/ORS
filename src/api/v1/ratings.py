from datetime import date

from fastapi import APIRouter, HTTPException, Query

from src.core.config import settings
from src.ors.client import ORSClient
from src.ors.exceptions import ORSHTTPError, ORSResponseError, ORSTimeoutError
from src.ors.schemas import VideoRatingPage

router = APIRouter()


@router.get("", response_model=VideoRatingPage)
async def get_video_ratings(
    company_name: str = Query(..., description="신청인(법인)명"),
    start_date: date | None = Query(None, description="시작 날짜"),
    end_date: date | None = Query(None, description="종료 날짜"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(100, ge=1, le=1000, description="페이지 크기"),
) -> VideoRatingPage:
    """비디오물 등급분류정보를 조회"""
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400, detail="start_date must be less than or equal to end_date."
        )
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
