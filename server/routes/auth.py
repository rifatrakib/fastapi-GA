from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from server.database.managers import get_cached_data
from server.database.users.auth import (
    activate_user_account,
    authenticate_user,
    create_user_account,
    read_user_by_email,
)
from server.schemas.base import MessageResponseSchema
from server.schemas.inc.auth import LoginRequestSchema, SignupRequestSchema
from server.schemas.out.auth import TokenResponseSchema
from server.security.dependencies import (
    email_form_field,
    get_database_session,
    login_form,
    signup_form,
)
from server.security.token import create_jwt
from server.utils.email import send_activation_mail
from server.utils.enums import Tags

router = APIRouter(prefix="/auth", tags=[Tags.authentication])


@router.post(
    "/signup",
    summary="Register new user",
    description="Register a new user account.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: Request,
    task_queue: BackgroundTasks,
    payload: SignupRequestSchema = Depends(signup_form),
    session: AsyncSession = Depends(get_database_session),
) -> MessageResponseSchema:
    new_user = await create_user_account(session=session, payload=payload)
    task_queue.add_task(send_activation_mail, request, new_user)
    return {"msg": "User account created. Check your email to activate your account."}


@router.post(
    "/login",
    summary="Authenticate user",
    description="Authenticate a user account.",
    response_model=TokenResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
async def login(
    payload: LoginRequestSchema = Depends(login_form),
    session: AsyncSession = Depends(get_database_session),
) -> TokenResponseSchema:
    try:
        user = await authenticate_user(
            session=session,
            username=payload.username,
            password=payload.password,
        )

        token = create_jwt(user)
        return {"access_token": token, "token_type": "Bearer"}
    except HTTPException as e:
        raise e


@router.get(
    "/activate",
    summary="Activate user account",
    description="Activate a user account.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def activate_account(
    token: str = Query(title="Activation token", description="Activation token sent to user email."),
    session: AsyncSession = Depends(get_database_session),
) -> MessageResponseSchema:
    user = get_cached_data(key=token)
    updated_user = await activate_user_account(session=session, user_id=user["user_id"])
    return {"msg": f"User account {updated_user.username} activated."}


@router.post(
    "/activate/resend",
    summary="Resend activation key",
    description="Resend activation key to a user.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def resend_activation_key(
    request: Request,
    task_queue: BackgroundTasks,
    email: EmailStr = Depends(email_form_field),
    session: AsyncSession = Depends(get_database_session),
):
    try:
        user = await read_user_by_email(session=session, email=email)
        task_queue.add_task(send_activation_mail, request, user)
        return {"msg": "Activation key sent."}
    except HTTPException as e:
        raise e
