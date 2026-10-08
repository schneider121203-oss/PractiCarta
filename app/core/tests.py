from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class HomeTests(TestCase):
    def test_home_renders_for_visitors(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tu carta lista para vender")
        self.assertContains(response, reverse("register"))

    def test_home_redirects_signed_in_user_to_dashboard(self):
        user = get_user_model().objects.create_user(email="home@example.com", username="home", password="safe-password-123")
        self.client.force_login(user)
        response = self.client.get(reverse("home"))
        self.assertRedirects(response, reverse("businesses:dashboard"), fetch_redirect_response=False)
