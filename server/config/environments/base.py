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
