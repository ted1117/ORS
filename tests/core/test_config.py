import pytest
from pydantic import ValidationError

from src.core.config import Settings


def build_settings(**overrides: object) -> Settings:
    """환경 파일을 읽지 않고 테스트용 설정을 생성한다."""
    values: dict[str, object] = {
        "ors_api_key": "test-api-key",
        "ors_api_base_url": "https://example.test",
        "db_url": "postgresql+asyncpg://user:password@localhost/db",
        "celery_broker_url": "redis://test-broker:6379/0",
        "celery_result_backend": "redis://test-backend:6379/1",
        "_env_file": None,
    }
    values.update(overrides)
    return Settings(**values)


def test_sync_companies_accept_comma_separated_value() -> None:
    settings = build_settings(ors_sync_companies="company-a, company-b")

    assert settings.sync_company_names == ("company-a", "company-b")


def test_sync_companies_accept_json_array_value() -> None:
    settings = build_settings(ors_sync_companies='["company-a", "company-b"]')

    assert settings.sync_company_names == ("company-a", "company-b")


def test_sync_companies_load_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ORS_SYNC_COMPANIES", "company-a, company-b")

    settings = build_settings()

    assert settings.sync_company_names == ("company-a", "company-b")


def test_sync_companies_reject_more_than_five_companies() -> None:
    with pytest.raises(ValidationError, match="at most 5"):
        build_settings(ors_sync_companies="a,b,c,d,e,f")


def test_sync_company_names_reject_missing_configuration() -> None:
    settings = build_settings()

    with pytest.raises(ValueError, match="ORS_SYNC_COMPANIES"):
        _ = settings.sync_company_names


def test_task_soft_limit_must_be_less_than_hard_limit() -> None:
    with pytest.raises(ValidationError, match="SOFT_TIME_LIMIT"):
        build_settings(
            ors_sync_companies="company-a",
            celery_task_soft_time_limit=1200,
            celery_task_time_limit=1200,
        )


def test_prd_sync_defaults_are_loaded() -> None:
    settings = build_settings(ors_sync_companies="company-a")

    assert settings.celery_broker_url == "redis://test-broker:6379/0"
    assert settings.celery_result_backend == "redis://test-backend:6379/1"
    assert settings.celery_timezone == "Asia/Seoul"
    assert settings.ors_sync_interval_seconds == 1200
    assert settings.ors_sync_page_size == 1000
    assert settings.ors_sync_window_days == 2
    assert settings.ors_sync_max_api_calls_per_day == 800
    assert settings.celery_task_max_retries == 3
    assert settings.celery_retry_backoff_max_seconds == 900
    assert settings.celery_task_soft_time_limit == 900
    assert settings.celery_task_time_limit == 1200
    assert settings.celery_sync_lock_ttl_seconds == 1800
