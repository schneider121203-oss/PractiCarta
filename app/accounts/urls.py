from django.contrib.auth import views as auth_views
from django.urls import path
from .views import RateLimitedLoginView, RateLimitedPasswordResetView, privacy, profile, register, terms
urlpatterns = [
    path("registro/", register, name="register"), path("ingresar/", RateLimitedLoginView.as_view(), name="login"), path("salir/", auth_views.LogoutView.as_view(), name="logout"),
    path("cuenta/", profile, name="profile"), path("cuenta/contrasena/", auth_views.PasswordChangeView.as_view(template_name="registration/password_change_form.html"), name="password_change"), path("cuenta/contrasena/listo/", auth_views.PasswordChangeDoneView.as_view(template_name="registration/password_change_done.html"), name="password_change_done"),
    path("recuperar/", RateLimitedPasswordResetView.as_view(template_name="registration/password_reset_form.html", email_template_name="registration/password_reset_email.txt"), name="password_reset"), path("recuperar/enviado/", auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"), name="password_reset_done"), path("recuperar/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), name="password_reset_confirm"), path("recuperar/completo/", auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"), name="password_reset_complete"),
    path("privacidad/", privacy, name="privacy"), path("terminos/", terms, name="terms"),
]
