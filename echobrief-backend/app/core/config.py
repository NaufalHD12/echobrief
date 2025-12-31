from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PGUSER: str = ""
    PGHOST: str = ""
    PGPASSWORD: str = ""
    PGDATABASE: str = ""
    PGPORT: int = 5432

    REDIS_HOST: str = ""
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = ""

    AUDIO_STORAGE_URL: str = ""

    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = ""

    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=False, extra="ignore"
    )

    @computed_field
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.PGUSER}:{self.PGPASSWORD}@{self.PGHOST}:{self.PGPORT}/{self.PGDATABASE}"

    @computed_field
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


settings = Settings()
