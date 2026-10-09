from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    class ThemePreference(models.TextChoices):
        SYSTEM = "system", "Según mi dispositivo"
        LIGHT = "light", "Modo claro"
        DARK = "dark", "Modo oscuro"

    email = models.EmailField(unique=True)
    theme_preference = models.CharField(max_length=10, choices=ThemePreference.choices, default=ThemePreference.SYSTEM)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]


class RequestLimit(models.Model):
    """Persistent counters for abuse controls; fingerprints never store raw IPs/emails."""
    scope = models.CharField(max_length=40)
    fingerprint = models.CharField(max_length=64)
    attempts = models.PositiveSmallIntegerField(default=0)
    window_started_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("scope", "fingerprint"), name="unique_request_limit")]
