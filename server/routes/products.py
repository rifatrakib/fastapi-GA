from fastapi import APIRouter, HTTPException, status

from server.database.products.crud import (
    create_product,
    delete_product_by_id,
    read_product_by_id,
    update_product_by_id,
)
from server.schemas.inc.products import ProductRequest
from server.schemas.out.products import ProductResponse
from server.utils.enums import Tags

router = APIRouter(prefix="/products", tags=[Tags.products])


@router.get(
    "/{product_id}",
    summary="Get a single product",
    description="Get a single product by its ID",
    response_model=ProductResponse,
)
async def read_single_product(product_id: str):
    try:
        return await read_product_by_id(product_id)
    except HTTPException as e:
        raise e


@router.post(
    "",
    summary="Create new product",
    description="Create a single product",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_single_product(product: ProductRequest):
    try:
        return await create_product(product)
    except HTTPException as e:
        raise e


@router.patch(
    "/{product_id}",
    summary="Update a single product",
    description="Update a single product by its ID",
    response_model=ProductResponse,
)
async def update_single_product(product_id: str, product: ProductRequest):
    try:
        return await update_product_by_id(product_id, product)
    except HTTPException as e:
        raise e


@router.delete(
    "/{product_id}",
    summary="Delete a single product",
    description="Delete a single product by its ID",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_single_product(product_id: str):
    try:
        await delete_product_by_id(product_id)
    except HTTPException as e:
        raise e
