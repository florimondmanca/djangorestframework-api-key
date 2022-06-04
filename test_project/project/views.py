from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from test_project.heroes.permissions import HasHeroAPIKey


class PublicAPIView(APIView):
    def get(self, request: Request) -> Response:
        return Response({"message": "Hello, world!"})


class ProtectedAPIView(APIView):
    permission_classes = [HasHeroAPIKey]

    def get(self, request: Request) -> Response:
        return Response({"message": "Hello, world!"})


class ProtectedObjectAPIView(APIView):
    permission_classes = [HasHeroAPIKey]

    def get(self, request: Request) -> Response:
        self.check_object_permissions(request, object())
        return Response({"message": "Hello, world!"})
