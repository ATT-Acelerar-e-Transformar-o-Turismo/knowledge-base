from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ORIGINS: str = Field(default="localhost", env="ORIGINS")
    MONGODB_URL: str = Field(
        default="mongodb://localhost:27017", env="MONGODB_URL"
    )
    DATABASE_NAME: str = Field(default="knowledge_base", env="DATABASE_NAME")

    MAX_FILE_SIZE_MB: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    UPLOAD_DIR: str = Field(default="app/uploads", env="UPLOAD_DIR")

    ALLOWED_IMAGE_TYPES: str = Field(
        default="image/jpeg,image/png,image/gif,image/webp",
        env="ALLOWED_IMAGE_TYPES"
    )
    ALLOWED_DOCUMENT_TYPES: str = Field(
        default="application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,text/plain,text/csv",
        env="ALLOWED_DOCUMENT_TYPES"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
