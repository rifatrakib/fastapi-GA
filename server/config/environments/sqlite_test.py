from server.config.environments.base import BaseConfig


class SQLiteTestConfig(BaseConfig):
    DEBUG: bool = True
    MODE: str = "sqlite-test"

    class Config:
        env_file = "configurations/.env.sqlite"
