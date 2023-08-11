from typing import List, Union

from pydantic import Field

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


class ProductUpdateRequest(ProductBase):
    name: Union[str, None] = Field(default=None, title="Product name")
    brand: Union[str, None] = Field(default=None, title="Product brand")
    model: Union[str, None] = Field(default=None, title="Product model")
    description: Union[str, None] = Field(default=None, title="Product description")
    price: Union[float, None] = Field(default=None, title="Product price")
    available_sizes: List[str] = Field(default_factory=list, title="Available sizes of the product")
    colors: List[str] = Field(default_factory=list, title="Available colors of the product")
    rating: Union[float, None] = Field(default=None, title="Average product rating")

    class Config:
        schema_extra = {
            "example": {
                "name": "Product name",
                "brand": "Product brand",
                "model": "Product model",
                "price": 100.0,
                "available_sizes": ["S", "M", "L"],
                "colors": ["red", "blue", "green"],
                "rating": 4.5,
            }
        }
