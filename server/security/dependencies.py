from fastapi import Depends, Form, Query
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from server.config.factory import settings
from server.database.managers import read_from_cache
from server.schemas.inc.auth import (
    LoginRequestSchema,
    PasswordChangeRequestSchema,
    SignupRequestSchema,
)
from server.schemas.out.auth import TokenUser
from server.security.token import decode_jwt
from server.utils.messages import raise_401_unauthorized, raise_422_unprocessable_entity

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_async_database_session() -> AsyncSession:
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


def is_user_active(token: str = Depends(oauth2_scheme)) -> TokenUser:
    user = read_from_cache(key=token)
    if user["is_active"]:
        return token

    raise_401_unauthorized("Inactive user")


def authenticate_active_user(token: str = Depends(is_user_active)) -> TokenUser:
    try:
        user_data: TokenUser = decode_jwt(token)
        return user_data
    except ValueError:
        raise_401_unauthorized("Invalid token")


def temporary_url_key(
    validation_key: str = Query(
        ...,
        title="Validation key",
        description="Validation key included as query parameter in the link sent to user email.",
    ),
) -> str:
    return validation_key


def username_form_field(
    username: str = Form(
        title="username",
        description="Username of the user to login.",
        min_length=1,
        max_length=64,
    ),
) -> str:
    return username


def email_form_field(
    email: EmailStr = Form(
        title="email",
        decription="Unique email that can be used for user account activation.",
    ),
) -> EmailStr:
    return email


def password_form_field(
    password: str = Form(
        alias="password",
        title="Password",
        decription="""
            Password containing at least 1 uppercase letter, 1 lowercase letter,
            1 number, 1 character that is neither letter nor number, and
            between 8 to 64 characters.
        """.replace("\n", " ").strip(),
        regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,64}$",
        min_length=8,
        max_length=64,
        example="Admin@12345",
    )
) -> str:
    return password


def repeat_password_form_field(
    repeat_password: str = Form(
        alias="repeatPassword",
        title="Repeat password",
        description="Repeat password to confirm password.",
        example="Admin@12345",
    ),
) -> str:
    return repeat_password


def new_password_form_field(
    new_password: str = Form(
        alias="newPassword",
        title="New password",
        decription="""
            Password containing at least 1 uppercase letter, 1 lowercase letter,
            1 number, 1 character that is neither letter nor number, and
            between 8 to 64 characters.
        """.replace("\n", " ").strip(),
        regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,64}$",
        min_length=8,
        max_length=64,
        example="Admin@12345",
    )
) -> str:
    return new_password


def signup_form(
    username: str = Depends(username_form_field),
    email: EmailStr = Depends(email_form_field),
    password: str = Depends(password_form_field),
    repeat_password: str = Depends(repeat_password_form_field),
) -> SignupRequestSchema:
    if password != repeat_password:
        raise_422_unprocessable_entity("Passwords do not match.")
    return SignupRequestSchema(username=username, email=email, password=password)


def login_form(
    username: str = Depends(username_form_field),
    password: str = Depends(password_form_field),
) -> LoginRequestSchema:
    return LoginRequestSchema(username=username, password=password)


def password_change_request_form(
    current_password: str = Depends(password_form_field),
    new_password: str = Depends(new_password_form_field),
    repeat_password: str = Depends(repeat_password_form_field),
) -> PasswordChangeRequestSchema:
    if new_password != repeat_password:
        raise_422_unprocessable_entity("Passwords do not match.")
    return PasswordChangeRequestSchema(current_password=current_password, new_password=new_password)


def password_reset_request_form(
    new_password: str = Depends(new_password_form_field),
    repeat_password: str = Depends(repeat_password_form_field),
) -> str:
    if new_password != repeat_password:
        raise_422_unprocessable_entity("Passwords do not match.")
    return new_password
