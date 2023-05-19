from typing import Union

from pydantic import BaseSettings, Extra, Field


class RootConfig(BaseSettings):
    class Config:
        env_file_encoding = "UTF-8"
        env_nested_delimiter = "__"
        extra = Extra.forbid


class BaseConfig(RootConfig):
    APP_NAME: str

    # SQL Database Configurations
    RDS_HOST: Union[str, None] = Field(default=None)
    RDS_PORT: Union[str, None] = Field(default=None)
    RDS_USER: Union[str, None] = Field(default=None)
    RDS_PASS: Union[str, None] = Field(default=None)
    RDS_NAME: Union[str, None] = Field(default=None)

    class Config:
        env_file = "configurations/.env"

    @property
    def RDS_URI(self) -> str:
        username = self.RDS_USER
        password = self.RDS_PASS
        host = self.RDS_HOST
        port = self.RDS_PORT
        db_name = self.RDS_NAME

        if not all([username, password, host, port, db_name]):
            return "sqlite:///database.db"
        return f"postgresql://{username}:{password}@{host}:{port}/{db_name}"
