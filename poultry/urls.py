# from poultry.flock.views import CustomObtainAuthToken
# from drf_spectacular.views import (
#     SpectacularAPIView,
#     SpectacularSwaggerView,
# )


# from django.contrib import admin
# from django.urls import path, include

# from django.views.generic import RedirectView

# urlpatterns = [
#     path("", RedirectView.as_view(url="/api/docs/", permanent=False), name="home"),
#     path("admin/", admin.site.urls),
#     path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
#     path(
#         "api/docs/",
#         SpectacularSwaggerView.as_view(url_name="schema"),
#         name="swagger-ui",
#     ),
#     path("api/user/", include("poultry.user.urls")),
#     path("api/flock/", include("poultry.flock.urls")),
#     path("api/user/token/", CustomObtainAuthToken.as_view(), name="token"),
# ]

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.http import JsonResponse
from django.db import connection
from poultry.flock.views import CustomObtainAuthToken
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "healthy", "database": "connected"})
    except Exception as e:
        return JsonResponse({"status": "error", "database": str(e)}, status=500)


urlpatterns = [
    path("", RedirectView.as_view(url="/api/docs/", permanent=False), name="home"),
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/user/", include("poultry.user.urls")),
    path("api/flock/", include("poultry.flock.urls")),
    path("api/user/token/", CustomObtainAuthToken.as_view(), name="token"),
    path("healthz/", health_check, name="health-check"),
]
