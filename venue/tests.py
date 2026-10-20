"""
Автотесты сайта. Запуск: python manage.py test

ПОДСКАЗКА: когда будете делать SEO-задания, допишите сюда свои тесты, например:
  - /robots.txt отвечает 200 и содержит строку «Sitemap:»;
  - /sitemap.xml отвечает 200 и не содержит /booking/;
  - /home/ и /halls/1/ отдают 301;
  - на каждой странице ровно один <h1>.
"""

import datetime
import io
from unittest import mock

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import BookingRequest, Hall, Poster


def aware_utc(*args):
    """datetime с явным UTC — для подмены django.utils.timezone.now в тестах."""
    return datetime.datetime(*args, tzinfo=datetime.timezone.utc)


class SiteTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", stdout=io.StringIO())


class PagesTest(SiteTestCase):
    def test_static_pages_ok(self):
        for name in ["home", "hall_list", "menu", "events", "gallery", "contacts", "booking", "poster_list"]:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(f"venue:{name}")).status_code, 200)

    def test_every_hall_and_poster_page_ok(self):
        for obj in [*Hall.objects.all(), *Poster.objects.all()]:
            with self.subTest(url=obj.get_absolute_url()):
                self.assertEqual(self.client.get(obj.get_absolute_url()).status_code, 200)

    def test_inactive_hall_is_404(self):
        hall = Hall.objects.first()
        hall.is_active = False
        hall.save()
        self.assertEqual(self.client.get(hall.get_absolute_url()).status_code, 404)

    def test_admin_login_works(self):
        self.assertTrue(self.client.login(username="admin", password="podzemka2026"))


class BookingTest(SiteTestCase):
    def form_data(self, **overrides):
        data = {
            "name": "Тест", "phone": "+7 (900) 000-00-00",
            "date": (datetime.date.today() + datetime.timedelta(days=30)).isoformat(),
            "guests": 50, "hall": Hall.objects.first().pk,
        }
        data.update(overrides)
        return data

    def test_booking_is_saved(self):
        response = self.client.post(reverse("venue:booking"), self.form_data(), follow=True)
        self.assertEqual(BookingRequest.objects.count(), 1)
        self.assertContains(response, "Заявка принята")

    def test_past_date_is_rejected(self):
        self.client.post(reverse("venue:booking"), self.form_data(date="2020-01-01"))
        self.assertEqual(BookingRequest.objects.count(), 0)

    def test_calculator_prefills_form(self):
        response = self.client.get(reverse("venue:booking"), {"guests": 120, "comment": "Расчёт с сайта"})
        self.assertContains(response, 'value="120"')
        self.assertContains(response, "Расчёт с сайта")


class PromoAndPosterTest(SiteTestCase):
    @override_settings(PROMO={**settings.PROMO, "until": "2026-10-01"})
    def test_promo_deadline_by_chita_time(self):
        """DEVOPS: граница акции считается по Чите, а не по UTC контейнера."""
        # 1 октября 20:00 UTC — это уже 2 октября 05:00 по Чите → акция скрыта
        with mock.patch("django.utils.timezone.now", return_value=aware_utc(2026, 10, 1, 20)):
            response = self.client.get(reverse("venue:home"))
        self.assertIsNone(response.context["promo"])
        # 1 октября 10:00 UTC (19:00 по Чите) — ещё показывается
        with mock.patch("django.utils.timezone.now", return_value=aware_utc(2026, 10, 1, 10)):
            response = self.client.get(reverse("venue:home"))
        self.assertIsNotNone(response.context["promo"])

    def test_past_poster_not_listed_but_regular_is(self):
        past = Poster.objects.create(
            title="Прошедшее", date=datetime.date(2020, 1, 1), short_description="-",
        )
        regular = Poster.objects.create(
            title="Регулярное", date=datetime.date(2020, 1, 1), schedule="Каждый день", short_description="-",
        )
        posters = list(self.client.get(reverse("venue:poster_list")).context["posters"])
        self.assertNotIn(past, posters)
        self.assertIn(regular, posters)