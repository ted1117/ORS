import json
from json import JSONDecodeError
from typing import Annotated, Self

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """ORS API, database, Celery 및 동기화 실행 설정을 제공한다."""

    ors_api_key: str
    ors_api_base_url: str
    ors_api_timeout: float = 10.0
    db_url: SecretStr

    celery_broker_url: str
    celery_result_backend: str
    celery_timezone: str = "Asia/Seoul"

    ors_sync_companies: Annotated[list[str], NoDecode] = Field(
        default_factory=list,
        max_length=5,
    )
    ors_sync_interval_seconds: int = Field(default=1200, gt=0)
    ors_sync_page_size: int = Field(default=1000, ge=1, le=1000)
    ors_sync_window_days: int = Field(default=2, gt=0)
    ors_sync_max_api_calls_per_day: int = Field(default=800, gt=0)

    celery_task_max_retries: int = Field(default=3, ge=0)
    celery_retry_backoff_max_seconds: int = Field(default=900, gt=0)
    celery_task_soft_time_limit: int = Field(default=900, gt=0)
    celery_task_time_limit: int = Field(default=1200, gt=0)
    celery_sync_lock_ttl_seconds: int = Field(default=1800, gt=0)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @field_validator("ors_sync_companies", mode="before")
    @classmethod
    def parse_sync_companies(cls, value: object) -> list[str]:
        """쉼표 구분 또는 JSON 배열 형식의 업체 목록을 파싱한다."""
        if isinstance(value, str):
            raw_value = value.strip()
            if not raw_value:
                return []
            try:
                value = json.loads(raw_value)
            except JSONDecodeError:
                value = raw_value.split(",")

        if not isinstance(value, (list, tuple)):
            raise ValueError(
                "ORS_SYNC_COMPANIES must be a list or comma-separated string"
            )

        companies: list[str] = []
        for company in value:
            if not isinstance(company, str):
                raise ValueError("ORS_SYNC_COMPANIES entries must be strings")
            company_name = company.strip()
            if company_name:
                companies.append(company_name)
        return companies

    @model_validator(mode="after")
    def validate_task_time_limits(self) -> Self:
        """soft limit이 hard limit보다 짧도록 검증한다."""
        if self.celery_task_soft_time_limit >= self.celery_task_time_limit:
            raise ValueError(
                "CELERY_TASK_SOFT_TIME_LIMIT must be less than hard time limit"
            )
        return self

    @property
    def sync_company_names(self) -> tuple[str, ...]:
        """동기화 대상 업체를 튜플로 반환하고 미설정 상태를 거부한다."""
        if not self.ors_sync_companies:
            raise ValueError("ORS_SYNC_COMPANIES must contain at least one company")
        return tuple(self.ors_sync_companies)


settings = Settings()  # type: ignore
