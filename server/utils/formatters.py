from datetime import datetime, timezone


def format_datetime_into_isoformat(ts: datetime) -> str:
    return ts.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
