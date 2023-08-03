from uuid import uuid4

from pydantic import HttpUrl

from server.database.managers import cache_data
from server.models.schemas.users import UserAccount


def create_temporary_activation_url(user: UserAccount, url: HttpUrl) -> HttpUrl:
    key = str(uuid4())
    cache_data(key=key, data=user.json(), ttl=60)
    return f"{url}?key={key}"
