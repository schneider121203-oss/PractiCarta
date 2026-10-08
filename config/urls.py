from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from app.core.views import health, home

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("health/", health, name="health"),
    path("", include("app.accounts.urls")),
    path("dashboard/", include("app.businesses.urls")),
    path("dashboard/importar/", include("app.menu_imports.urls")),
    path("", include("app.catalog.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
