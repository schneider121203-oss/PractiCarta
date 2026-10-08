import uuid
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.urls import reverse

HEX_COLOR_VALIDATOR = RegexValidator(r"^#[0-9a-fA-F]{6}$", "Usa un color hexadecimal válido, por ejemplo #1677c8.")


def _hex_color_parts(value):
    value = value.lstrip("#")
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


def _mix_color(value, target, weight):
    source_parts, target_parts = _hex_color_parts(value), _hex_color_parts(target)
    mixed = tuple(round(source + (destination - source) * weight) for source, destination in zip(source_parts, target_parts))
    return "#" + "".join(f"{channel:02x}" for channel in mixed)

class Business(models.Model):
    class MenuTheme(models.TextChoices):
        SYSTEM = "system", "Según el dispositivo del cliente"
        LIGHT = "light", "Modo claro"
        DARK = "dark", "Modo oscuro"

    class SubscriptionStatus(models.TextChoices):
        TRIAL = "trial", "En prueba"
        ACTIVE = "active", "Activo"
        PAYMENT_DUE = "payment_due", "Pago pendiente"
        SUSPENDED = "suspended", "Suspendido"
        CANCELED = "canceled", "Cancelado"

    class BrandPalette(models.TextChoices):
        SUNSET = "sunset", "Naranja cálido"
        OCEAN = "ocean", "Azul océano"
        FOREST = "forest", "Verde bosque"
        GRAPE = "grape", "Morado uva"
        ROSE = "rose", "Rosa coral"
        CUSTOM = "custom", "Color personalizado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="businesses")
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, max_length=140)
    description = models.TextField(blank=True)
    greeting_message = models.CharField(max_length=160, blank=True)
    whatsapp_number = models.CharField(max_length=20, help_text="Código de país incluido. Ej.: 51999999999")
    primary_color = models.CharField(max_length=7, default="#ea580c", validators=[HEX_COLOR_VALIDATOR])
    secondary_color = models.CharField(max_length=7, default="#18211d", validators=[HEX_COLOR_VALIDATOR])
    brand_palette = models.CharField(max_length=16, choices=BrandPalette.choices, default=BrandPalette.SUNSET)
    menu_theme = models.CharField(max_length=10, choices=MenuTheme.choices, default=MenuTheme.SYSTEM)
    logo = models.ImageField(upload_to="logos/", blank=True)
    cover_image = models.ImageField(upload_to="covers/", blank=True)
    pickup_enabled = models.BooleanField(default=True)
    delivery_enabled = models.BooleanField(default=False)
    dine_in_enabled = models.BooleanField(default=False)
    address = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, validators=[MinValueValidator(-180), MaxValueValidator(180)])
    is_published = models.BooleanField(default=True)
    subscription_status = models.CharField(max_length=16, choices=SubscriptionStatus.choices, default=SubscriptionStatus.TRIAL)
    subscription_expires_at = models.DateField(null=True, blank=True)
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "businesses"

    def __str__(self): return self.name
    def get_absolute_url(self): return reverse("catalog:menu", kwargs={"slug": self.slug})

    @property
    def brand_dark_color(self):
        return _mix_color(self.primary_color, "#000000", 0.22)

    @property
    def brand_soft_color(self):
        return _mix_color(self.primary_color, "#ffffff", 0.90)

    @property
    def brand_contrast_color(self):
        red, green, blue = _hex_color_parts(self.primary_color)
        return "#18211d" if (red * 299 + green * 587 + blue * 114) / 1000 > 155 else "#ffffff"

    @property
    def secondary_contrast_color(self):
        red, green, blue = _hex_color_parts(self.secondary_color)
        return "#18211d" if (red * 299 + green * 587 + blue * 114) / 1000 > 155 else "#ffffff"

    @property
    def maps_url(self):
        if self.latitude is None or self.longitude is None:
            return ""
        return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
