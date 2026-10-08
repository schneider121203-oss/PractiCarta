from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

User = get_user_model()

class AccountFlowTests(TestCase):
    def test_protected_pages_redirect_to_the_custom_login(self):
        response = self.client.get(reverse("businesses:dashboard"))
        self.assertRedirects(
            response,
            f'{reverse("login")}?next={reverse("businesses:dashboard")}',
        )

    def test_registration_uses_email_without_asking_for_username(self):
        response = self.client.get(reverse("register"))
        self.assertNotContains(response, 'name="username"')
        response = self.client.post(reverse("register"), {"email": "Owner@Example.com", "first_name": "Ana", "password1": "A-long-safe-password-2040", "password2": "A-long-safe-password-2040"})
        self.assertRedirects(response, reverse("businesses:create"))
        user = User.objects.get(email="owner@example.com")
        self.assertTrue(user.username.startswith("user-"))

    def test_password_reset_sends_link_without_disclosing_account(self):
        User.objects.create_user(email="owner@example.com", username="owner", password="A-long-safe-password-2040")
        response = self.client.post(reverse("password_reset"), {"email": "owner@example.com"})
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/recuperar/", mail.outbox[0].body)

    def test_profile_requires_login_and_can_be_updated(self):
        user = User.objects.create_user(email="owner@example.com", username="owner", password="A-long-safe-password-2040")
        self.assertEqual(self.client.get(reverse("profile")).status_code, 302)
        self.client.force_login(user)
        response = self.client.post(reverse("profile"), {"first_name": "Ana", "last_name": "Pérez", "email": "ana@example.com", "theme_preference": "dark"})
        self.assertRedirects(response, reverse("profile"))
        user.refresh_from_db(); self.assertEqual(user.email, "ana@example.com"); self.assertEqual(user.theme_preference, "dark")
