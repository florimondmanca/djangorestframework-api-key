from rest_framework.routers import DefaultRouter

from .views import PetViewSet

router = DefaultRouter()
router.register("pets", PetViewSet)

urlpatterns = router.urls
