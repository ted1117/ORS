from datetime import date
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from src.main import app
from src.ors.schemas import VideoRating, VideoRatingPage

client = TestClient(app)


def test_get_video_ratings():
    """비디오물 등급분류정보를 조회한다."""

    mock_result = VideoRatingPage(
        items=[
            VideoRating(
                title="테스트 작품",
                original_title="Test Title",
                rating_number="2026-VF00001",
                rating_date=date(2026, 8, 14),
                grade="15세이상관람가",
                applicant_name="테스트 회사",
            )
        ],
        page=1,
        page_size=100,
        total_count=1,
    )

    with patch(
        "src.api.v1.ratings.ORSClient.fetch",
        new_callable=AsyncMock,
        return_value=mock_result,
    ) as mock_fetch:
        response = client.get(
            "/api/v1/video-ratings",
            params={
                "company_name": "테스트 회사",
                "start_date": "2026-08-01",
                "end_date": "2026-08-14",
                "page": 1,
                "page_size": 100,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["page_size"] == 100
    assert data["total_count"] == 1
    assert len(data["items"]) == 1

    assert data["items"][0]["title"] == "테스트 작품"
    assert data["items"][0]["rating_number"] == "2026-VF00001"
    assert data["items"][0]["rating_date"] == "2026-08-14"

    mock_fetch.assert_awaited_once_with(
        company_name="테스트 회사",
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 14),
        page=1,
        page_size=100,
    )


def test_get_video_ratings_with_invalid_date():
    """잘못된 날짜 형식이면 422를 반환한다."""

    response = client.get(
        "/api/v1/video-ratings",
        params={
            "company_name": "테스트 회사",
            "start_date": "20260801",
        },
    )

    assert response.status_code == 422
