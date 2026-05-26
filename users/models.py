from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    PERSONAL = "PERSONAL"
    BUSINESS = "BUSINESS"
    ACCESS_CONTEXT_CHOICES = (
        (PERSONAL, "Personal"),
        (BUSINESS, "Business"),
    )

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    access_context = models.CharField(max_length=20, choices=ACCESS_CONTEXT_CHOICES)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "access_context"]

    objects = CustomUserManager()

    def clean(self):
        super().clean()
        if self.access_context not in {self.PERSONAL, self.BUSINESS}:
            raise ValidationError({"access_context": "Choose Personal or Business access."})

    @property
    def is_personal(self):
        return self.access_context == self.PERSONAL

    @property
    def is_business(self):
        return self.access_context == self.BUSINESS

    def __str__(self):
        return self.username or self.email
