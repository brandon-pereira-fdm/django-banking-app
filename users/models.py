from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    PERSONAL = "PERSONAL"
    BUSINESS_EMPLOYEE = "BUSINESS_EMPLOYEE"
    LOGIN_CONTEXT_CHOICES = (
        (PERSONAL, "Personal"),
        (BUSINESS_EMPLOYEE, "Business Employee"),
    )

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    login_context = models.CharField(max_length=24, choices=LOGIN_CONTEXT_CHOICES)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "login_context"]

    objects = CustomUserManager()

    def clean(self):
        super().clean()
        if self.login_context not in {self.PERSONAL, self.BUSINESS_EMPLOYEE}:
            raise ValidationError({"login_context": "Choose Personal or Business Employee access."})

    @property
    def is_personal(self):
        return self.login_context == self.PERSONAL

    @property
    def is_business(self):
        return self.login_context == self.BUSINESS_EMPLOYEE

    def __str__(self):
        return self.username or self.email
