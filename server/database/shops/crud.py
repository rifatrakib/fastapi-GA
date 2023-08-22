from typing import List

from beanie import PydanticObjectId
from beanie.odm.operators.find.evaluation import Text

from server.models.documents.products import ShopDocument
from server.schemas.inc.products import ShopRequest
from server.utils.messages import raise_404_not_found


async def create_shop(shop: ShopRequest, owner_id: int) -> ShopDocument:
    shop = await ShopDocument.insert_one(ShopDocument(**shop.dict(), owner_id=owner_id))
    return shop


async def read_shop_by_id(shop_id: str) -> ShopDocument:
    shop = await ShopDocument.get(PydanticObjectId(shop_id))
    if not shop:
        raise raise_404_not_found("Shop not found")
    return shop


async def read_shop_by_owner(owner_id: int, page: int, limit: int = 10) -> List[ShopDocument]:
    shops = (
        await ShopDocument.find(ShopDocument.owner_id == owner_id)
        .sort(+ShopDocument.name)
        .skip((page - 1) * limit)
        .limit(limit)
        .to_list()
    )
    return shops


async def search_shops_by_name(name: str, page: int, limit: int = 10) -> List[ShopDocument]:
    shops = await ShopDocument.find(Text(name)).sort(+ShopDocument.name).skip((page - 1) * limit).limit(limit).to_list()
    return shops


async def update_shop(shop_id: str, owner_id: int, shop: ShopRequest) -> ShopDocument:
    existing_shop = await ShopDocument.find_one(
        ShopDocument.id == PydanticObjectId(shop_id), ShopDocument.owner_id == owner_id
    )
    updated_shop = await ShopDocument(**{**existing_shop.dict(), **shop.dict(exclude_unset=True)}).save()
    return updated_shop


async def delete_shop(shop_id: str, owner_id: int):
    await ShopDocument.find_one(
        ShopDocument.id == PydanticObjectId(shop_id), ShopDocument.owner_id == owner_id
    ).delete()
