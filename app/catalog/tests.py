import json
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from app.analytics.models import AnalyticsEvent
from app.businesses.models import Business
from app.businesses.forms import BusinessForm
from .models import Category, Product, ProductOption, ProductOptionGroup

User = get_user_model()

class CatalogFlowTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email="owner@example.com", username="owner", password="safe-password-123")
        self.other = User.objects.create_user(email="other@example.com", username="other", password="safe-password-123")
        self.business = Business.objects.create(owner=self.owner, name="Café Norte", slug="cafe-norte", whatsapp_number="51999999999")
        self.category = Category.objects.create(business=self.business, name="Cafés")
        self.product = Product.objects.create(category=self.category, name="Capuccino", price="12.50")

    def test_public_menu_only_shows_available_active_products(self):
        hidden = Product.objects.create(category=self.category, name="No visible", price="4.00", active=False)
        response = self.client.get(reverse("catalog:menu", args=[self.business.slug]))
        self.assertContains(response, "Capuccino")
        self.assertContains(response, 'data-price="12.50"')
        self.assertNotContains(response, hidden.name)
        self.assertEqual(AnalyticsEvent.objects.filter(event_type="menu_view").count(), 1)

    def test_dashboard_renders_categories_products_and_setup(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("businesses:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cafés")
        self.assertContains(response, "Capuccino")

    def test_checkout_uses_server_price_and_creates_whatsapp_event(self):
        response = self.client.post(reverse("catalog:checkout", args=[self.business.slug]), data=json.dumps({"items": [{"id": str(self.product.id), "quantity": 2, "price": 0.01}]}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("S/ 25.00", response.json()["text"])
        self.assertEqual(AnalyticsEvent.objects.filter(event_type="whatsapp_click").count(), 1)

    def test_checkout_validates_options_and_modality_on_server(self):
        group = ProductOptionGroup.objects.create(product=self.product, name="Tamaño", required=True)
        option = ProductOption.objects.create(group=group, name="Grande", price_delta="3.50")
        url = reverse("catalog:checkout", args=[self.business.slug])
        missing = self.client.post(url, data=json.dumps({"items": [{"id": str(self.product.id), "quantity": 1}], "order_type": "pickup"}), content_type="application/json")
        self.assertEqual(missing.status_code, 400)
        self.business.delivery_enabled = True; self.business.save(update_fields=["delivery_enabled"])
        response = self.client.post(url, data=json.dumps({"items": [{"id": str(self.product.id), "quantity": 2, "options": [str(option.id)]}], "order_type": "delivery", "delivery_address": "Puerta negra", "customer_note": "Sin azúcar", "location": {"latitude": -12.119142, "longitude": -77.034904}}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("S/ 32.00", response.json()["text"])
        self.assertIn("Tamaño: Grande", response.json()["text"])
        self.assertIn("Modalidad: Delivery", response.json()["text"])
        self.assertIn("Ubicación compartida por el cliente: https://www.google.com/maps?q=-12.119142,-77.034904", response.json()["text"])
        self.assertIn("Dirección/referencia: Puerta negra", response.json()["text"])
        self.assertIn("Indicaciones: Sin azúcar", response.json()["text"])

    def test_delivery_requires_location_or_manual_address(self):
        self.business.delivery_enabled = True; self.business.save(update_fields=["delivery_enabled"])
        url = reverse("catalog:checkout", args=[self.business.slug])
        payload = {"items": [{"id": str(self.product.id), "quantity": 1}], "order_type": "delivery"}
        self.assertEqual(self.client.post(url, data=json.dumps(payload), content_type="application/json").status_code, 400)
        payload["delivery_address"] = "Av. Principal 123"
        self.assertEqual(self.client.post(url, data=json.dumps(payload), content_type="application/json").status_code, 200)

    def test_checkout_rejects_oversized_notes_and_invalid_coordinates(self):
        self.business.delivery_enabled = True; self.business.save(update_fields=["delivery_enabled"])
        url = reverse("catalog:checkout", args=[self.business.slug])
        base = {"items": [{"id": str(self.product.id), "quantity": 1}], "order_type": "delivery", "delivery_address": "Referencia"}
        oversized = {**base, "customer_note": "x" * 401}
        invalid_location = {**base, "location": {"latitude": 100, "longitude": -77}}
        self.assertEqual(self.client.post(url, data=json.dumps(oversized), content_type="application/json").status_code, 400)
        self.assertEqual(self.client.post(url, data=json.dumps(invalid_location), content_type="application/json").status_code, 400)

    def test_public_location_section_and_optional_pickup_location(self):
        self.business.address = "Av. Norte 123"
        self.business.latitude = "-12.119142"
        self.business.longitude = "-77.034904"
        self.business.save(update_fields=["address", "latitude", "longitude"])
        menu = self.client.get(reverse("catalog:menu", args=[self.business.slug]))
        self.assertContains(menu, "Encuentra el camino más fácil")
        self.assertContains(menu, "Abrir en Google Maps")
        payload = {"items": [{"id": str(self.product.id), "quantity": 1}], "order_type": "pickup", "location": {"latitude": -12.1, "longitude": -77.03}}
        response = self.client.post(reverse("catalog:checkout", args=[self.business.slug]), data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Ubicación compartida por el cliente: https://www.google.com/maps?q=-12.100000,-77.030000", response.json()["text"])

    def test_public_menu_shows_clean_openstreetmap_map_with_coordinates(self):
        self.business.address = "Av. Norte 123"
        self.business.latitude = "-12.119142"
        self.business.longitude = "-77.034904"
        self.business.save(update_fields=["address", "latitude", "longitude"])
        response = self.client.get(reverse("catalog:menu", args=[self.business.slug]))
        self.assertContains(response, "MAPA DEL LOCAL")
        self.assertContains(response, "unpkg.com/leaflet@1.9.4")
        self.assertContains(response, 'data-latitude="-12.119142"')
        self.assertContains(response, "colaboradores de OpenStreetMap")
        self.assertNotContains(response, "Reportar un problema")

    def test_qr_download_is_png_for_public_menu(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("businesses:download_qr"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertGreater(len(response.content), 100)

    def test_owner_cannot_edit_another_tenant_product(self):
        other_business = Business.objects.create(owner=self.other, name="Otro", slug="otro", whatsapp_number="51988888888")
        category = Category.objects.create(business=other_business, name="Comida")
        foreign_product = Product.objects.create(category=category, name="Secreto", price="10")
        self.client.force_login(self.owner)
        response = self.client.get(reverse("businesses:product_edit", args=[foreign_product.id]))
        self.assertEqual(response.status_code, 404)

    def test_product_flow_requires_category_and_continues_after_creating_it(self):
        new_owner = User.objects.create_user(email="new@example.com", username="new", password="safe-password-123")
        Business.objects.create(owner=new_owner, name="Nuevo", slug="nuevo", whatsapp_number="51977777777")
        self.client.force_login(new_owner)
        response = self.client.get(reverse("businesses:product_add"))
        self.assertRedirects(response, f'{reverse("businesses:category_add")}?next=product', fetch_redirect_response=False)
        response = self.client.post(f'{reverse("businesses:category_add")}?next=product', {"name": "Bebidas", "sort_order": 0, "active": True})
        self.assertRedirects(response, reverse("businesses:product_add"))
        self.assertContains(self.client.get(reverse("businesses:product_add")), "Bebidas")

    def test_owner_cannot_edit_another_tenant_category(self):
        other_business = Business.objects.create(owner=self.other, name="Otro local", slug="otro-local", whatsapp_number="51988888888")
        foreign_category = Category.objects.create(business=other_business, name="Privada")
        self.client.force_login(self.owner)
        response = self.client.get(reverse("businesses:category_edit", args=[foreign_category.id]))
        self.assertEqual(response.status_code, 404)

    def test_option_group_can_be_reused_without_crossing_tenants(self):
        source_product = Product.objects.create(category=self.category, name="Latte", price="14.00")
        source_group = ProductOptionGroup.objects.create(product=source_product, name="Tamaño", required=True)
        ProductOption.objects.create(group=source_group, name="Grande", price_delta="3.00")
        self.client.force_login(self.owner)
        response = self.client.post(reverse("businesses:product_options_copy", args=[self.product.id]), {"group_id": source_group.id})
        self.assertRedirects(response, reverse("businesses:product_edit", args=[self.product.id]))
        copied = self.product.option_groups.get(name="Tamaño")
        self.assertEqual(copied.options.get().name, "Grande")

        foreign_business = Business.objects.create(owner=self.other, name="Ajeno", slug="ajeno-opciones", whatsapp_number="51988888888")
        foreign_category = Category.objects.create(business=foreign_business, name="Privada")
        foreign_product = Product.objects.create(category=foreign_category, name="Secreto", price="20.00")
        foreign_group = ProductOptionGroup.objects.create(product=foreign_product, name="Privado")
        denied = self.client.post(reverse("businesses:product_options_copy", args=[self.product.id]), {"group_id": foreign_group.id})
        self.assertEqual(denied.status_code, 404)

    def test_business_link_accepts_spaces_and_generates_a_safe_url(self):
        form = BusinessForm(data={
            "name": "Pollería El Sol", "slug": "Pollería El Sol", "description": "",
            "greeting_message": "Hoy provoca pollito", "whatsapp_number": "51999999998", "brand_palette": "ocean", "primary_color": "#000000", "secondary_color": "#111111",
            "pickup_enabled": True, "delivery_enabled": False, "dine_in_enabled": False, "address": "Av. Uno 123", "latitude": "-12.100000", "longitude": "-77.030000", "is_published": True,
        })
        self.assertTrue(form.is_valid(), form.errors)
        business = form.save(commit=False); business.owner = self.other; business.save()
        self.assertEqual(business.slug, "polleria-el-sol")
        self.assertEqual(business.primary_color, "#1677c8")
        self.assertEqual(business.secondary_color, "#16344d")
        self.assertEqual(business.menu_theme, "system")
        self.assertEqual(business.greeting_message, "Hoy provoca pollito")
        self.client.force_login(self.owner)
        response = self.client.get(reverse("businesses:edit"))
        self.assertContains(response, "Enlace de tu carta")
        self.assertContains(response, "Puedes escribir con espacios")

    def test_operations_backoffice_requires_staff_and_shows_client_metrics(self):
        AnalyticsEvent.objects.create(business=self.business, event_type="menu_view")
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(reverse("businesses:operations_dashboard")).status_code, 302)
        self.owner.is_staff = True; self.owner.save(update_fields=["is_staff"])
        response = self.client.get(reverse("businesses:operations_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.business.name)
        self.assertContains(response, "Clientes y cobros")
