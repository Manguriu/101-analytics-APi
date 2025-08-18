"""Test user models"""

# from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from poultry.core import models


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """test creating a user with an email success"""
        email = "test@example.com"
        password = "testpass1234"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "sample123")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "test123")

    def test_create_superuser(self):
        """testing creating super user"""
        user = get_user_model().objects.create_superuser("test@example.com", "test123")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_flock(self):
        "test creating flock is successful"
        user = get_user_model().objects.create_user(
            "test@example.com",
            "testpass123",
        )
        flock = models.Flock.objects.create(
            user=user,
            batch_name="Layer Batch A",
            date_acquired="2025-06-01",
            initial_count=200,
            breed="Kienyeji",
        )
        self.assertIsNotNone(flock.batch_id)
        self.assertEqual(len(flock.batch_id), 20)
        self.assertTrue(flock.batch_id.isalnum())
        # self.assertEqual(str(flock), flock.batch_name)
        # self.assertRegex(flock.batch_id, r"^[a-f0-9\-]{36}$")
