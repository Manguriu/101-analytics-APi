# "test for flock api"

# from django.contrib.auth import get_user_model
# from django.test import TestCase
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APIClient
# from datetime import date


# from core.models import Flock, HealthCheck
# from flock.serializers import (
#     FlockSerializer,
#     FlockDetailSerializer,
# )


# HEALTHCHECK_URL = reverse("flock:healthcheck-list")
# SUMMARY_URL = reverse("flock:healthcheck-summary")
# FLOCK_SUMMARY_URL = reverse("flock:flock-summary")
# FLOCKS_URL = reverse("flock:flock-list")
# SUMMARY_URL = reverse("flock:flock-summary")
# HEALTHCHECK_URL = reverse("flock:healthcheck-list")
# SUMMARY_URL = reverse("flock:healthcheck-summary")


# def detail_url(flock_id):
#     "create and return a flock detail URL"
#     return reverse("flock:flock-detail", args=[flock_id])


# "helper function to create flock"


# def create_flock(user, **params):
#     "create and retun sample flocks"
#     defaults = {
#         "batch_name": "Test Batch",
#         "date_acquired": "2025-06-01",
#         "initial_count": 100,
#         "breed": "Broiler",
#     }
#     defaults.update(params)

#     flock = Flock.objects.create(user=user, **defaults)
#     return flock


# def create_user(**params):
#     """Create and return a new user."""
#     return get_user_model().objects.create_user(**params)


# class PublicFlockAPITests(TestCase):
#     "Test authenticated API requests"

#     def setUp(self):
#         self.client = APIClient()

#     def test_auth_required(self):
#         "test auth is required to call API"
#         res = self.client.get(FLOCKS_URL)

#         self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# class PrivateFlockApiTests(TestCase):
#     "test authenticated api request"

#     def setUp(self):
#         self.client = APIClient()
#         self.user = create_user(email="user@example.com", password="testpass123")
#         self.client.force_authenticate(self.user)

#     def test_retrieve_flocks(self):
#         create_flock(user=self.user)
#         create_flock(user=self.user)

#         res = self.client.get(FLOCKS_URL)

#         flocks = Flock.objects.all().order_by("-id")
#         serializer = FlockSerializer(flocks, many=True)
#         self.assertTrue(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data, serializer.data)

#     def test_flock_list_limited_to_user(self):
#         """Test list of flocks is limited to authenticated user."""
#         other_user = create_user(email="other@example.com", password="test123")
#         create_flock(user=other_user)
#         create_flock(user=self.user)

#         res = self.client.get(FLOCKS_URL)

#         flocks = Flock.objects.filter(user=self.user)
#         serializer = FlockSerializer(flocks, many=True)
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data, serializer.data)

#     def test_get_flock_detail(self):
#         """Test get recipe detail."""
#         flock = create_flock(user=self.user)

#         url = detail_url(flock.id)
#         res = self.client.get(url)

#         serializer = FlockDetailSerializer(flock)
#         self.assertEqual(res.data, serializer.data)

#     def test_create_flock(self):
#         """Test creating a flock."""
#         payload = {
#             "batch_name": "Test Batch 1",
#             "date_acquired": "2025-06-01",
#             "initial_count": 100,
#             "breed": "Broiler",
#         }
#         res = self.client.post(FLOCKS_URL, payload)

#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#         flock = Flock.objects.get(id=res.data["id"])

#         # fields checks to handle type conversion
#         self.assertEqual(flock.batch_name, payload["batch_name"])
#         self.assertEqual(flock.initial_count, payload["initial_count"])
#         self.assertEqual(flock.breed, payload["breed"])
#         self.assertEqual(
#             flock.date_acquired, date.fromisoformat(payload["date_acquired"])
#         )
#         self.assertEqual(flock.user, self.user)

#     def test_partial_update(self):
#         """Test partial update of a flock."""
#         original_breed = "Broiler"
#         flock = create_flock(
#             user=self.user,
#             batch_name="Sample Batch",
#             breed=original_breed,
#         )

