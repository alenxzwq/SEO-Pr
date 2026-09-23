from django.contrib import admin

from .models import FAQ, BookingRequest, EventFormat, Hall, MenuPackage, Poster, Review


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ("name", "line_number", "capacity_banquet", "area", "price_from", "order", "is_active")
    list_editable = ("order", "is_active")
    # ПОДСКАЗКА: когда добавите поле slug, раскомментируйте —
    # slug будет заполняться автоматически при вводе названия:
    # prepopulated_fields = {"slug": ("name",)}
    # Внимание: автозаполнение транслитерирует кириллицу — проверьте результат!


@admin.register(Poster)
class PosterAdmin(admin.ModelAdmin):
    list_display = ("title", "topic", "date", "time", "schedule", "is_published")
    list_filter = ("is_published",)
    list_editable = ("is_published",)
    date_hierarchy = "date"


@admin.register(EventFormat)
class EventFormatAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "order")
    list_editable = ("order",)


@admin.register(MenuPackage)
class MenuPackageAdmin(admin.ModelAdmin):
    list_display = ("name", "price_per_person", "is_featured", "order")
    list_editable = ("is_featured", "order")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("author", "event", "rating", "created_at", "is_published")
    list_filter = ("is_published", "rating")
    list_editable = ("is_published",)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "order")
    list_editable = ("order",)


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "date", "guests", "hall", "status", "created_at")
    list_filter = ("status", "hall", "date")
    list_editable = ("status",)
    search_fields = ("name", "phone", "comment")
    readonly_fields = ("created_at",)


admin.site.site_header = "Подземка — управление"
admin.site.site_title = "Подземка"
admin.site.index_title = "Контент сайта и заявки"
