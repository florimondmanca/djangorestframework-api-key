from datetime import datetime, timedelta

NOW = datetime.now()
TOMORROW = NOW + timedelta(days=1)
YESTERDAY = NOW - timedelta(days=1)
