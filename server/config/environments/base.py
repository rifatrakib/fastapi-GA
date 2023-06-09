from typing import Union

from pydantic import BaseSettings, EmailStr, Extra, Field


class RootConfig(BaseSettings):
    class Config:
        env_file_encoding = "UTF-8"
        env_nested_delimiter = "__"
        extra = Extra.forbid


class BaseConfig(RootConfig):
    APP_NAME: str

    # SQL Database Configurations
    POSTGRES_HOST: Union[str, None] = Field(default=None)
    POSTGRES_PORT: Union[str, None] = Field(default=None)
    POSTGRES_USER: Union[str, None] = Field(default=None)
    POSTGRES_PASSWORD: Union[str, None] = Field(default=None)
    POSTGRES_DB: Union[str, None] = Field(default=None)

    # MongoDB Configurations
    MONGO_URI: str

    # Cache Servers Configurations
    REDIS_HOST: str
    REDIS_PORT: int

    # JWT Configurations
    JWT_SECRET_KEY: str
    JWT_SUBJECT: str
    JWT_ALGORITHM: str
    JWT_MIN: int
    JWT_HOUR: int
    JWT_DAY: int

    # SMTP Configurations
    MAIL_USERNAME: Union[EmailStr, str]
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    USE_CREDENTIALS: bool

    class Config:
        env_file = "configurations/.env"

    @property
    def RDS_URI_SYNC(self) -> str:
        username = self.POSTGRES_USER
        password = self.POSTGRES_PASSWORD
        host = self.POSTGRES_HOST
        port = self.POSTGRES_PORT
        db_name = self.POSTGRES_DB
        return f"postgresql://{username}:{password}@{host}:{port}/{db_name}"

    @property
    def RDS_URI(self) -> str:
        uri = self.RDS_URI_SYNC
        return uri.replace("postgresql://", "postgresql+asyncpg://")
