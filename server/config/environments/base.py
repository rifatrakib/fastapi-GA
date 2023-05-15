from pydantic import BaseSettings, Extra


class RootConfig(BaseSettings):
    class Config:
        env_file_encoding = "UTF-8"
        env_nested_delimiter = "__"
        extra = Extra.forbid


class BaseConfig(RootConfig):
    APP_NAME: str

    class Config:
        env_file = "configurations/.env"
