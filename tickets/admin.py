from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.urls import reverse
from django.utils.html import format_html
from djangoql.admin import DjangoQLSearchMixin
from import_export.admin import ImportExportActionModelAdmin

from tickets.forms import TicketAdminForm
from tickets.models import Venue, ConcertCategory, Concert, Ticket


class ConcertInline(admin.TabularInline):
    model = Concert
    fields = ["name", "starts_at", "price", "tickets_left"]
    readonly_fields = ["name", "starts_at", "price", "tickets_left"]
    max_num = 0
    extra = 0
    can_delete = False
    show_change_link = True


class VenueAdmin(admin.ModelAdmin):
    list_display = ["name", "address", "capacity"]
    inlines = [ConcertInline]


class ConcertCategoryAdmin(admin.ModelAdmin):
    pass


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


class ConcertAdmin(admin.ModelAdmin):
    list_display = ["name", "display_venue", "starts_at", "display_price", "tickets_left", "display_sold_out"]
    search_fields = ["name", "venue__name", "venue__address"]
    list_filter = ["venue", SoldOutFilter]
    readonly_fields = ["tickets_left"]

    def display_sold_out(self, obj):
        return obj.is_sold_out()

    display_sold_out.short_description = "Sold out"
    display_sold_out.boolean = True

    def display_price(self, obj):
        return f"${obj.price}"

    display_price.short_description = "Price"
    display_price.admin_order_field = "price"

    def display_venue(self, obj):
        link = reverse("admin:tickets_venue_change", args=[obj.venue.id])
        return format_html('<a href="{}">{}</a>', link, obj.venue)

    display_venue.short_description = "Venue"


@admin.action(description="Activate selected tickets")
def activate_tickets(modeladmin, request, queryset):
    queryset.update(is_active=True)


@admin.action(description="Deactivate selected tickets")
def deactivate_tickets(modeladmin, request, queryset):
    queryset.update(is_active=False)


class TicketAdmin(DjangoQLSearchMixin, ImportExportActionModelAdmin):
    list_display = ["customer_full_name", "concert", "payment_method", "paid_at", "is_active"]
    actions = [activate_tickets, deactivate_tickets]
    form = TicketAdminForm


admin.site.register(Venue, VenueAdmin)
admin.site.register(ConcertCategory, ConcertCategoryAdmin)
admin.site.register(Concert, ConcertAdmin)
admin.site.register(Ticket, TicketAdmin)
