from typing import List, Union

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(..., title="Product name")
    brand: str = Field(..., title="Product brand")
    model: str = Field(..., title="Product model")
    description: str = Field(..., title="Product description")
    price: float = Field(..., title="Product price")
    available_sizes: List[str] = Field(default_factory=list, title="Available sizes of the product")
    colors: List[str] = Field(default_factory=list, title="Available colors of the product")
    rating: Union[float, None] = Field(default=None, title="Average product rating")
