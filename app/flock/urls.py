from django.urls import path, include
from rest_framework.routers import DefaultRouter  # type: ignore
from flock import views
from flock.views import FinanceRecordViewSet, FinanceSummaryView, FlockSummaryView

router = DefaultRouter()
router.register("flocks", views.FlockViewSet)
router.register("summaries", views.FlockSummaryViewSet)
router.register("healthchecks", views.HealthCheckViewSet, basename="healthcheck")
router.register("finance-records", FinanceRecordViewSet)

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
    path("finance-summary/", FinanceSummaryView.as_view(), name="finance-summary"),
]
