import uuid
from django.db import models
from app.businesses.models import Business

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)
    sort_order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    class Meta:
        ordering = ["sort_order", "name"]
        constraints = [models.UniqueConstraint(fields=["business", "name"], name="unique_category_per_business")]
    def __str__(self): return self.name

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="products/", blank=True)
    active = models.BooleanField(default=True)
    available = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ["sort_order", "name"]
    def __str__(self): return self.name

class ProductOptionGroup(models.Model):
    class SelectionType(models.TextChoices):
        SINGLE = "single", "Una opción"
        MULTIPLE = "multiple", "Varias opciones"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="option_groups")
    name = models.CharField(max_length=100)
    selection_type = models.CharField(max_length=12, choices=SelectionType.choices, default=SelectionType.SINGLE)
    required = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]

class ProductOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(ProductOptionGroup, on_delete=models.CASCADE, related_name="options")
    name = models.CharField(max_length=100)
    price_delta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    available = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
