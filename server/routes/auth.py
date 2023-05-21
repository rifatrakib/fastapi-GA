from fastapi import APIRouter, status

from server.schemas.inc.auth import SignupSchema
from server.utils.enums import Tags

router = APIRouter(prefix="/auth", tags=[Tags.authentication])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def register(payload: SignupSchema):
    return {"message": "User created successfully."}
