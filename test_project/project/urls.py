from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/public/", views.PublicAPIView.as_view()),
    path("api/protected/", views.ProtectedAPIView.as_view()),
    path("api/protected/object/", views.ProtectedObjectAPIView.as_view()),
]
