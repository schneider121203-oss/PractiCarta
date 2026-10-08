from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import ProfileForm, RegisterForm

def register(request):
    if request.user.is_authenticated:
        return redirect("businesses:dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("businesses:create")
    return render(request, "registration/register.html", {"form": form})

@login_required
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save(); messages.success(request, "Tu perfil fue actualizado."); return redirect("profile")
    return render(request, "accounts/profile.html", {"form": form})

def privacy(request): return render(request, "legal/privacy.html")
def terms(request): return render(request, "legal/terms.html")
