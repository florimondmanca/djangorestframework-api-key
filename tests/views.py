"""Views for testing purposes."""

from rest_framework.views import APIView
from rest_framework.response import Response


def create_test_view(*perm_classes):
    """Create a test view with given permission classes."""

    class View(APIView):

        permission_classes = perm_classes

        def get(self, request):
            return Response()

    return View.as_view()
