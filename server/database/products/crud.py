from beanie import PydanticObjectId

from server.models.documents.products import ProductDocument
from server.utils.messages import raise_404_not_found


async def read_product_by_id(product_id: str) -> ProductDocument:
    product = await ProductDocument.get(PydanticObjectId(product_id))
    if not product:
        raise raise_404_not_found("Product not found")
    return product
