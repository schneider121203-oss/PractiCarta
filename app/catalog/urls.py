from django.urls import path
from . import views
app_name = "catalog"
urlpatterns = [path("m/<slug:slug>/", views.menu, name="menu"), path("m/<slug:slug>/checkout/", views.checkout, name="checkout"), path("m/<slug:slug>/event/", views.event, name="event")]
