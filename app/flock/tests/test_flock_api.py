from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status  # type: ignore
from rest_framework.test import APIClient  # type: ignore
from datetime import date, timedelta
from django.utils import timezone

from core.models import FinanceRecord, Flock, HealthCheck, User
from flock.serializers import FlockSerializer, FlockDetailSerializer

# Define URL constants at the top
FLOCKS_URL = reverse("flock:flock-list")
FLOCK_SUMMARY_URL = reverse("flock:flock-summary")
HEALTHCHECK_URL = reverse("flock:healthcheck-list")
FINANCE_SUMMARY_URL = reverse("flock:finance-summary")


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


# financialrecords


class FinanceSummaryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com", password="testpass"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.flock1 = Flock.objects.create(
            user=self.user,
            batch_name="Batch A",
            initial_count=100,
            date_acquired="2025-06-01",
            breed="Broiler",
        )
        self.flock2 = Flock.objects.create(
            user=self.user,
            batch_name="Batch B",
            initial_count=150,
            date_acquired="2025-06-01",
            breed="Broiler",
        )

        now = timezone.now()

        # Record 1: created 5 days ago
        self.record1 = FinanceRecord.objects.create(
            flock=self.flock1,
            batch_name="Batch A",
            number_of_initial_birds=100,
            price_per_initial_bird=20.00,
            total_initial_cost=2000.00,
            food_expense=500.00,
            water_expense=100.00,
            vaccination_expense=150.00,
            medicine_expense=200.00,
            lab_expense=50.00,
            remaining_birds=90,
            selling_price_per_bird=30.00,
        )
        # Update created_at to 5 days ago
        self.record1.created_at = now - timezone.timedelta(days=5)
        self.record1.save()

        # Record 2: created today
        self.record2 = FinanceRecord.objects.create(
            flock=self.flock2,
            batch_name="Batch B",
            number_of_initial_birds=150,
            price_per_initial_bird=25.00,
            total_initial_cost=3750.00,
            food_expense=700.00,
            water_expense=150.00,
            vaccination_expense=200.00,
            medicine_expense=300.00,
            lab_expense=100.00,
            remaining_birds=145,
            selling_price_per_bird=35.00,
            created_at=now,
        )
        # Debug: Print created_at values
        print(f"Setup - Record1 created_at: {self.record1.created_at}")
        print(f"Setup - Record2 created_at: {self.record2.created_at}")

    def test_summary_all_flocks(self):
        """Test summary with all flocks includes records + overall"""
        response = self.client.get(FINANCE_SUMMARY_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        overall = response.data[-1]
        self.assertEqual(overall["batch_name"], "Overall")
        self.assertAlmostEqual(overall["total_expenses"], 8200.00, places=2)
        self.assertAlmostEqual(overall["total_revenue"], 7775.00, places=2)
        self.assertAlmostEqual(overall["profit_margin"], -425.00, places=2)

    def test_summary_filtered_by_flock(self):
        """Test summary filtered to one flock"""
        response = self.client.get(f"{FINANCE_SUMMARY_URL}?flock_id={self.flock1.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for record in response.data:
            if record["batch_name"] != "Overall":
                self.assertEqual(record["flock_id"], self.flock1.id)
        overall = response.data[-1]
        self.assertAlmostEqual(overall["total_expenses"], 3000.00, places=2)
        self.assertAlmostEqual(overall["total_revenue"], 2700.00, places=2)
        self.assertAlmostEqual(overall["profit_margin"], -300.00, places=2)

    def test_summary_filtered_by_date_range(self):
        today = timezone.now().date().isoformat()
        # print(f"Test today: {today}")
        # print(f"Record1 created_at: {self.record1.created_at}")
        # print(f"Record2 created_at: {self.record2.created_at}")
        response = self.client.get(f"{FINANCE_SUMMARY_URL}?start={today}&end={today}")
        # print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        non_overall = [r for r in response.data if r["batch_name"] != "Overall"]
        self.assertEqual(len(non_overall), 1)
        self.assertEqual(non_overall[0]["batch_name"], "Batch B")
        self.assertEqual(non_overall[0]["flock_id"], self.flock2.id)

    def test_summary_unauthenticated(self):
        """Test unauthenticated access is denied"""
        self.client.logout()
        response = self.client.get(FINANCE_SUMMARY_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_summary_empty_records(self):
        """Test summary for user with no records"""
        # Delete all records for the current user
        FinanceRecord.objects.filter(flock__user=self.user).delete()
        response = self.client.get(FINANCE_SUMMARY_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        overall = response.data[0]
        self.assertEqual(overall["batch_name"], "Overall")
        self.assertEqual(overall["total_expenses"], 0.00)
        self.assertEqual(overall["total_revenue"], 0.00)
        self.assertEqual(overall["profit_margin"], 0.00)
