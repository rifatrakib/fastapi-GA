from server.models.base import BaseDocumentModel
from server.schemas.common.products import ProductBase, ShopBase


class ProductDocument(BaseDocumentModel, ProductBase):
    class Settings:
        name = "products"
        indexes = ["name"]


class ShopDocument(BaseDocumentModel, ShopBase):
    class Settings:
        name = "shops"
        indexes = ["name"]
