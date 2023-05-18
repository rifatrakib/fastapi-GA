from datetime import datetime

from pydantic import BaseModel

from server.utils.formatters import format_datetime_into_isoformat


class BaseModelConfig(BaseModel):
    class Config:
        use_enum_values = True
        validate_assignment = True
        allow_population_by_field_name: bool = True
        json_encoders: dict = {datetime: format_datetime_into_isoformat}
