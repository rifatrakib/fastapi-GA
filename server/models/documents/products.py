from server.models.base import BaseDocumentModel
from server.schemas.common.products import ProductBase, ShopBase


class ProductDocument(BaseDocumentModel, ProductBase):
    shop_id: str

    class Settings:
        name = "products"
        indexes = ["name", "shop_id"]


class ShopDocument(BaseDocumentModel, ShopBase):
    owner_id: str

    class Settings:
        name = "shops"
        indexes = ["name", "owner_id"]
