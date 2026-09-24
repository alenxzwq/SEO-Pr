from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "venue"

urlpatterns = [
    path("", views.home, name="home"),

    path(
        "home/",
        RedirectView.as_view(url="/", permanent=True),
        name="home_duplicate",
    ),

    path("halls/", views.hall_list, name="hall_list"),
    path("halls/<slug:slug>/", views.hall_detail, name="hall_detail"),

    path("menu/", views.menu, name="menu"),
    path("events/", views.events, name="events"),
    path("afisha/", views.poster_list, name="poster_list"),
    path("afisha/<slug:slug>/", views.poster_detail, name="poster_detail"),

    path("gallery/", views.gallery, name="gallery"),
    path("contacts/", views.contacts, name="contacts"),
    path("booking/", views.booking, name="booking"),
]