#         payload = {"batch_name": "New Batch Name"}
#         url = detail_url(flock.id)
#         res = self.client.patch(url, payload)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         flock.refresh_from_db()
#         self.assertEqual(flock.batch_name, payload["batch_name"])
#         self.assertEqual(flock.breed, original_breed)
#         self.assertEqual(flock.user, self.user)

#     def test_full_update(self):
#         """Test full update of flock."""
#         flock = create_flock(
#             user=self.user,
#             batch_name="Sample Batch",
#             date_acquired="2025-06-01",
#             initial_count=100,
#             breed="Broiler",
#         )

#         payload = {
#             "batch_name": "New Batch Name",
#             "date_acquired": "2025-07-01",
#             "initial_count": 150,
#             "breed": "Layer",
#         }
#         url = detail_url(flock.id)
#         res = self.client.put(url, payload)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         flock.refresh_from_db()
#         for k, v in payload.items():
#             if k == "date_acquired":
#                 self.assertEqual(getattr(flock, k), date.fromisoformat(v))
#             else:
#                 self.assertEqual(getattr(flock, k), v)
#         self.assertEqual(flock.user, self.user)

#     def test_update_user_returns_error(self):
#         """Test changing the flock user results in an error."""
#         new_user = create_user(email="user2@example.com", password="test123")
#         flock = create_flock(user=self.user)

#         payload = {"user": new_user.id}
#         url = detail_url(flock.id)
#         res = self.client.patch(url, payload)

#         flock.refresh_from_db()
#         self.assertEqual(flock.user, self.user)

#     def test_delete_flock(self):
#         """Test deleting a flock successful."""
#         flock = create_flock(user=self.user)

#         url = detail_url(flock.id)
#         res = self.client.delete(url)

#         self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertFalse(Flock.objects.filter(id=flock.id).exists())

#     def test_flock_other_users_flock_error(self):
#         """Test trying to delete another user's flock gives error."""
#         new_user = create_user(email="user2@example.com", password="test123")
#         flock = create_flock(user=new_user)

#         url = detail_url(flock.id)
#         res = self.client.delete(url)

#         self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
#         self.assertTrue(Flock.objects.filter(id=flock.id).exists())


# # summaries tests
# class FlockSummaryAPITests(TestCase):
#     """Test flock summary endpoint."""

#     def setUp(self):
#         self.client = APIClient()
#         self.user = create_user(email="summary@example.com", password="pass123")
#         self.client.force_authenticate(self.user)

#     def test_summary_empty(self):
#         """Test summary when no flocks exist."""
#         res = self.client.get(SUMMARY_URL)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data["total_flocks"], 0)
#         self.assertEqual(res.data["total_birds"], 0)

#     def test_summary_single_flock(self):
#         Flock.objects.create(
#             user=self.user,
#             batch_name="Alpha",
#             date_acquired="2023-01-01",
#             initial_count=10,
#         )

#         url = reverse("flock:flock-summary")
#         res = self.client.get(url)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data["total_flocks"], 1)
#         self.assertEqual(res.data["total_birds"], 10)

#     def test_summary_multiple_flocks(self):
#         """Test summary with multiple flocks."""
#         create_flock(user=self.user, initial_count=200)
#         create_flock(user=self.user, initial_count=120)
#         create_flock(user=self.user, initial_count=80)

#         res = self.client.get(SUMMARY_URL)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data["total_flocks"], 3)
#         self.assertEqual(res.data["total_birds"], 400)

#     def test_summary_limited_to_user(self):
#         """Test that summary only includes user's flocks."""
#         other_user = create_user(email="other@example.com", password="otherpass")
#         create_flock(user=other_user, initial_count=100)
#         create_flock(user=self.user, initial_count=250)

#         res = self.client.get(SUMMARY_URL)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data["total_flocks"], 1)
#         self.assertEqual(res.data["total_birds"], 250)


