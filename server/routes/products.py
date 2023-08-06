from fastapi import APIRouter

from server.database.products.crud import read_product_by_id
from server.utils.enums import Tags

router = APIRouter(prefix="/products", tags=Tags.products)


@router.get("/{product_id}")
async def read_single_product(product_id: str):
    return await read_product_by_id(product_id)
