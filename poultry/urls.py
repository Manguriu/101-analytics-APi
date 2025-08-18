from poultry.flock.views import CustomObtainAuthToken
from drf_spectacular.views import (  # type: ignore
    SpectacularAPIView,
    SpectacularSwaggerView,
)


from django.contrib import admin
from django.urls import path, include

from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="/api/docs/", permanent=False), name="home"),
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
    path("api/user/", include("poultry.user.urls")),
    path("api/flock/", include("poultry.flock.urls")),
    path("api/user/token/", CustomObtainAuthToken.as_view(), name="token"),
]
