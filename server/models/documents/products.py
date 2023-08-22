from pymongo import TEXT

from server.models.base import BaseDocumentModel
from server.schemas.common.products import ProductBase, ShopBase


class ProductDocument(BaseDocumentModel, ProductBase):
    shop_id: str

    class Settings:
        name = "products"
        indexes = [
            "shop_id",
            [("name", TEXT)],
        ]


class ShopDocument(BaseDocumentModel, ShopBase):
    owner_id: int

    class Settings:
        name = "shops"
        indexes = [
            "owner_id",
            [("name", TEXT)],
        ]
