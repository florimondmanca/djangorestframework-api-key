import pytest

from .legacy.permissions import HasAPIKeyWithLegacyKeyGenerator

pytestmark = pytest.mark.django_db


@pytest.fixture(name="view")
def fixture_view(view_with_permissions):
    return view_with_permissions(HasAPIKeyWithLegacyKeyGenerator)


def test_api_key_granted(create_request, view):
    request = create_request()
    response = view(request)
    assert response.status_code == 200
