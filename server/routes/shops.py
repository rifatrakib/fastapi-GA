from fastapi import APIRouter, HTTPException

from server.database.shops.crud import read_shop_by_id
from server.schemas.out.products import ShopResponse
from server.utils.enums import Tags

router = APIRouter(prefix="/shops", tags=[Tags.shops])


@router.get(
    "/{shop_id}",
    summary="Get shop by id",
    description="Get shop by id",
    response_model=ShopResponse,
)
async def read_single_shop(shop_id: str) -> ShopResponse:
    try:
        return await read_shop_by_id(shop_id)
    except HTTPException as e:
        raise e
