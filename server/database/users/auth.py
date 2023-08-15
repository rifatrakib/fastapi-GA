from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from server.models.schemas.users import UserAccount
from server.schemas.inc.auth import PasswordChangeRequestSchema, SignupRequestSchema
from server.security.authentication import pwd_context
from server.utils.messages import (
    raise_401_unauthorized,
    raise_403_forbidden,
    raise_404_not_found,
)


async def create_user_account(session: AsyncSession, payload: SignupRequestSchema) -> UserAccount:
    hashed_password = pwd_context.hash_plain_password(payload.password)
    user = UserAccount(
        username=payload.username,
        email=payload.email,
        hashed_password=hashed_password,
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


async def authenticate_user(session: AsyncSession, username: str, password: str) -> UserAccount:
    stmt = select(UserAccount).where(UserAccount.username == username)
    query = await session.execute(stmt)
    user = query.scalar()

    if not user:
        raise_404_not_found(message=f"The username {username} is not registered.")

    if not user.is_active:
        raise_403_forbidden(message=f"The account for username {username} is not activated.")

    if not pwd_context.verify_password(password, user.hashed_password):
        raise_401_unauthorized(message="Incorrect password.")

    return user


async def activate_user_account(session: AsyncSession, user_id: int) -> UserAccount:
    user = await session.get(UserAccount, user_id)
    user.is_active = True
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def read_user_by_email(session: AsyncSession, email: EmailStr) -> UserAccount:
    stmt = select(UserAccount).where(UserAccount.email == email)
    query = await session.execute(stmt)
    user = query.scalar()

    if not user:
        raise_404_not_found(message=f"The email {email} is not registered.")

    return user


async def update_password(
    session: AsyncSession,
    user_id: int,
    payload: PasswordChangeRequestSchema,
):
    stmt = select(UserAccount).where(UserAccount.id == user_id)
    query = await session.execute(stmt)
    user = query.scalar()

    if not pwd_context.verify_password(payload.current_password, user.hashed_password):
        raise_401_unauthorized(message="Incorrect password.")

    user.hashed_password = pwd_context.hash_plain_password(payload.new_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)


async def reset_password(
    session: AsyncSession,
    user_id: int,
    new_password: str,
):
    stmt = select(UserAccount).where(UserAccount.id == user_id)
    query = await session.execute(stmt)
    user = query.scalar()

    user.hashed_password = pwd_context.hash_plain_password(new_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)


async def update_email(
    session: AsyncSession,
    user_id: int,
    new_email: EmailStr,
):
    stmt = select(UserAccount).where(UserAccount.id == user_id)
    query = await session.execute(stmt)
    user = query.scalar()

    user.email = new_email
    session.add(user)
    await session.commit()
    await session.refresh(user)


async def read_user_by_user_id(session: AsyncSession, user_id: int) -> UserAccount:
    stmt = select(UserAccount).where(UserAccount.id == user_id)
    query = await session.execute(stmt)
    user = query.scalar()

    if not user:
        raise_404_not_found(message=f"The user ID {user_id} is not registered.")

    return user
