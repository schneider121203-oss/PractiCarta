import uuid
from django.db import models
from app.businesses.models import Business
from app.catalog.models import Product

class AnalyticsEvent(models.Model):
    TYPES = [(x, x) for x in ("menu_view", "add_to_cart", "whatsapp_click")]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="events")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=32, choices=TYPES)
    session_id = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: indexes = [models.Index(fields=["business", "event_type", "created_at"])]
