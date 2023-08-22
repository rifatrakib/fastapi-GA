from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from server.database.shops.crud import (
    create_shop,
    delete_shop,
    read_shop_by_id,
    read_shop_by_owner,
    update_shop,
)
from server.schemas.inc.products import ShopRequest, ShopUpdateRequest
from server.schemas.out.auth import TokenUser
from server.schemas.out.products import ShopResponse
from server.security.dependencies import authenticate_active_user
from server.utils.enums import Tags

router = APIRouter(prefix="/shops", tags=[Tags.shops])


@router.get(
    "/me",
    summary="Get own shop",
    description="Get own shop information",
    response_model=List[ShopResponse],
)
async def read_personal_shop(
    page: int = Query(default=1, ge=1, title="Page number", description="Page number"),
    user: TokenUser = Depends(authenticate_active_user),
) -> ShopResponse:
    try:
        return await read_shop_by_owner(user.id, page)
    except HTTPException as e:
        raise e


@router.get(
    "/{shop_id}",
    summary="Get shop by id",
    description="Get shop by id",
    response_model=ShopResponse,
    dependencies=[Depends(authenticate_active_user)],
)
async def read_single_shop(shop_id: str) -> ShopResponse:
    try:
        return await read_shop_by_id(shop_id)
    except HTTPException as e:
        raise e


@router.post(
    "",
    summary="Create shop",
    description="Create shop",
    response_model=ShopResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_shop(
    shop: ShopRequest,
    user: TokenUser = Depends(authenticate_active_user),
) -> ShopResponse:
    try:
        return await create_shop(shop, user.id)
    except HTTPException as e:
        raise e


@router.patch(
    "/{shop_id}",
    summary="Update shop",
    description="Update shop",
    response_model=ShopResponse,
)
async def update_single_shop(
    shop_id: str,
    shop: ShopUpdateRequest,
    user: TokenUser = Depends(authenticate_active_user),
) -> ShopResponse:
    try:
        return await update_shop(shop_id, user.id, shop)
    except HTTPException as e:
        raise e


@router.delete(
    "/{shop_id}",
    summary="Delete shop",
    description="Delete shop",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_single_shop(
    shop_id: str,
    user: TokenUser = Depends(authenticate_active_user),
):
    try:
        await delete_shop(shop_id, user.id)
    except HTTPException as e:
        raise e
