from django.core.management.base import BaseCommand
from core.tasks import persist_club_dataset

class Command(BaseCommand):
    def handle(self, *args, **options):
        # generate fake dataset
        ds = [{'images': [f'url_{i}']} for i in range(100)]
        task = persist_club_dataset.delay(str(35), ds)
        print("Task created:", task.id)
