from django.urls import path, include
from rest_framework.routers import DefaultRouter  # type: ignore
from flock import views
from flock.views import FlockSummaryView

router = DefaultRouter()
router.register("flocks", views.FlockViewSet)
router.register("summaries", views.FlockSummaryViewSet)
router.register("healthchecks", views.HealthCheckViewSet, basename="healthcheck")

app_name = "flock"

urlpatterns = [
    path("", include(router.urls)),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("summary/", FlockSummaryView.as_view(), name="flock-summary"),
    path(
        "healthchecks/summary/",
        views.HealthCheckSummaryView.as_view(),
        name="healthcheck-summary",
    ),
]
