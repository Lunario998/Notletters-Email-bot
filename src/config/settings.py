from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    telegram_bot_token: str = Field(alias="TELEGRAM_BOT_TOKEN")
    notletters_api_key: str = Field(alias="NOTLETTERS_API_KEY")
    notletters_api_base_url: str = Field(
        default="https://api.notletters.com",
        alias="NOTLETTERS_API_BASE_URL",
    )
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    new_password: str = Field(default="ChangeMe123", alias="NEW_PASSWORD")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache(maxsize=1)
def get_settings():
    return Settings()
