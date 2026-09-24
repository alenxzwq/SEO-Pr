import datetime

from django.contrib import messages
from django.db.models import Avg, Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookingForm
from .models import FAQ, EventFormat, Hall, MenuPackage, Poster, Review


def home(request):
    reviews = Review.objects.filter(is_published=True)
    context = {
        "halls": Hall.objects.filter(is_active=True),
        "formats": EventFormat.objects.all()[:6],
        "packages": MenuPackage.objects.filter(is_featured=True)[:3],
        "reviews": reviews[:6],
        "rating": reviews.aggregate(avg=Avg("rating"))["avg"],
        "reviews_count": reviews.count(),
        "faqs": FAQ.objects.all(),
        "posters": upcoming_posters()[:6],
        "form": BookingForm(),
    }
    return render(request, "venue/home.html", context)


def hall_list(request):
    return render(request, "venue/hall_list.html", {
        "halls": Hall.objects.filter(is_active=True),
    })


def hall_detail(request, slug):
    """
    Страница зала. Коммерческая — должна быть в индексе.

    SEO-ЗАДАНИЕ (301-редирект): если пришёл старый URL /halls/1/,
    делаем постоянный редирект на новый /halls/depo/.
    """
    hall = Hall.objects.filter(slug=slug, is_active=True).first()

    if hall is None:
        if slug.isdigit():
            hall = get_object_or_404(Hall, pk=int(slug), is_active=True)
            return redirect("venue:hall_detail", slug=hall.slug, permanent=True)
        raise Http404("Зал не найден")

    others = Hall.objects.filter(is_active=True).exclude(pk=hall.pk)
    form = BookingForm(initial={"hall": hall})
    return render(request, "venue/hall_detail.html", {
        "hall": hall,
        "others": others,
        "form": form,
    })


def upcoming_posters():
    """Будущие события + регулярные (у них заполнено поле schedule)."""
    return Poster.objects.filter(is_published=True).filter(
        Q(date__gte=datetime.date.today()) | ~Q(schedule=""),
    )


def poster_list(request):
    return render(request, "venue/poster_list.html", {
        "posters": upcoming_posters(),
    })


def poster_detail(request, slug):
    """
    Страница события афиши.

    SEO-ЗАДАНИЕ (301-редирект): старые URL /afisha/1/ → /afisha/kviz-60-sekund/.

    SEO-ВОПРОС: что делать со страницей события, когда оно уже прошло?
    Ответ: оставить в архиве с пометкой «событие прошло» + предложить
    похожие будущие события. 404 или 410 — плохо, потому что теряется
    накопленный ссылочный вес и пользователи по старым ссылкам видят ошибку.
    """
    poster = Poster.objects.filter(slug=slug, is_published=True).first()

    if poster is None:
        if slug.isdigit():
            poster = get_object_or_404(Poster, pk=int(slug), is_published=True)
            return redirect("venue:poster_detail", slug=poster.slug, permanent=True)
        raise Http404("Событие не найдено")

    return render(request, "venue/poster_detail.html", {
        "poster": poster,
        "is_past": not poster.schedule and poster.date < datetime.date.today(),
    })


def menu(request):
    return render(request, "venue/menu.html", {
        "packages": MenuPackage.objects.all(),
    })


def events(request):
    return render(request, "venue/events.html", {
        "formats": EventFormat.objects.all(),
        "halls": Hall.objects.filter(is_active=True),
    })


def gallery(request):
    """
    SEO-ПОДСКАЗКА: у картинок нет alt — обязательно пропишите в шаблоне
    gallery.html: alt="{{ photo.caption }}".
    """
    photos = [
        {"src": "img/hall-depo.jpg", "caption": "Зал «Депо»"},
        {"src": "img/hall-tonnel.webp", "caption": "Зал «Тоннель»"},
        {"src": "img/hall-platforma.jpg", "caption": "Зал «Платформа»"},
        {"src": "img/hall-vestibul.jpg", "caption": "Бар «Вестибюль»"},
    ]
    return render(request, "venue/gallery.html", {"photos": photos})


def contacts(request):
    return render(request, "venue/contacts.html")


def booking(request):
    """
    SEO-ВОПРОС: нужна ли эта страница в поисковой выдаче?
    Ответ: нет, служебная. Закрываем через <meta name="robots" content="noindex, follow">
    в шаблоне booking.html. Disallow в robots.txt хуже — робот не зайдёт и не
    прочитает noindex, страница может попасть в индекс через внешние ссылки.
    """
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Заявка принята! Перезвоним в течение 15 минут.")
            return redirect("venue:booking")
    else:
        form = BookingForm(initial={
            "hall": request.GET.get("hall"),
            "comment": request.GET.get("comment", ""),
            "guests": request.GET.get("guests"),
        })
    return render(request, "venue/booking.html", {"form": form})


def robots_txt(request):
    """Отдаёт robots.txt с автоматически подставленным доменом."""
    sitemap_url = request.build_absolute_uri("/sitemap.xml")
    content = f"""User-agent: *
Disallow: /admin/
Disallow: /home/
Allow: /

Sitemap: {sitemap_url}
"""
    return HttpResponse(content, content_type="text/plain")