from fastapi import HTTPException, status


def raise_401_unauthorized(message: str = "Not authorized") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"msg": message},
    )


def raise_403_forbidden(message: str = "Forbidden") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"msg": message},
    )


def raise_404_not_found(message: str = "Not found") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"msg": message},
    )
