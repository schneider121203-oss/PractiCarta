import uuid
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "password1", "password2")
        labels = {"email": "Correo electrónico", "first_name": "Tu nombre"}

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].strip().lower()
        user.username = f"user-{uuid.uuid4().hex}"
        if commit: user.save()
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "theme_preference")
        labels = {"first_name": "Nombre", "last_name": "Apellidos", "email": "Correo electrónico", "theme_preference": "Apariencia"}
        help_texts = {"theme_preference": "Puedes cambiarla cuando quieras; no afecta la carta que ven tus clientes."}

    def clean_email(self): return self.cleaned_data["email"].strip().lower()
