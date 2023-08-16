from beanie import PydanticObjectId

from server.models.documents.products import ShopDocument
from server.schemas.inc.products import ShopRequest
from server.utils.messages import raise_404_not_found


async def create_shop(shop: ShopRequest) -> ShopDocument:
    shop = await ShopDocument.insert_one(ShopDocument(**shop.dict()))
    return shop


async def read_shop_by_id(shop_id: str) -> ShopDocument:
    shop = await ShopDocument.get(PydanticObjectId(shop_id))
    if not shop:
        raise raise_404_not_found("Shop not found")
    return shop


async def update_shop(shop_id: str, shop: ShopRequest) -> ShopDocument:
    existing_shop = await read_shop_by_id(shop_id)
    updated_shop = await ShopDocument(**{**existing_shop.dict(), **shop.dict(exclude_unset=True)}).save()
    return updated_shop


async def delete_shop(shop_id: str):
    await ShopDocument.find_one(ShopDocument.id == PydanticObjectId(shop_id)).delete()
