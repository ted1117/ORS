from datetime import date

from pydantic import BaseModel


class VideoRating(BaseModel):
    title: str
    original_title: str | None = None
    rating_number: str
    rating_date: date | None = None
    grade: str

    applicant_name: str
    producer_name: str | None = None
    production_country: str | None = None
    production_year: int | None = None

    kind: str | None = None
    running_time: str | None = None

    director_name: str | None = None
    lead_actor_name: str | None = None

    content: str | None = None
    core_harm_reason: str | None = None


class VideoRatingPage(BaseModel):
    items: list[VideoRating]
    page: int
    page_size: int
    total_count: int
