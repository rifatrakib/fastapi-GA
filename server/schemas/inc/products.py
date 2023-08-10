from server.schemas.common.products import ProductBase


class ProductRequest(ProductBase):
    class Config:
        schema_extra = {
            "example": {
                "name": "Product name",
                "brand": "Product brand",
                "model": "Product model",
                "description": "Product description",
                "price": 100.0,
                "available_sizes": ["S", "M", "L"],
                "colors": ["red", "blue", "green"],
                "rating": 4.5,
            }
        }
