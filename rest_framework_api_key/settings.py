from django.conf import settings

API_KEY_HEADER = getattr(settings, 'API_KEY_HEADER', 'HTTP_API_KEY')
