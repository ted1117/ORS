from datetime import date

from pydantic import BaseModel, Field


class VideoRating(BaseModel):
    title: str = Field(description="사용 제목")
    original_title: str | None = Field(default=None, description="원제")
    rating_number: str = Field(description="등급분류번호")
    rating_date: date | None = Field(default=None, description="등급분류일")
    grade: str = Field(description="등급분류 결과")

    applicant_name: str = Field(description="신청사명")
    producer_name: str | None = Field(default=None, description="제작사명")
    production_country: str | None = Field(default=None, description="제작 국가")
    production_year: int | None = Field(default=None, description="제작 연도")

    kind: str | None = Field(default=None, description="종류")
    running_time: str | None = Field(default=None, description="상영 시간")

    director_name: str | None = Field(default=None, description="감독명")
    lead_actor_name: str | None = Field(default=None, description="주연 배우명")

    content: str | None = Field(default=None, description="내용 정보")
    core_harm_reason: str | None = Field(
        default=None,
        description="핵심 유해 요소",
    )


class VideoRatingPage(BaseModel):
    items: list[VideoRating] = Field(description="등급분류 정보 목록")
    page: int = Field(description="페이지 번호")
    page_size: int = Field(description="페이지당 결과 수")
    total_count: int = Field(description="전체 결과 수")
