from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status

from server.database.managers import get_cached_data
from server.database.users.auth import activate_user_account, authenticate_user, create_user_account
from server.schemas.base import MessageResponseSchema
from server.schemas.inc.auth import LoginRequestSchema, SignupRequestSchema
from server.schemas.out.auth import TokenResponseSchema
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
async def register(payload: SignupRequestSchema, request: Request, task_queue: BackgroundTasks):
    new_user = create_user_account(payload)
    task_queue.add_task(send_activation_mail, request, new_user)
    return {"msg": "User account created. Check your email to activate your account."}


@router.post(
    "/login",
    summary="Authenticate user",
    description="Authenticate a user account.",
    response_model=TokenResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
async def login(payload: LoginRequestSchema):
    try:
        user = authenticate_user(payload.username, payload.password)
        token = create_jwt(user)
        return {"access_token": token, "token_type": "Bearer"}
    except HTTPException as e:
        raise e


@router.get(
    "/activate/{token}",
    summary="Activate user account",
    description="Activate a user account.",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def activate_account(token: str):
    user = get_cached_data(key=token)
    updated_user = activate_user_account(user["user_id"])
    return {"msg": f"User account {updated_user.username} activated."}
