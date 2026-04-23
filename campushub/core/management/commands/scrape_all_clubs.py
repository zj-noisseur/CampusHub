from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Club
from core.views.scraper import scrape_club


class Command(BaseCommand):
    help = "Scrape all clubs with IG handles and persist new posts incrementally."

    def add_arguments(self, parser):
        parser.add_argument(
            "--full-sync",
            action="store_true",
            help="Delete existing posts per club and re-ingest from API response.",
        )
        parser.add_argument(
            "--search-limit",
            type=int,
            default=20,
            help="Maximum posts requested per club from Apify actor.",
        )
        parser.add_argument(
            "--max-items",
            type=int,
            default=50,
            help="Maximum dataset items to fetch from Apify actor.",
        )

    def handle(self, *args, **options):
        full_sync = options["full_sync"]
        search_limit = options["search_limit"]
        max_items = options["max_items"]

        clubs = Club.objects.filter(ig_handle__isnull=False).exclude(ig_handle="").order_by("name")

        success = 0
        failures = 0
        created_total = 0

        for club in clubs:
            try:
                with transaction.atomic():
                    created = scrape_club(
                        club,
                        full_sync=full_sync,
                        search_limit=search_limit,
                        max_items=max_items,
                    )
                success += 1
                created_total += created
                self.stdout.write(self.style.SUCCESS(f"{club.name}: +{created} new posts"))
            except Exception as exc:
                failures += 1
                self.stdout.write(self.style.ERROR(f"{club.name}: failed ({exc})"))

        self.stdout.write(
            self.style.WARNING(
                f"Completed. Clubs ok={success}, failed={failures}, new_posts={created_total}."
            )
        )