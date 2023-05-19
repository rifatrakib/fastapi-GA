from pydantic import Field

from server.models.base import BaseDocumentModel


class ProductDocument(BaseDocumentModel):
    name: str = Field(..., title="Product name")
    description: str = Field(..., title="Product description")
    price: float = Field(..., title="Product price")

    class Settings:
        name = "products"
        indexes = ["name"]
