from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from djangoql.admin import DjangoQLSearchMixin
from import_export.admin import ExportActionModelAdmin, ImportExportActionModelAdmin

from tickets.models import Venue, ConcertCategory, Concert, Ticket


class ConcertInline(admin.TabularInline):
    model = Concert
    fields = ["name", "starts_at", "price", "tickets_left"]
    readonly_fields = ["name", "starts_at", "price", "tickets_left"]
    max_num = 0
    extra = 0
    can_delete = False
    show_change_link = True


class ConcertThroughInline(admin.TabularInline):
    verbose_name = "concert"
    verbose_name_plural = "concerts"
    model = Concert.categories.through
    fields = ["concert"]
    readonly_fields = ["concert"]
    max_num = 0
    extra = 0
    can_delete = False
    show_change_link = True


class VenueAdmin(admin.ModelAdmin):
    list_display = ["name", "address", "capacity"]
    inlines = [ConcertInline]


class ConcertCategoryAdmin(admin.ModelAdmin):
    inlines = [ConcertThroughInline]


class SoldOutFilter(SimpleListFilter):
    title = "Sold out"
    parameter_name = "sold_out"

    def lookups(self, request, model_admin):
        return [
            ("yes", "Yes"),
            ("no", "No"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(tickets_left=0)
        else:
            return queryset.exclude(tickets_left=0)


class ConcertAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    list_display = ["name", "venue", "starts_at", "display_price", "tickets_left", "display_sold_out"]
    list_filter = ["venue", SoldOutFilter]
    readonly_fields = ["tickets_left"]
    search_fields = ["name", "venue__name", "venue__address"]

    def display_sold_out(self, obj):
        return obj.is_sold_out()

    display_sold_out.short_description = "Sold out"
    display_sold_out.boolean = True

    def display_price(self, obj):
        return f"${obj.price}"

    display_price.short_description = "Price"
    display_price.admin_order_field = "price"


@admin.action(description="Activate selected tickets")
def activate_tickets(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description="Deactivate selected tickets")
def deactivate_tickets(modeladmin, request, queryset):
    queryset.update(is_active=False)


class TicketAdmin(ImportExportActionModelAdmin):
    list_display = ["customer_full_name", "concert", "payment_method", "paid_at", "is_active"]
    list_filter = ["payment_method", "paid_at", "is_active"]
    actions = [activate_tickets, deactivate_tickets]


admin.site.register(Venue, VenueAdmin)
admin.site.register(ConcertCategory, ConcertCategoryAdmin)
admin.site.register(Concert, ConcertAdmin)
admin.site.register(Ticket, TicketAdmin)
