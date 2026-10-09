import hashlib
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import RequestLimit


def client_ip(request):
    # Caddy sets X-Forwarded-For before proxying to Django.
    return request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "")).split(",")[0].strip()


def fingerprint(request, value):
    material = f"{settings.SECRET_KEY}:{client_ip(request)}:{value.strip().lower()}"
    return hashlib.sha256(material.encode()).hexdigest()


def is_limited(scope, key, limit, seconds):
    entry = RequestLimit.objects.filter(scope=scope, fingerprint=key).first()
    if not entry:
        return False
    if timezone.now() - entry.window_started_at >= timedelta(seconds=seconds):
        entry.delete()
        return False
    return entry.attempts >= limit


def consume(scope, key, limit, seconds):
    """Record one protected action. Returns False once its window is exhausted."""
    now = timezone.now()
    with transaction.atomic():
        entry, _ = RequestLimit.objects.select_for_update().get_or_create(
            scope=scope, fingerprint=key, defaults={"attempts": 0, "window_started_at": now},
        )
        if now - entry.window_started_at >= timedelta(seconds=seconds):
            entry.attempts, entry.window_started_at = 0, now
        if entry.attempts >= limit:
            return False
        entry.attempts += 1
        entry.save(update_fields=("attempts", "window_started_at", "updated_at"))
    return True


def clear(scope, key):
    RequestLimit.objects.filter(scope=scope, fingerprint=key).delete()
