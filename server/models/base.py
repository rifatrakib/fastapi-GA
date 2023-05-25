from datetime import datetime
from importlib import import_module
from typing import List, Union

from beanie import Document
from pydantic import BaseModel, validator
from sqlmodel import Field, SQLModel

from server.utils.formatters import format_datetime_into_isoformat


class BaseModelConfig(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated_at: Union[datetime, None] = Field(default=None)

    class Config:
        use_enum_values = True
        validate_assignment = True
        allow_population_by_field_name: bool = True
        json_encoders: dict = {datetime: format_datetime_into_isoformat}


class BaseSQLTable(SQLModel, BaseModelConfig):
    id: int = Field(index=True, primary_key=True)

    def update(self):
        self.last_updated_at = datetime.utcnow()
        return super().update()


class BaseDocumentModel(Document, BaseModelConfig):
    async def save(self):
        if self.id:
            self.last_updated_at = datetime.utcnow()
        return await super().save()


class MapperSchema(BaseModel):
    database_name: str
    model_paths: List[str]

    @validator("model_paths")
    def validate_model_paths(cls, value):
        for path in value:
            try:
                module_name, class_name = path.rsplit(".", 1)
                module = import_module(module_name)
                _ = getattr(module, class_name)
            except (ValueError, ImportError, AttributeError):
                raise ValueError(f"Invalid class path: {path}")
        return value
