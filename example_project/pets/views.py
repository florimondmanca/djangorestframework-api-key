"""Example views."""

from rest_framework import viewsets


from .models import Pet
from .serializers import PetSerializer
from rest_framework_api_key.permissions import HasAPIKey


class PetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    permission_classes = [HasAPIKey]
