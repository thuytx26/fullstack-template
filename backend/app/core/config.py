from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env")
    PROJECT_NAME: str = "FastAPI"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(..., min_length=32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    # db
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URL_OBJECT(self) -> URL:
        url_object = URL.create(
            "postgresql+psycopg2",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        )
        return url_object

    # first superuser
    FIRST_SUPERUSER_NAME: str = Field(max_length=255)
    FIRST_SUPERUSER_PASSWORD: str = Field(min_length=8, max_length=40)

    TEST_NORMAL_USER_NAME: str = "testuser"


settings = Settings()
