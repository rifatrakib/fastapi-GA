from server.models.documents.products import ProductDocument, ShopDocument
from server.schemas.base import BaseResponseSchema


class ProductResponse(BaseResponseSchema, ProductDocument):
    pass


class ShopResponse(BaseResponseSchema, ShopDocument):
    pass
