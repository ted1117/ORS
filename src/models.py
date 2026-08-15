from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class VideoRating(Base):
    __tablename__ = "video_ratings"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(Text, nullable=False)
    original_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    rating_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )
    rating_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    grade: Mapped[str] = mapped_column(Text, nullable=False)

    applicant_name: Mapped[str] = mapped_column(Text, nullable=False)
    producer_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    production_country: Mapped[str | None] = mapped_column(Text, nullable=True)
    production_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    kind: Mapped[str | None] = mapped_column(Text, nullable=True)
    running_time: Mapped[str | None] = mapped_column(Text, nullable=True)

    director_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    lead_actor_name: Mapped[str | None] = mapped_column(Text, nullable=True)

    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    core_harm_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
