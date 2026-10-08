from django.urls import path
from . import views

app_name = "menu_imports"
urlpatterns = [path("", views.upload, name="upload"), path("<uuid:import_id>/reintentar/", views.retry, name="retry"), path("<uuid:import_id>/revisar/", views.review, name="review")]
