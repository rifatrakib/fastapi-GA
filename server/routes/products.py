from fastapi import APIRouter, HTTPException

from server.database.products.crud import read_product_by_id
from server.schemas.out.products import ProductResponse
from server.utils.enums import Tags

router = APIRouter(prefix="/products", tags=[Tags.products])


@router.get("/{product_id}", response_model=ProductResponse)
async def read_single_product(product_id: str):
    try:
        return await read_product_by_id(product_id)
    except HTTPException as e:
        raise e