# # HealthCheck
# def create_healthcheck(flock, **params):
#     defaults = {"date": date.today(), "deaths": 5, "disease": "Coccidiosis"}
#     defaults.update(params)
#     return HealthCheck.objects.create(flock=flock, **defaults)


# class PublicHealthCheckApiTests(TestCase):
#     """Test unauthenticated health check access"""

#     def setUp(self):
#         self.client = APIClient()

#     def test_auth_required(self):
#         res = self.client.get(HEALTHCHECK_URL)
#         self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# class PrivateHealthCheckApiTests(TestCase):
#     """Test authenticated health check operations"""

#     def setUp(self):
#         self.client = APIClient()
#         self.user = create_user(email="health@example.com", password="testpass123")
#         self.client.force_authenticate(self.user)

#     def test_create_healthcheck(self):
#         """Test creating a health check"""
#         flock = create_flock(user=self.user)
#         payload = {
#             "date": "2025-07-01",
#             "deaths": 4,
#             "disease": "Avian flu",
#             "flock": flock.id,
#         }
#         res = self.client.post(HEALTHCHECK_URL, payload)

#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#         health = HealthCheck.objects.get(id=res.data["id"])
#         self.assertEqual(health.disease, payload["disease"])
#         self.assertEqual(health.deaths, payload["deaths"])
#         self.assertEqual(health.flock, flock)

#     def test_list_healthchecks_limited_to_user(self):
#         """Test listing health checks for authenticated user only"""
#         other_user = create_user(email="other@example.com", password="test123")
#         flock1 = create_flock(user=self.user)
#         flock2 = create_flock(user=other_user)

#         create_healthcheck(flock=flock1)
#         create_healthcheck(flock=flock2)

#         res = self.client.get(HEALTHCHECK_URL)
#         healthchecks = HealthCheck.objects.filter(flock__user=self.user)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(res.data), healthchecks.count())
#         self.assertEqual(res.data[0]["flock"], flock1.id)

#     def test_healthcheck_summary_no_data(self):
#         """Test summary with no health checks"""
#         res = self.client.get(SUMMARY_URL)
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data["total_deaths"], 0)
#         self.assertEqual(res.data["most_common_disease"], None)
#         self.assertEqual(res.data["health_percentage"], 100)

#     def test_healthcheck_summary_with_data(self):
#         """Test health summary calculations"""
#         flock = create_flock(user=self.user, initial_count=100)
#         create_healthcheck(flock=flock, deaths=10, disease="Flu")
#         create_healthcheck(flock=flock, deaths=5, disease="Flu")
#         create_healthcheck(flock=flock, deaths=3, disease="Pox")

#         res = self.client.get(SUMMARY_URL)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data["total_deaths"], 18)
#         self.assertEqual(res.data["most_common_disease"], "Flu")
#         self.assertEqual(res.data["health_percentage"], 82.0)

#     def test_healthcheck_summary_only_user_data(self):
#         """Ensure other users' data is not included in summary"""
#         other_user = create_user(email="other@example.com", password="pass123")
#         flock_user = create_flock(user=self.user, initial_count=100)
#         flock_other = create_flock(user=other_user, initial_count=100)

#         create_healthcheck(flock=flock_user, deaths=10, disease="Pox")
#         create_healthcheck(flock=flock_other, deaths=20, disease="Flu")

#         res = self.client.get(SUMMARY_URL)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data["total_deaths"], 10)
#         self.assertEqual(res.data["most_common_disease"], "Pox")
#         self.assertEqual(res.data["health_percentage"], 90.0)


# class FlockSummaryAPITests(TestCase):
#     """Test flock summary API endpoints"""

#     def setUp(self):
#         self.client = APIClient()
#         self.user = create_user(email="test@example.com", password="testpass123")
#         self.client.force_authenticate(self.user)

