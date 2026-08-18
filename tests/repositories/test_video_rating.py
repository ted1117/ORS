from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.dialects.postgresql import dialect
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import VideoRating as VideoRatingModel
from src.ors.schemas import VideoRating as VideoRatingSchema
from src.repositories import VideoRatingRepository


def make_rating(**overrides: object) -> VideoRatingSchema:
    values: dict[str, object] = {
        "title": "테스트 작품",
        "original_title": "Test Title",
        "rating_number": "2026-VF00001",
        "rating_date": date(2026, 8, 15),
        "grade": "15세이상관람가",
        "applicant_name": "테스트 회사",
        "producer_name": "테스트 제작사",
        "production_country": "대한민국",
        "production_year": 2026,
        "kind": "영화",
        "running_time": "120분",
        "director_name": "테스트 감독",
        "lead_actor_name": "테스트 배우",
        "content": "테스트 내용",
        "core_harm_reason": "없음",
    }
    values.update(overrides)
    return VideoRatingSchema.model_validate(values)


@pytest.fixture
def session() -> AsyncMock:
    """공통 Given: AsyncSession을 흉내내는 Mock 세션"""
    return AsyncMock(spec=AsyncSession)


@pytest.mark.asyncio
async def test_upsert_inserts_or_updates_by_rating_number(session: AsyncMock):
    # Given
    saved_rating = VideoRatingModel(
        title="테스트 작품",
        rating_number="2026-VF00001",
        grade="15세이상관람가",
        applicant_name="테스트 회사",
    )
    result = MagicMock()
    result.scalar_one.return_value = saved_rating
    session.execute.return_value = result

    # When
    saved = await VideoRatingRepository(session).upsert(make_rating())

    # Then
    statement = session.execute.await_args.args[0]
    compiled = str(statement.compile(dialect=dialect()))

    assert saved is saved_rating
    assert "ON CONFLICT (rating_number) DO UPDATE" in compiled
    session.commit.assert_awaited_once()
    session.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_upsert_rolls_back_when_save_fails(session: AsyncMock):
    # Given
    session.execute.side_effect = RuntimeError("database error")

    # When & Then
    with pytest.raises(RuntimeError, match="database error"):
        await VideoRatingRepository(session).upsert(make_rating())

    session.rollback.assert_awaited_once()
    session.commit.assert_not_awaited()