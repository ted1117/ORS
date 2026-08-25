import os
from collections.abc import AsyncIterator
from uuid import uuid4

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.models import VideoRating as VideoRatingModel
from src.ors.schemas import VideoRating as VideoRatingSchema
from src.repositories import VideoRatingRepository

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


@pytest.fixture
async def postgres_session_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    db_url = os.getenv("TEST_DB_URL")
    if db_url is None:
        pytest.skip("TEST_DB_URL is required for PostgreSQL integration tests")

    engine = create_async_engine(db_url, pool_pre_ping=True)
    try:
        yield async_sessionmaker(engine, expire_on_commit=False)
    finally:
        await engine.dispose()


def make_rating(*, rating_number: str, title: str) -> VideoRatingSchema:
    return VideoRatingSchema(
        title=title,
        rating_number=rating_number,
        grade="15세이상관람가",
        applicant_name="통합 테스트 회사",
    )


async def test_upsert_persists_none_and_updates_existing_row(
    postgres_session_factory: async_sessionmaker[AsyncSession],
):
    rating_number = f"TEST-PRD002-{uuid4().hex}"
    record_created = False

    try:
        async with postgres_session_factory() as session:
            inserted = await VideoRatingRepository(session).upsert(
                make_rating(rating_number=rating_number, title="최초 작품명")
            )
            inserted_id = inserted.id
            record_created = True

        async with postgres_session_factory() as session:
            stored = await session.scalar(
                select(VideoRatingModel).where(
                    VideoRatingModel.rating_number == rating_number
                )
            )

            assert stored is not None
            assert stored.original_title is None
            assert stored.rating_date is None
            assert stored.production_year is None
            assert stored.core_harm_reason is None

        async with postgres_session_factory() as session:
            updated = await VideoRatingRepository(session).upsert(
                make_rating(rating_number=rating_number, title="수정된 작품명")
            )

            assert updated.id == inserted_id

        async with postgres_session_factory() as session:
            count = await session.scalar(
                select(func.count())
                .select_from(VideoRatingModel)
                .where(VideoRatingModel.rating_number == rating_number)
            )
            stored = await session.scalar(
                select(VideoRatingModel).where(
                    VideoRatingModel.rating_number == rating_number
                )
            )

            assert count == 1
            assert stored is not None
            assert stored.id == inserted_id
            assert stored.title == "수정된 작품명"
    finally:
        if record_created:
            async with postgres_session_factory() as session:
                await session.execute(
                    delete(VideoRatingModel).where(
                        VideoRatingModel.rating_number == rating_number
                    )
                )
                await session.commit()


async def test_upsert_rolls_back_real_database_error(
    postgres_session_factory: async_sessionmaker[AsyncSession],
):
    async with postgres_session_factory() as session:
        with pytest.raises(DBAPIError):
            await VideoRatingRepository(session).upsert(
                make_rating(rating_number="X" * 101, title="저장 실패 작품")
            )

        assert await session.scalar(select(1)) == 1
