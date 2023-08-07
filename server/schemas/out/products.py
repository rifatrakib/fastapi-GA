from server.models.documents.products import ProductDocument
from server.schemas.base import BaseResponseSchema


class ProductResponse(BaseResponseSchema, ProductDocument):
    pass
