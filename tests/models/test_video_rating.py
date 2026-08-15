from datetime import date

from sqlalchemy import inspect

from src.models import VideoRating


def test_video_rating_model_mapping():
    mapper = inspect(VideoRating)
    columns = mapper.columns

    assert VideoRating.__tablename__ == "video_ratings"
    assert columns.rating_number.unique is True
    assert columns.title.nullable is False
    assert columns.rating_date.nullable is True
    assert columns.production_year.nullable is True


def test_video_rating_accepts_optional_fields_as_none():
    rating = VideoRating(
        title="테스트 작품",
        rating_number="2026-VF00001",
        rating_date=date(2026, 8, 15),
        grade="15세이상관람가",
        applicant_name="테스트 회사",
        original_title=None,
        producer_name=None,
        production_country=None,
        production_year=None,
        kind=None,
        running_time=None,
        director_name=None,
        lead_actor_name=None,
        content=None,
        core_harm_reason=None,
    )

    assert rating.rating_number == "2026-VF00001"
    assert rating.content is None
