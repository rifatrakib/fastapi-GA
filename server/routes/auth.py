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

from server.config.factory import settings
from server.database.managers import cache_data, pop_from_cache, validate_key
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
    authenticate_active_user,
    email_form_field,
    get_database_session,
    login_form,
    password_change_request_form,
    password_reset_request_form,
    signup_form,
    temporary_url_key,
)
from server.security.token import create_jwt
from server.utils.email import send_activation_mail
from server.utils.enums import Tags
from server.utils.generators import create_temporary_activation_url
from server.utils.messages import raise_410_gone

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
        cache_data(key=token, data=user.json(), ttl=settings.JWT_MIN * 60)
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
    validation_key: str = Depends(temporary_url_key),
    session: AsyncSession = Depends(get_database_session),
) -> MessageResponseSchema:
    user = pop_from_cache(key=validation_key)
    updated_user = await activate_user_account(session=session, user_id=user["id"])
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
    user: TokenUser = Depends(authenticate_active_user),
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


@router.options(
    "/password/reset",
    summary="Validate password reset link",
    description="Validate password reset link.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def validate_password_reset_link(
    validation_key: str = Query(
        ...,
        title="Validation key",
        description="Validation key included as query parameter in the link sent to user email.",
    ),
):
    try:
        if not validate_key(key=validation_key):
            raise_410_gone(message="Link expired!")
    except HTTPException as e:
        raise e


@router.patch(
    "/password/reset",
    summary="Verify email and reset password",
    description="Use secret key sent in mail to verify and reset password.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
async def reset_user_password(
    validation_key: str = Depends(temporary_url_key),
    new_password: str = Depends(password_reset_request_form),
    session: AsyncSession = Depends(get_database_session),
):
    try:
        user = pop_from_cache(key=validation_key)
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
    user: TokenUser = Depends(authenticate_active_user),
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


@router.options(
    "/update/email",
    summary="Validate email change link",
    description="Validate email change link.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def validate_email_change_link(validation_key: str = Depends(temporary_url_key)):
    try:
        if not validate_key(key=validation_key):
            raise_410_gone(message="Link expired!")
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
    validation_key: str = Depends(temporary_url_key),
    session: AsyncSession = Depends(get_database_session),
):
    try:
        user = pop_from_cache(key=validation_key)
        await update_email(
            session=session,
            account_id=user["account_id"],
            new_email=user["new_email"],
        )
        return MessageResponseSchema(msg="Email was changed successfully!")
    except HTTPException as e:
        raise e
