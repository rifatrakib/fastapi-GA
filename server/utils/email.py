import json
from datetime import timedelta
from typing import Any, Dict, List

from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from server.config.smtp import config_smtp_server, config_templates
from server.database.managers import cache_data
from server.models.schemas.users import UserAccount
from server.utils.generators import generate_account_validation_token


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
    user: UserAccount,
) -> None:
    key = generate_account_validation_token()
    url = f"{request.base_url}auth/activate/{key}"
    context = {
        "request": request,
        "subject": "Activate your account",
        "url": url,
        "username": user.username,
    }

    cache_data(
        key=key,
        data=json.dumps({"user_id": str(user.id)}),
        ttl=timedelta(minutes=5).seconds,
    )

    await send_mail(
        context=context,
        recipients=[user.email],
        subject="Activate your account",
        template_name="activation.html",
    )
    print(f"Activation email sent to {user.email}")
