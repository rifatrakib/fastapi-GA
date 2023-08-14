from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from server.database.users.auth import read_user_by_user_id
from server.schemas.out.users import UserResponse
from server.security.dependencies import get_database_session
from server.utils.enums import Tags

router = APIRouter(prefix="/users", tags=[Tags.users])


@router.get(
    "/{user_id}",
    summary="Get user by ID",
    description="Get user by ID.",
    response_model=UserResponse,
)
async def read_single_user(
    user_id: int,
    session: AsyncSession = Depends(get_database_session),
):
    try:
        user = await read_user_by_user_id(session=session, user_id=user_id)
        return user
    except HTTPException as e:
        raise e
