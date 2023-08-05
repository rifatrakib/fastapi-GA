import json
from typing import Any, Dict, Union
from uuid import uuid4

from pydantic import HttpUrl

from server.database.managers import cache_data
from server.models.schemas.users import UserAccount


def create_temporary_activation_url(
    user: UserAccount, url: HttpUrl, extras: Union[Dict[str, Any], None] = None
) -> HttpUrl:
    key = str(uuid4())
    data = user.dict()

    if extras:
        data.update(**extras)

    cache_data(key=key, data=json.dumps(data), ttl=60)
    return f"{url}?key={key}"
