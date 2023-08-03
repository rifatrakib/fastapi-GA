from typing import Any, Dict, List

from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr, HttpUrl

from server.config.smtp import config_smtp_server, config_templates
from server.models.schemas.users import UserAccount
from server.utils.generators import create_temporary_activation_url


def build_mail_body(context: Dict[str, Any], template_name: str) -> str:
    template_server: Jinja2Templates = config_templates()
    template = template_server.TemplateResponse(
        name=template_name,
        context=context,
    )
    return template.body.decode("utf-8")


def prepare_message(
    context: Dict[str, Any],
    recipients: List[EmailStr],
    subject: str,
    template_name: str,
) -> MessageSchema:
    return MessageSchema(
        subject=subject,
        recipients=recipients,
        body=build_mail_body(context, template_name),
        subtype=MessageType.html,
    )


async def send_mail(
    context: Dict[str, Any],
    recipients: List[EmailStr],
    subject: str,
    template_name: str,
) -> None:
    smtp_config: ConnectionConfig = config_smtp_server()
    smtp_agent = FastMail(smtp_config)
    message: MessageSchema = prepare_message(
        context=context,
        recipients=recipients,
        subject=subject,
        template_name=template_name,
    )
    await smtp_agent.send_message(message)


async def send_activation_mail(
    request: Request,
    url: HttpUrl,
    user: UserAccount,
) -> None:
    url = create_temporary_activation_url(user=user, url=url)
    context = {
        "request": request,
        "subject": "Activate your account",
        "url": url,
        "username": user.username,
    }

    await send_mail(
        context=context,
        recipients=[user.email],
        subject="Activate your account",
        template_name="activation.html",
    )
