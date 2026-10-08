import tempfile
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from app.businesses.models import Business
from app.catalog.models import Category, Product
from .models import MenuImport
from .services import MenuImportError, normalize_draft

User = get_user_model()

class MenuImportTests(TestCase):
    def setUp(self):
        self.media = tempfile.TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.media.name, GEMINI_API_KEY="", AWS_GEMINI_SECRET_ID="")
        self.override.enable()
        self.owner = User.objects.create_user(email="import@example.com", username="importer", password="safe-password-123")
        self.business = Business.objects.create(owner=self.owner, name="Importador", slug="importador", whatsapp_number="51999999999")
        self.client.force_login(self.owner)

    def tearDown(self):
        self.override.disable(); self.media.cleanup()

    def test_normalize_draft_filters_invalid_products(self):
        draft = normalize_draft({"categories": [{"name": "Bebidas", "products": [{"name": "Limonada", "description": "Vaso", "price": 8}, {"name": "Sin precio", "price": None}]}]})
        self.assertEqual(draft["categories"][0]["products"], [{"name": "Limonada", "description": "Vaso", "price": "8.00"}])

    def test_upload_without_api_key_fails_safely(self):
        source = SimpleUploadedFile("carta.pdf", b"%PDF-1.4\nmock", content_type="application/pdf")
        response = self.client.post(reverse("menu_imports:upload"), {"source_file": source})
        self.assertEqual(response.status_code, 200)
        job = MenuImport.objects.get()
        self.assertEqual(job.status, MenuImport.Status.FAILED)
        self.assertIn("GEMINI_API_KEY", job.error_message)

    def test_review_confirmation_creates_products_only_once(self):
        job = MenuImport.objects.create(
            business=self.business, created_by=self.owner,
            source_file=SimpleUploadedFile("menu.pdf", b"%PDF-1.4\nmock"), original_name="menu.pdf", mime_type="application/pdf",
            status=MenuImport.Status.READY,
            draft={"categories": [{"name": "Platos", "products": [{"name": "Ceviche", "description": "Clásico", "price": "29.90"}]}]},
        )
        payload = {"category_0_name": "Marinos", "product_0_0_include": "on", "product_0_0_name": "Ceviche clásico", "product_0_0_description": "Pesca del día", "product_0_0_price": "31.50"}
        response = self.client.post(reverse("menu_imports:review", args=[job.id]), payload)
        self.assertRedirects(response, reverse("businesses:dashboard"))
        self.assertTrue(Category.objects.filter(business=self.business, name="Marinos").exists())
        self.assertTrue(Product.objects.filter(name="Ceviche clásico", price="31.50").exists())
        self.client.post(reverse("menu_imports:review", args=[job.id]), payload)
        self.assertEqual(Product.objects.filter(name="Ceviche clásico").count(), 1)

    def test_import_is_tenant_scoped(self):
        other = User.objects.create_user(email="other-import@example.com", username="otherimport", password="safe-password-123")
        other_business = Business.objects.create(owner=other, name="Otro", slug="otro-import", whatsapp_number="51988888888")
        job = MenuImport.objects.create(business=other_business, created_by=other, source_file=SimpleUploadedFile("menu.pdf", b"%PDF-1.4"), original_name="menu.pdf", mime_type="application/pdf", status=MenuImport.Status.READY, draft={"categories": []})
        self.assertEqual(self.client.get(reverse("menu_imports:review", args=[job.id])).status_code, 404)
