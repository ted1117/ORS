from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import VideoRating as VideoRatingModel
from src.ors.schemas import VideoRating as VideoRatingSchema


class VideoRatingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert(self, rating: VideoRatingSchema) -> VideoRatingModel:
        """등급분류번호를 기준으로 등급분류정보를 저장하거나 갱신한다."""
        values = rating.model_dump()
        stmt = insert(VideoRatingModel).values(**values)

        update_values = {
            column.name: getattr(stmt.excluded, column.name)
            for column in VideoRatingModel.__table__.columns
            if column.name not in {"id", "rating_number", "created_at", "updated_at"}
        }
        update_values["updated_at"] = func.now()

        stmt = stmt.on_conflict_do_update(
            index_elements=[VideoRatingModel.rating_number],
            set_=update_values,
        ).returning(VideoRatingModel)

        try:
            result = await self.session.execute(
                stmt.execution_options(populate_existing=True)
            )
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

        return result.scalar_one()
