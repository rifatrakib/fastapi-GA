from fastapi import Depends, Form
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from server.config.factory import settings
from server.schemas.inc.auth import LoginRequestSchema, SignupRequestSchema


def get_async_database_session():
    url = settings.RDS_URI
    engine = create_async_engine(url)
    SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    return SessionLocal()


async def get_database_session() -> AsyncSession:
    try:
        session: AsyncSession = get_async_database_session()
        yield session
    finally:
        await session.close()


def username_form_field(
    username: str = Form(
        title="username",
        description="Username of the user to login.",
        min_length=1,
        max_length=64,
    ),
):
    return username


def email_form_field(
    email: EmailStr = Form(
        title="email",
        decription="Unique email that can be used for user account activation.",
    ),
):
    return email


def password_form_field(
    password: str = Form(
        title="password",
        description="Password of the user to login.",
        min_length=1,
        max_length=64,
    )
):
    return password


def signup_form(
    username: str = Depends(username_form_field),
    email: EmailStr = Depends(email_form_field),
    password: str = Depends(password_form_field),
):
    return SignupRequestSchema(username=username, email=email, password=password)


def login_form(
    username: str = Depends(username_form_field),
    password: str = Depends(password_form_field),
):
    return LoginRequestSchema(username=username, password=password)
