"""Example views."""

from rest_framework import viewsets


from .models import Animal
from .serializers import AnimalSerializer
from rest_framework_api_key.permissions import HasAPIKey


class AnimalViewSet(viewsets.ReadOnlyModelViewSet):
    """Endpoints for listing and retrieving animals."""

    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer
    permission_classes = (HasAPIKey,)
