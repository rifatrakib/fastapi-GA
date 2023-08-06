from server.models.documents.products import ProductDocument


async def read_product_by_id(product_id: str) -> ProductDocument:
    return await ProductDocument.get(product_id)
