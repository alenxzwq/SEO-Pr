from django.contrib import admin
from django.urls import include, path
from django.contrib.sitemaps.views import sitemap

from venue.views import robots_txt
from venue.sitemaps import StaticViewSitemap, HallSitemap, PosterSitemap


sitemaps = {
    "static": StaticViewSitemap,
    "halls": HallSitemap,
    "posters": PosterSitemap,
}


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("venue.urls")),

    path("robots.txt", robots_txt, name="robots_txt"),

    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]