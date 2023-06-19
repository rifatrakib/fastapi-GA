from sqlmodel import Session, select

from server.models.schemas.users import UserAccount
from server.schemas.inc.auth import SignupRequestSchema
from server.security.authentication import pwd_context
from server.utils.messages import raise_401_unauthorized, raise_403_forbidden, raise_404_not_found


def create_user_account(session: Session, payload: SignupRequestSchema) -> UserAccount:
    hashed_password = pwd_context.hash_plain_password(payload.password)
    user = UserAccount(
        username=payload.username,
        email=payload.email,
        hashed_password=hashed_password,
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def authenticate_user(session: Session, username: str, password: str) -> UserAccount:
    user = session.exec(select(UserAccount).where(UserAccount.username == username)).first()

    if not user:
        raise_404_not_found(message=f"The username {username} is not registered.")

    if not user.is_active:
        raise_403_forbidden(message=f"The account for username {username} is not activated.")

    if not pwd_context.verify_password(password, user.hashed_password):
        raise_401_unauthorized(message="Incorrect password.")

    return user


def activate_user_account(session: Session, user_id: int) -> UserAccount:
    user = session.get(UserAccount, user_id)
    user.is_active = True
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
