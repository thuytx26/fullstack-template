from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env"
    )
    PROJECT_NAME: str = 'FastAPI'
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(..., min_length=32)
    ACCESS_TOKEN_EXPIRE_MINUTES : int = 15

    # db
    database_parent_directory: str = "/mnt/c/Users/ASUS/Documents"
    database_name: str = "database.db"

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        database_url = f"sqlite:///{self.database_parent_directory}/{self.database_name}"
        return database_url


    # first superuser
    FIRST_SUPERUSER_NAME: str = Field(max_length=255)
    FIRST_SUPERUSER_PASSWORD: str = Field(min_length=8, max_length=40)

    TEST_NORMAL_USER_NAME: str = "testuser"

settings = Settings()