#     def test_summary_empty(self):
#         """Test summary when no flocks exist"""
#         res = self.client.get(SUMMARY_URL)
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data["total_deaths"], 0)
#         self.assertEqual(res.data["most_common_disease"], None)
#         self.assertEqual(res.data["health_percentage"], 100)

#     def test_summary_multiple_flocks(self):
#         """Test summary with multiple flocks"""
#         flock1 = create_flock(user=self.user, initial_count=100)
#         flock2 = create_flock(user=self.user, initial_count=50)
#         create_healthcheck(flock=flock1, deaths=10, disease="Flu")
#         create_healthcheck(flock=flock2, deaths=5, disease="Flu")

#         res = self.client.get(SUMMARY_URL)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data["total_deaths"], 15)
#         self.assertEqual(res.data["most_common_disease"], "Flu")
#         self.assertEqual(res.data["health_percentage"], 90.0)

#     def test_summary_limited_to_user(self):
#         """Test that summary only includes user's flocks"""
#         other_user = create_user(email="other@example.com", password="pass123")
#         flock_user = create_flock(user=self.user, initial_count=100)
#         flock_other = create_flock(user=other_user, initial_count=100)

#         create_healthcheck(flock=flock_user, deaths=10, disease="Pox")
#         create_healthcheck(flock=flock_other, deaths=20, disease="Flu")

#         res = self.client.get(SUMMARY_URL)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data["total_deaths"], 10)
#         self.assertEqual(res.data["most_common_disease"], "Pox")
#         self.assertEqual(res.data["health_percentage"], 90.0)


# class PublicHealthCheckApiTests(TestCase):
#     """Test unauthenticated health check access"""

#     def setUp(self):
#         self.client = APIClient()

#     def test_auth_required(self):
#         res = self.client.get(HEALTHCHECK_URL)
#         self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# class PrivateHealthCheckApiTests(TestCase):
#     """Test authenticated health check operations"""

#     def setUp(self):
#         self.client = APIClient()
#         self.user = create_user(email="health@example.com", password="testpass123")
#         self.client.force_authenticate(self.user)

#     def test_create_healthcheck(self):
#         """Test creating a health check"""
#         flock = create_flock(user=self.user)
#         payload = {
#             "date": "2025-07-01",
#             "symptoms": "Coughing",
#             "disease": "Avian flu",
#             "treatment": "Antibiotics",
#             "health_status": "Stable",
#             "deaths": 4,
#             "flock": flock.id,
#             "notes": "Initial treatment applied",
#         }
#         res = self.client.post(HEALTHCHECK_URL, payload)

#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#         health = HealthCheck.objects.get(id=res.data["id"])
#         self.assertEqual(health.disease, payload["disease"])
#         self.assertEqual(health.deaths, payload["deaths"])
#         self.assertEqual(health.health_status, payload["health_status"])
#         self.assertEqual(health.flock, flock)

#     def test_list_healthchecks_limited_to_user(self):
#         """Test listing health checks for authenticated user only"""
#         other_user = create_user(email="other@example.com", password="test123")
#         flock1 = create_flock(user=self.user)
#         flock2 = create_flock(user=other_user)

#         create_healthcheck(flock=flock1)
#         create_healthcheck(flock=flock2)

#         res = self.client.get(HEALTHCHECK_URL)
#         healthchecks = HealthCheck.objects.filter(flock__user=self.user)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(res.data), healthchecks.count())
#         self.assertEqual(res.data[0]["flock"], flock1.id)

#     def test_healthcheck_summary_no_data(self):
#         """Test summary with no health checks"""
#         res = self.client.get(SUMMARY_URL)
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data["total_deaths"], 0)
#         self.assertEqual(res.data["most_common_disease"], None)
#         self.assertEqual(res.data["health_percentage"], 100)

#     def test_healthcheck_summary_with_data(self):
#         """Test health summary calculations"""
#         flock = create_flock(user=self.user, initial_count=100)
#         create_healthcheck(flock=flock, deaths=10, disease="Flu")
#         create_healthcheck(flock=flock, deaths=5, disease="Flu")
#         create_healthcheck(flock=flock, deaths=3, disease="Pox")

