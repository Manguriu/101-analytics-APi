"""database models"""

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
import uuid


class UserManger(BaseUserManager):
    """manager for users"""

    def create_user(self, email, password=None, **extra_fields):
        """create save and return a new user"""
        if not email:
            raise ValueError("User must have an email address")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """create and return new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """user in the system"""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManger()

    USERNAME_FIELD = "email"


def generate_batch_id():
    return uuid.uuid4().hex[:20]


class Flock(models.Model):
    "Flock oject"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    batch_id = models.CharField(
        max_length=20, unique=True, editable=False, default=generate_batch_id
    )
    batch_name = models.CharField(max_length=255)
    date_acquired = models.DateField()
    initial_count = models.PositiveIntegerField()
    breed = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ["-date_acquired"]

    def __str__(self):
        return f"{self.batch_name} ({self.batch_id})"
