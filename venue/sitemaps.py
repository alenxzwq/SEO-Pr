from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Hall, Poster


class StaticViewSitemap(Sitemap):
    """Статические страницы: главная, залы, меню, форматы, афиша, галерея, контакты."""
    priority = 0.8


    def items(self):
        return [
            "venue:home",
            "venue:hall_list",
            "venue:menu",
            "venue:events",
            "venue:poster_list",
            "venue:gallery",
            "venue:contacts",
        ]

    def location(self, item):
        return reverse(item)


class HallSitemap(Sitemap):
    """Все активные залы."""
    priority = 0.9
    changefreq = "weekly"

    def items(self):
        return Hall.objects.filter(is_active=True)

    def lastmod(self, obj):
        return getattr(obj, "updated_at", None)


class PosterSitemap(Sitemap):
    """Опубликованные события афиши."""
    priority = 0.6
    changefreq = "daily"

    def items(self):
        return Poster.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.date