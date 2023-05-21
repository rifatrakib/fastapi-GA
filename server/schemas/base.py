from typing import Any

from pydantic import BaseModel

from server.utils.formatters import format_dict_key_to_camel_case


class BaseTokenAPISchema(BaseModel):
    class Config:
        allow_population_by_field_name: bool = True


class BaseAPISchema(BaseTokenAPISchema):
    class Config:
        orm_mode: bool = True
        alias_generator: Any = format_dict_key_to_camel_case
