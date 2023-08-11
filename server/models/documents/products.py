from server.models.base import BaseDocumentModel
from server.schemas.common.products import ProductBase


class ProductDocument(BaseDocumentModel, ProductBase):
    class Settings:
        name = "products"
        indexes = ["name"]
