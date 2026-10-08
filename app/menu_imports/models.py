import uuid
from django.conf import settings
from django.db import models
from app.businesses.models import Business

class MenuImport(models.Model):
    class Status(models.TextChoices):
        UPLOADED = "uploaded", "Subido"
        PROCESSING = "processing", "Procesando"
        READY = "ready", "Listo para revisar"
        FAILED = "failed", "Falló"
        IMPORTED = "imported", "Importado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="menu_imports")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    source_file = models.FileField(upload_to="menu-imports/%Y/%m/")
    original_name = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=100)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.UPLOADED)
    draft = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
