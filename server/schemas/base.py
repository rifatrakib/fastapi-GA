from typing import Any, Union

from pydantic import BaseModel, Extra, validator

from server.utils.formatters import format_dict_key_to_camel_case


class BaseTokenAPISchema(BaseModel):
    class Config:
        allow_population_by_field_name: bool = True


class BaseAPISchema(BaseTokenAPISchema):
    class Config:
        orm_mode: bool = True
        alias_generator: Any = format_dict_key_to_camel_case


class BaseRequestSchema(BaseAPISchema):
    class Config:
        extra = Extra.forbid


class BaseResponseSchema(BaseAPISchema):
    id: Union[str, None] = None

    @validator("id", pre=True)
    def convert_id(cls, v):
        return str(v) if v else None