#         res = self.client.get(SUMMARY_URL)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data["total_deaths"], 18)
#         self.assertEqual(res.data["most_common_disease"], "Flu")
#         self.assertEqual(res.data["health_percentage"], 82.0)

#     def test_healthcheck_summary_only_user_data(self):
#         """Ensure other users' data is not included in summary"""
#         other_user = create_user(email="other@example.com", password="pass123")
#         flock_user = create_flock(user=self.user, initial_count=100)
#         flock_other = create_flock(user=other_user, initial_count=100)

#         create_healthcheck(flock=flock_user, deaths=10, disease="Pox")
#         create_healthcheck(flock=flock_other, deaths=20, disease="Flu")

#         res = self.client.get(SUMMARY_URL)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data["total_deaths"], 10)
#         self.assertEqual(res.data["most_common_disease"], "Pox")
#         self.assertEqual(res.data["health_percentage"], 90.0)


from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import date

from core.models import Flock, HealthCheck
from flock.serializers import FlockSerializer, FlockDetailSerializer

# Define URL constants at the top
FLOCKS_URL = reverse("flock:flock-list")
FLOCK_SUMMARY_URL = reverse("flock:flock-summary")
HEALTHCHECK_URL = reverse("flock:healthcheck-list")


def detail_url(flock_id):
    """Create and return a flock detail URL"""
    return reverse("flock:flock-detail", args=[flock_id])


def create_flock(user, **params):
    """Create and return sample flocks"""
    defaults = {
        "batch_name": "Test Batch",
        "date_acquired": "2025-06-01",
        "initial_count": 100,
        "breed": "Broiler",
    }
    defaults.update(params)
    return Flock.objects.create(user=user, **defaults)


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


def create_healthcheck(flock, date=date.today(), **params):
    """Create and return health checks with flexible dates"""
    defaults = {
        "date": date,
        "deaths": 5,
        "health_status": "Good",
        "symptoms": "None",
        "treatment": "None",
        "notes": "Sample notes",
    }
    defaults.update(params)
    return HealthCheck.objects.create(flock=flock, **defaults)


