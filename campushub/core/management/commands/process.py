import os
from django.core.management.base import BaseCommand
from core.models import Club
from core.task import run_club_scrape_task

class Command(BaseCommand):
    help = 'Run Instagram scrape and export tasks for a club'

    def handle(self, *args, **options):
        ig_handle = 'itsocietymmu'
        try:
            club = Club.objects.get(ig_handle=ig_handle)
        except Club.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Club with handle '{ig_handle}' not found."))
            return

        export_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'export'))
        self.stdout.write(self.style.SUCCESS(f"Running scrape task for {ig_handle} and exporting to {export_dir}"))

        result = run_club_scrape_task(club, export_dir=export_dir)
        self.stdout.write(self.style.SUCCESS(
            f"Completed scrape task: items_returned={result.get('items_returned')} created_count={result.get('created_count')} export_dir={result.get('export_dir')}"
        ))





