from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ors_api_key: str
    ors_api_base_url: str
    ors_api_timeout: float = 10.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
