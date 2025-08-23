from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError
import os


class Command(createsuperuser.Command):
    help = "Create a superuser with a password from environment variables"

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not all([username, email, password]):
            raise CommandError(
                "DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD must be set in environment variables."
            )

        if self.UserModel.objects.filter(username=username).exists():
            self.stdout.write(
                f"Superuser {username} already exists, skipping creation."
            )
            return

        self.UserModel.objects.create_superuser(
            username=username, email=email, password=password
        )
        self.stdout.write(f"Superuser {username} created successfully.")
