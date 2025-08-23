from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError
import os
import logging

logger = logging.getLogger(__name__)


class Command(createsuperuser.Command):
    help = "Create a superuser with a password from environment variables"

    def handle(self, *args, **options):
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        logger.info(f"Email: {email}, Password: {password}")  # Debug log

        if not all([email, password]):
            raise CommandError(
                "DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD must be set in environment variables."
            )

        # Check if a user with the email already exists
        if self.UserModel.objects.filter(email=email).exists():
            self.stdout.write(
                f"Superuser with email {email} already exists, skipping creation."
            )
            return

        # Create the superuser using email and password
        self.UserModel.objects.create_superuser(email=email, password=password)
        self.stdout.write(f"Superuser with email {email} created successfully.")
