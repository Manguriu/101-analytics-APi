"test for flock api"

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import date


from core.models import Flock
from flock.serializers import (
    FlockSerializer,
    FlockDetailSerializer,
)

FLOCKS_URL = reverse("flock:flock-list")


def detail_url(flock_id):
    "create and return a flock detail URL"
    return reverse("flock:flock-detail", args=[flock_id])


"helper function to create flock"


def create_flock(user, **params):
    "create and retun sample flocks"
    defaults = {
        "batch_name": "Test Batch",
        "date_acquired": "2025-06-01",
        "initial_count": 100,
        "breed": "Broiler",
    }
    defaults.update(params)

    flock = Flock.objects.create(user=user, **defaults)
    return flock


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicFlockAPITests(TestCase):
    "Test authenticated API requests"

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        "test auth is required to call API"
        res = self.client.get(FLOCKS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateFlockApiTests(TestCase):
    "test authenticated api request"

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="user@example.com", password="testpass123")
        self.client.force_authenticate(self.user)

    def test_retrieve_flocks(self):
        create_flock(user=self.user)
        create_flock(user=self.user)

        res = self.client.get(FLOCKS_URL)

        flocks = Flock.objects.all().order_by("-id")
        serializer = FlockSerializer(flocks, many=True)
        self.assertTrue(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_flock_list_limited_to_user(self):
        """Test list of flocks is limited to authenticated user."""
        other_user = create_user(email="other@example.com", password="test123")
        create_flock(user=other_user)
        create_flock(user=self.user)

        res = self.client.get(FLOCKS_URL)

        flocks = Flock.objects.filter(user=self.user)
        serializer = FlockSerializer(flocks, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_flock_detail(self):
        """Test get recipe detail."""
        flock = create_flock(user=self.user)

        url = detail_url(flock.id)
        res = self.client.get(url)

        serializer = FlockDetailSerializer(flock)
        self.assertEqual(res.data, serializer.data)

    def test_create_flock(self):
        """Test creating a flock."""
        payload = {
            "batch_name": "Test Batch 1",
            "date_acquired": "2025-06-01",
            "initial_count": 100,
            "breed": "Broiler",
        }
        res = self.client.post(FLOCKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        flock = Flock.objects.get(id=res.data["id"])

        # fields checks to handle type conversion
        self.assertEqual(flock.batch_name, payload["batch_name"])
        self.assertEqual(flock.initial_count, payload["initial_count"])
        self.assertEqual(flock.breed, payload["breed"])
        self.assertEqual(
            flock.date_acquired, date.fromisoformat(payload["date_acquired"])
        )
        self.assertEqual(flock.user, self.user)

    def test_partial_update(self):
        """Test partial update of a flock."""
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
        """Test full update of flock."""
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
        """Test changing the flock user results in an error."""
        new_user = create_user(email="user2@example.com", password="test123")
        flock = create_flock(user=self.user)

        payload = {"user": new_user.id}
        url = detail_url(flock.id)
        res = self.client.patch(url, payload)

        flock.refresh_from_db()
        self.assertEqual(flock.user, self.user)

    def test_delete_flock(self):
        """Test deleting a flock successful."""
        flock = create_flock(user=self.user)

        url = detail_url(flock.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Flock.objects.filter(id=flock.id).exists())

    def test_flock_other_users_flock_error(self):
        """Test trying to delete another user's flock gives error."""
        new_user = create_user(email="user2@example.com", password="test123")
        flock = create_flock(user=new_user)

        url = detail_url(flock.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Flock.objects.filter(id=flock.id).exists())
