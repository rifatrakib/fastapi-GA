from server.schemas.base import BaseResponseSchema
from server.schemas.common.users import UserBase


class UserResponse(BaseResponseSchema, UserBase):
    pass
