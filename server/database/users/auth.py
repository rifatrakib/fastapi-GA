from sqlmodel import Session, create_engine

from server.config.factory import settings
from server.models.schemas.users import UserAccount
from server.schemas.inc.auth import SignupSchema
from server.security.authentication import pwd_context


def create_user_account(payload: SignupSchema) -> UserAccount:
    engine = create_engine(settings.RDS_URI, echo=True)
    hashed_password = pwd_context.hash_plain_password(payload.password)
    user = UserAccount(
        username=payload.username,
        email=payload.email,
        hashed_password=hashed_password,
    )

    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)

    return user
