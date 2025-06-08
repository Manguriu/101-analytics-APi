"url maping for flock app"

from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from flock import views

router = DefaultRouter()
router.register("flocks", views.FlockViewSet)

app_name = "flock"

urlpatterns = [
    path("", include(router.urls)),
]
