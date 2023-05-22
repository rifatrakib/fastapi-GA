from fastapi import APIRouter, status

from server.database.users.auth import authenticate_user, create_user_account
from server.schemas.inc.auth import LoginRequestSchema, SignupRequestSchema
from server.schemas.out.auth import SignupResponseSchema
from server.security.token import create_jwt
from server.utils.enums import Tags

router = APIRouter(prefix="/auth", tags=[Tags.authentication])


@router.post(
    "/signup",
    summary="Register new user",
    description="Register a new user account.",
    response_model=SignupResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register(payload: SignupRequestSchema):
    new_user = create_user_account(payload)
    token = create_jwt(new_user)
    return {"access_token": token, "token_type": "Bearer"}


@router.post(
    "/login",
    summary="Authenticate user",
    description="Authenticate a user account.",
    response_model=SignupResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
async def login(payload: LoginRequestSchema):
    user = authenticate_user(payload.username, payload.password)
    token = create_jwt(user)
    return {"access_token": token, "token_type": "Bearer"}
