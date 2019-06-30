from rest_framework_api_key.permissions import HasAPIKey
from .crypto import LegacyKeyGenerator


class HasAPIKeyWithLegacyKeyGenerator(HasAPIKey):
    key_generator = LegacyKeyGenerator()
