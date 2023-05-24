from typing import Any, Dict, List

from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from server.config.smtp import config_smtp_server, config_templates


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
    request: Request,
    recipients: List[EmailStr],
    subject: str,
    template_name: str,
) -> None:
    smtp_config: ConnectionConfig = config_smtp_server()
    smtp_agent = FastMail(smtp_config)
    message: MessageSchema = prepare_message(
        context={"request": request},
        recipients=recipients,
        subject=subject,
        template_name=template_name,
    )
    await smtp_agent.send_message(message)
