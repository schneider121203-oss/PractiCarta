from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class ThemePreference(models.TextChoices):
        SYSTEM = "system", "Según mi dispositivo"
        LIGHT = "light", "Modo claro"
        DARK = "dark", "Modo oscuro"

    email = models.EmailField(unique=True)
    theme_preference = models.CharField(max_length=10, choices=ThemePreference.choices, default=ThemePreference.SYSTEM)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
