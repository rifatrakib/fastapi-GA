from beanie import PydanticObjectId

from server.models.documents.products import ShopDocument
from server.utils.messages import raise_404_not_found


async def read_shop_by_id(shop_id: str) -> ShopDocument:
    shop = await ShopDocument.get(PydanticObjectId(shop_id))
    if not shop:
        raise raise_404_not_found("Shop not found")
    return shop
