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
    reset_password,
    update_email,
    update_password,
)
from server.schemas.base import MessageResponseSchema
from server.schemas.inc.auth import (
    LoginRequestSchema,
    PasswordChangeRequestSchema,
    SignupRequestSchema,
)
from server.schemas.out.auth import TokenResponseSchema, TokenUser
from server.security.dependencies import (
    email_form_field,
    get_database_session,
    is_user_active,
    login_form,
    password_change_request_form,
    password_reset_request_form,
    signup_form,
)
from server.security.token import create_jwt
from server.utils.email import send_activation_mail
from server.utils.enums import Tags
from server.utils.generators import create_temporary_activation_url

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
    url = create_temporary_activation_url(new_user, f"{request.base_url}auth/activate")

    task_queue.add_task(
        send_activation_mail,
        request,
        f"Account activation for {new_user.username}",
        "activation",
        url,
        new_user,
    )

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


@router.patch(
    "/password/change",
    summary="Change user password",
    description="Change a user's password.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def change_password(
    user: TokenUser = Depends(is_user_active),
    payload: PasswordChangeRequestSchema = Depends(password_change_request_form),
    session: AsyncSession = Depends(get_database_session),
) -> MessageResponseSchema:
    try:
        await update_password(session=session, user_id=user.id, payload=payload)
        return {"msg": "Password changed."}
    except HTTPException as e:
        raise e


@router.post(
    "/password/forgot",
    summary="Forgot password",
    description="Send password reset link to user.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def forgot_password(
    request: Request,
    task_queue: BackgroundTasks,
    email: EmailStr = Depends(email_form_field),
    session: AsyncSession = Depends(get_database_session),
) -> MessageResponseSchema:
    try:
        user = await read_user_by_email(session=session, email=email)
        url = create_temporary_activation_url(user, f"{request.base_url}auth/password/reset")

        task_queue.add_task(
            send_activation_mail,
            request,
            f"Password reset requested by {user.username}",
            "password-reset",
            url,
            user,
        )

        return {"msg": "Please check your email for the temporary password reset link."}
    except HTTPException as e:
        raise e


@router.patch(
    "/password/reset",
    name="account:reset-password",
    summary="Use secret key sent in mail to verify and reset password",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
async def reset_user_password(
    validation_key: str = Query(
        ...,
        title="Validation key",
        description="Validation key included as query parameter in the link sent to user email.",
    ),
    new_password: str = Depends(password_reset_request_form),
    session: AsyncSession = Depends(get_database_session),
):
    try:
        user = get_cached_data(key=validation_key)
        await reset_password(
            session=session,
            account_id=user["account_id"],
            new_password=new_password,
        )
        return MessageResponseSchema(msg="Password was reset successfully!")
    except HTTPException as e:
        raise e


@router.post(
    "/update/email",
    summary="Request email change",
    description="Send email change link to user.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def request_email_change(
    request: Request,
    task_queue: BackgroundTasks,
    user: TokenUser = Depends(is_user_active),
    new_email: EmailStr = Depends(email_form_field),
) -> MessageResponseSchema:
    try:
        url = create_temporary_activation_url(
            user,
            f"{request.base_url}auth/update/email",
            extras={"new_email": new_email},
        )

        task_queue.add_task(
            send_activation_mail,
            request,
            f"Change email requested by {user.username}",
            "change-email",
            url,
            user,
        )

        return {"msg": "Please check your email for the temporary email change link."}
    except HTTPException as e:
        raise e


@router.patch(
    "/update/email",
    summary="Change user email",
    description="Change a user's email.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
async def change_user_email(
    validation_key: str = Query(
        ...,
        title="Validation key",
        description="Validation key included as query parameter in the link sent to user email.",
    ),
    session: AsyncSession = Depends(get_database_session),
):
    try:
        user = get_cached_data(key=validation_key)
        await update_email(
            session=session,
            account_id=user["account_id"],
            new_email=user["new_email"],
        )
        return MessageResponseSchema(msg="Email was changed successfully!")
    except HTTPException as e:
        raise e
