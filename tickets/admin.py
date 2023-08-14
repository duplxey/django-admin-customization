from django.contrib import admin
from tickets.models import Venue, ConcertCategory, Concert, Ticket


class VenueAdmin(admin.ModelAdmin):
    pass


class ConcertCategoryAdmin(admin.ModelAdmin):
    pass


class ConcertAdmin(admin.ModelAdmin):
    pass


class TicketAdmin(admin.ModelAdmin):
    pass


admin.site.register(Venue, VenueAdmin)
admin.site.register(ConcertCategory, ConcertCategoryAdmin)
admin.site.register(Concert, ConcertAdmin)
admin.site.register(Ticket, TicketAdmin)
