from functools import lru_cache

from fastapi.templating import Jinja2Templates
from fastapi_mail import ConnectionConfig

from server.config.factory import settings


@lru_cache()
def config_smtp_server() -> ConnectionConfig:
    return ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=settings.USE_CREDENTIALS,
    )


@lru_cache()
def config_templates() -> Jinja2Templates:
    return Jinja2Templates(directory="server/templates")
