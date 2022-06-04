import pytest
from rest_framework.test import APIClient
from test_project.heroes.models import Hero
from test_project.heroes.permissions import HeroAPIKey


@pytest.mark.django_db
def test_test_project_routes() -> None:
    batman = Hero.objects.create(name="Batman")
    _, key = HeroAPIKey.objects.create_key(name="test", hero=batman)
    headers = {"HTTP_AUTHORIZATION": f"Api-Key {key}"}

    client = APIClient()

    response = client.get("/api/public/", format="json")
    assert response.status_code == 200

    response = client.get("/api/protected/", format="json", **headers)
    assert response.status_code == 200

    response = client.get("/api/protected/object/", format="json", **headers)
    assert response.status_code == 200
