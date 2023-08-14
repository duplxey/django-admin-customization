import random
from datetime import datetime, timedelta

import pytz
from django.core.management.base import BaseCommand

from tickets.models import Venue, ConcertCategory, Concert, Ticket


class Command(BaseCommand):
    help = "Populates the database with random generated data."

    def handle(self, *args, **options):
        # populate the database with venues
        venues = [
            Venue.objects.get_or_create(
                name="The O2 Arena", address="Peninsula Square, London SE10 0DX, United Kingdom", capacity=960,
            ),
            Venue.objects.get_or_create(
                name="Arena of Nîmes", address="Boulevard des Arènes, 30000 Nîmes, France", capacity=720,
            ),
            Venue.objects.get_or_create(
                name="Red Rocks Amphitheatre", address="18300 W Alameda, Morrison, CO, United States", capacity=640,
            ),
            Venue.objects.get_or_create(
                name="Dalhalla Amphitheatre", address="Dalhalla, 790 90 Rättvik, Sweden", capacity=800,
            ),
            Venue.objects.get_or_create(
                name="The Fillmore", address="1805 Geary Blvd, San Francisco, CA, United States", capacity=620,
            ),
        ]

        # populate the database with categories
        categories = ["Rock", "Pop", "Metal", "Hip Hop", "Jazz"]
        for category in categories:
            ConcertCategory.objects.get_or_create(name=category)

        # populate the database with concerts
        concert_prefix = ["Underground", "Midnight", "Late Night", "Secret", "" * 10]
        concert_suffix = ["Party", "Rave", "Concert", "Gig", "Revolution", "Jam", "Tour"]
        for i in range(10):
            venue = random.choice(venues)[0]
            category = ConcertCategory.objects.order_by("?").first()
            concert = Concert.objects.create(
                name=f"{random.choice(concert_prefix)} {category.name} {random.choice(concert_suffix)}",
                description="",
                venue=venue,
                starts_at=datetime.now(pytz.utc)
                + timedelta(days=random.randint(1, 365)),
                price=random.randint(10, 100),
            )
            concert.categories.add(category)
            concert.save()

        # populate the database with ticket purchases
        names = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles"]
        surname = ["Smith", "Jones", "Taylor", "Brown", "Williams", "Wilson", "Johnson", "Davies", "Patel", "Wright"]
        for i in range(500):
            concert = Concert.objects.order_by("?").first()
            Ticket.objects.create(
                concert=concert,
                customer_full_name=f"{random.choice(names)} {random.choice(surname)}",
                payment_method=random.choice(["CC", "CC", "CC", "CC", "DC", "DC", "ET", "BC"]),
                paid_at=datetime.now(pytz.utc) - timedelta(days=random.randint(1, 365)),
                is_active=random.choice([True, False]),
            )
            concert.tickets_left -= 1
            concert.save()

        self.stdout.write(self.style.SUCCESS("Successfully populated the database."))
