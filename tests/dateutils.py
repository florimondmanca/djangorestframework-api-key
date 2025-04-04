from datetime import datetime, timedelta, timezone

NOW = datetime.now(tz=timezone.utc)
TOMORROW = NOW + timedelta(days=1)
YESTERDAY = NOW - timedelta(days=1)
