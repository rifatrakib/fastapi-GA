from fastapi import APIRouter, status

from server.database.users.auth import create_user_account
from server.schemas.inc.auth import SignupSchema
from server.utils.enums import Tags

router = APIRouter(prefix="/auth", tags=[Tags.authentication])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def register(payload: SignupSchema):
    new_user = create_user_account(payload)
    return new_user.dict()
