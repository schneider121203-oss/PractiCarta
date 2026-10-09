from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import ProfileForm, RegisterForm
from .rate_limits import clear, consume, fingerprint, is_limited

LOGIN_LIMIT, LOGIN_WINDOW_SECONDS = 3, 15 * 60
SIGNUP_LIMIT, RESET_LIMIT, HOUR_SECONDS = 5, 3, 60 * 60


class RateLimitedLoginView(LoginView):
    def dispatch(self, request, *args, **kwargs):
        self.limit_key = fingerprint(request, request.POST.get("username", "")) if request.method == "POST" else ""
        if request.method == "POST" and is_limited("login", self.limit_key, LOGIN_LIMIT, LOGIN_WINDOW_SECONDS):
            form = self.get_form()
            form.add_error(None, "Por seguridad, espera 15 minutos antes de volver a intentarlo.")
            return self.render_to_response(self.get_context_data(form=form))
        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        if self.limit_key:
            consume("login", self.limit_key, LOGIN_LIMIT, LOGIN_WINDOW_SECONDS)
        return super().form_invalid(form)

    def form_valid(self, form):
        if self.limit_key:
            clear("login", self.limit_key)
        return super().form_valid(form)


class RateLimitedPasswordResetView(PasswordResetView):
    def post(self, request, *args, **kwargs):
        key = fingerprint(request, request.POST.get("email", ""))
        if not consume("password_reset", key, RESET_LIMIT, HOUR_SECONDS):
            # Keep Django's neutral response: do not disclose an account or rate-limit state.
            return redirect("password_reset_done")
        return super().post(request, *args, **kwargs)

def register(request):
    if request.user.is_authenticated:
        return redirect("businesses:dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and not consume("registration", fingerprint(request, request.POST.get("email", "")), SIGNUP_LIMIT, HOUR_SECONDS):
        form.add_error(None, "Por seguridad, espera una hora antes de volver a registrarte.")
        return render(request, "registration/register.html", {"form": form})
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