class PublicFlockAPITests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(FLOCKS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateFlockApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="user@example.com", password="testpass123")
        self.client.force_authenticate(self.user)

    def test_retrieve_flocks(self):
        """Test retrieving flocks list"""
        create_flock(user=self.user)
        create_flock(user=self.user)

        res = self.client.get(FLOCKS_URL)
        flocks = Flock.objects.all().order_by("-id")
        serializer = FlockSerializer(flocks, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_flock_list_limited_to_user(self):
        """Test list of flocks is limited to authenticated user"""
        other_user = create_user(email="other@example.com", password="test123")
        create_flock(user=other_user)
        create_flock(user=self.user)

        res = self.client.get(FLOCKS_URL)
        flocks = Flock.objects.filter(user=self.user)
        serializer = FlockSerializer(flocks, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_flock_detail(self):
        """Test get flock detail"""
        flock = create_flock(user=self.user)
        url = detail_url(flock.id)
        res = self.client.get(url)

        serializer = FlockDetailSerializer(flock)
        self.assertEqual(res.data, serializer.data)

    def test_create_flock(self):
        """Test creating a flock"""
        payload = {
            "batch_name": "Test Batch 1",
            "date_acquired": "2025-06-01",
            "initial_count": 100,
            "breed": "Broiler",
        }
        res = self.client.post(FLOCKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        flock = Flock.objects.get(id=res.data["id"])
        self.assertEqual(flock.batch_name, payload["batch_name"])
        self.assertEqual(flock.initial_count, payload["initial_count"])
        self.assertEqual(flock.breed, payload["breed"])
        self.assertEqual(
            flock.date_acquired, date.fromisoformat(payload["date_acquired"])
        )
        self.assertEqual(flock.user, self.user)

    def test_partial_update(self):
        """Test partial update of a flock"""
        original_breed = "Broiler"
        flock = create_flock(
            user=self.user,
            batch_name="Sample Batch",
            breed=original_breed,
        )

        payload = {"batch_name": "New Batch Name"}
        url = detail_url(flock.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        flock.refresh_from_db()
        self.assertEqual(flock.batch_name, payload["batch_name"])
        self.assertEqual(flock.breed, original_breed)
        self.assertEqual(flock.user, self.user)

    def test_full_update(self):
        """Test full update of flock"""
        flock = create_flock(
            user=self.user,
            batch_name="Sample Batch",
            date_acquired="2025-06-01",
            initial_count=100,
            breed="Broiler",
        )

        payload = {
            "batch_name": "New Batch Name",
            "date_acquired": "2025-07-01",
            "initial_count": 150,
            "breed": "Layer",
        }
        url = detail_url(flock.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        flock.refresh_from_db()
        for k, v in payload.items():
            if k == "date_acquired":
                self.assertEqual(getattr(flock, k), date.fromisoformat(v))
            else:
                self.assertEqual(getattr(flock, k), v)
        self.assertEqual(flock.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the flock user results in an error"""
        new_user = create_user(email="user2@example.com", password="test123")
        flock = create_flock(user=self.user)

        payload = {"user": new_user.id}
        url = detail_url(flock.id)
        res = self.client.patch(url, payload)

        flock.refresh_from_db()
        self.assertEqual(flock.user, self.user)

    def test_delete_flock(self):
        """Test deleting a flock successful"""
        flock = create_flock(user=self.user)

        url = detail_url(flock.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Flock.objects.filter(id=flock.id).exists())

    def test_flock_other_users_flock_error(self):
        """Test trying to delete another user's flock gives error"""
        new_user = create_user(email="user2@example.com", password="test123")
        flock = create_flock(user=new_user)

        url = detail_url(flock.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Flock.objects.filter(id=flock.id).exists())


class FlockSummaryAPITests(TestCase):
    """Test flock summary endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="summary@example.com", password="pass123")
        self.client.force_authenticate(self.user)

    def test_summary_empty(self):
        """Test summary when no flocks exist"""
        res = self.client.get(FLOCK_SUMMARY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["total_flocks"], 0)
        self.assertEqual(res.data["total_birds"], 0)

    def test_summary_single_flock(self):
        """Test summary with single flock"""
        Flock.objects.create(
            user=self.user,
            batch_name="Alpha",
            date_acquired="2023-01-01",
            initial_count=10,
        )

        res = self.client.get(FLOCK_SUMMARY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["total_flocks"], 1)
        self.assertEqual(res.data["total_birds"], 10)

    def test_summary_multiple_flocks(self):
        """Test summary with multiple flocks"""
        create_flock(user=self.user, initial_count=200)
        create_flock(user=self.user, initial_count=120)
        create_flock(user=self.user, initial_count=80)

        res = self.client.get(FLOCK_SUMMARY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["total_flocks"], 3)
        self.assertEqual(res.data["total_birds"], 400)

    def test_summary_limited_to_user(self):
        """Test that summary only includes user's flocks"""
        other_user = create_user(email="other@example.com", password="otherpass")
        create_flock(user=other_user, initial_count=100)
        create_flock(user=self.user, initial_count=250)

        res = self.client.get(FLOCK_SUMMARY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["total_flocks"], 1)
        self.assertEqual(res.data["total_birds"], 250)


class PublicHealthCheckApiTests(TestCase):
    """Test unauthenticated health check access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(HEALTHCHECK_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateHealthCheckApiTests(TestCase):
    """Test authenticated health check operations"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="health@example.com", password="testpass123")
        self.client.force_authenticate(self.user)

    def test_create_healthcheck(self):
        """Test creating a health check with all fields"""
        flock = create_flock(user=self.user)
        payload = {
            "flock": flock.id,
            "date": "2025-07-01",
            "symptoms": "Coughing, sneezing",
            "treatment": "Antibiotics",
            "health_status": "Stable",
            "deaths": 4,
            "notes": "Isolating affected birds",
        }
        res = self.client.post(HEALTHCHECK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        health = HealthCheck.objects.get(id=res.data["id"])
        self.assertEqual(health.flock.id, payload["flock"])
        self.assertEqual(str(health.date), payload["date"])
        self.assertEqual(health.symptoms, payload["symptoms"])
        self.assertEqual(health.treatment, payload["treatment"])
        self.assertEqual(health.health_status, payload["health_status"])
        self.assertEqual(health.deaths, payload["deaths"])
        self.assertEqual(health.notes, payload["notes"])

    def test_create_healthcheck_minimal_fields(self):
        """Test creating health check with only required fields"""
        flock = create_flock(user=self.user)
        payload = {
            "flock": flock.id,
            "date": "2025-07-01",
            "health_status": "Good",
            "deaths": 2,
        }
        res = self.client.post(HEALTHCHECK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        health = HealthCheck.objects.get(id=res.data["id"])
        self.assertEqual(health.flock.id, payload["flock"])
        self.assertEqual(str(health.date), payload["date"])
        self.assertEqual(health.health_status, payload["health_status"])
        self.assertEqual(health.deaths, payload["deaths"])

    def test_cannot_create_healthcheck_for_other_users_flock(self):
        """Test cannot create health check for another user's flock"""
        other_user = create_user(email="other@example.com", password="test123")
        flock = create_flock(user=other_user)

        payload = {
            "flock": flock.id,
            "date": "2025-07-01",
            "health_status": "Good",
            "deaths": 2,
        }
        res = self.client.post(HEALTHCHECK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Current user has no rights", str(res.data))

    def test_list_healthchecks_limited_to_user(self):
        """Test listing health checks for authenticated user only"""
        other_user = create_user(email="other@example.com", password="test123")
        flock1 = create_flock(user=self.user)
        flock2 = create_flock(user=other_user)

        # Create health checks with complete data
        health1 = create_healthcheck(flock=flock1)
        health2 = create_healthcheck(flock=flock2)

        res = self.client.get(HEALTHCHECK_URL)
        healthchecks = HealthCheck.objects.filter(flock__user=self.user)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), healthchecks.count())
        self.assertEqual(res.data[0]["id"], health1.id)
        self.assertEqual(res.data[0]["flock"], flock1.id)

    def test_retrieve_healthcheck_detail(self):
        """Test retrieving health check details"""
        flock = create_flock(user=self.user)
        health = create_healthcheck(flock=flock)

        url = reverse("flock:healthcheck-detail", args=[health.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], health.id)
        self.assertEqual(res.data["flock"], health.flock.id)
        self.assertEqual(res.data["date"], str(health.date))
        self.assertEqual(res.data["symptoms"], health.symptoms)
        self.assertEqual(res.data["health_status"], health.health_status)
        self.assertEqual(res.data["deaths"], health.deaths)

    def test_update_healthcheck(self):
        """Test updating a health check"""
        flock = create_flock(user=self.user)
        health = create_healthcheck(flock=flock)

        payload = {
            "health_status": "Critical",
            "deaths": 10,
            "notes": "Emergency treatment needed",
        }
        url = reverse("flock:healthcheck-detail", args=[health.id])
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        health.refresh_from_db()
        self.assertEqual(health.health_status, payload["health_status"])
        self.assertEqual(health.deaths, payload["deaths"])
        self.assertEqual(health.notes, payload["notes"])

    def test_delete_healthcheck(self):
        """Test deleting a health check"""
        flock = create_flock(user=self.user)
        health = create_healthcheck(flock=flock)

        url = reverse("flock:healthcheck-detail", args=[health.id])
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(HealthCheck.objects.filter(id=health.id).exists())
