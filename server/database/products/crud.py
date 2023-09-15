from typing import List

from beanie import PydanticObjectId
from fastapi import HTTPException

from server.database.shops.crud import read_shop_by_id
from server.models.documents.products import ProductDocument
from server.schemas.inc.products import ProductRequest
from server.utils.messages import raise_403_forbidden, raise_404_not_found


async def create_product(product: ProductRequest, owner_id: int) -> ProductDocument:
    try:
        shop = await read_shop_by_id(product.shop_id)
        if shop.owner_id != owner_id:
            raise_403_forbidden("You are not the owner of this shop")

        product = ProductDocument(**product.dict(), shop=shop)
        await ProductDocument.insert_one(product)
        return product
    except HTTPException as e:
        raise e


async def read_product_by_id(product_id: str) -> ProductDocument:
    product = await ProductDocument.get(PydanticObjectId(product_id))
    if not product:
        raise_404_not_found("Product not found")
    return product


async def read_products(page: int, limit: int = 10) -> List[ProductDocument]:
    products = await ProductDocument.find().skip((page - 1) * limit).limit(limit).to_list()
    return products


async def update_product_by_id(product_id: str, product: ProductRequest) -> ProductDocument:
    existing_product = await read_product_by_id(product_id)
    updated_product = await ProductDocument(**{**existing_product.dict(), **product.dict(exclude_unset=True)}).save()
    return updated_product


async def delete_product_by_id(product_id: str):
    await ProductDocument.find_one(ProductDocument.id == PydanticObjectId(product_id)).delete()
