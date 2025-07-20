from django.urls import path, include
from rest_framework.routers import DefaultRouter  # type: ignore
from flock import views
from flock.views import FlockSummaryView

router = DefaultRouter()
router.register("flocks", views.FlockViewSet)
router.register("summaries", views.FlockSummaryViewSet)


app_name = "flock"

urlpatterns = [
    path("", include(router.urls)),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("summary/", FlockSummaryView.as_view(), name="flock-summary"),
]
