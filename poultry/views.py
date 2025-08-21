from django.db import connection
from django.http import HttpResponse, JsonResponse


def home(request):
    return HttpResponse("Welcome to the Poultry Management System!")


def health_check(request):
    return JsonResponse({"status": "ok"}, status=200)


# def health_check(request):
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT 1")
#         return JsonResponse({"status": "healthy", "database": "connected"})
#     except Exception as e:
#         return JsonResponse({"status": "error", "database": str(e)}, status=500)
