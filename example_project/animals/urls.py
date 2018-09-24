"""Example URL configuration."""

from rest_framework.routers import DefaultRouter

from .views import AnimalViewSet

router = DefaultRouter()
router.register('animals', AnimalViewSet)

urlpatterns = router.urls
