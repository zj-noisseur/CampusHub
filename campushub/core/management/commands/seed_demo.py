import os
import json
import re
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from core.models import Institution, Club, State, Post, Event

class Command(BaseCommand):
    help = 'Seed database from exported JSON files including clubs, posts, and detected events'

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write("Starting demo seed process...")
            
            # 1. Setup States
            melaka, _ = State.objects.get_or_create(name='Melaka')
            selangor, _ = State.objects.get_or_create(name='Selangor')

            # 2. Setup Institutions
            mmumelaka, _ = Institution.objects.get_or_create(
                university_name='Multimedia University Melaka',
                state=melaka
            )
            cyberjaya, _ = Institution.objects.get_or_create(
                university_name='Multimedia University Cyberjaya',
                state=selangor
            )

            # 3. Process JSON Exports
            # Path: campushub/export/
            export_dir = os.path.join(settings.BASE_DIR, 'core', '..', 'export')
            if not os.path.exists(export_dir):
                # Try another common path
                export_dir = os.path.join(settings.BASE_DIR, 'export')
                
            if not os.path.exists(export_dir):
                self.stderr.write(self.style.ERROR(f"Export directory not found. Checked: {export_dir}"))
                return

            json_files = [f for f in os.listdir(export_dir) if f.endswith('.json')]
            self.stdout.write(self.style.SUCCESS(f"Found {len(json_files)} JSON files in {export_dir}"))

            # Heuristic for detecting events in captions
            date_patterns = [
                r"Date:\s*([\d]{1,2}[a-z]{0,2}\s+[A-Za-z]+\s+[\d]{4})", # 14th May 2026
                r"Date:\s*([\d]{1,2}/[\d]{1,2}/[\d]{4})",               # 14/05/2026
                r"📅\s*Date:\s*([\d]{1,2}[a-z]{0,2}\s+[A-Za-z]+\s+[\d]{4})",
            ]
            venue_patterns = [
                r"Venue:\s*(.+)",
                r"📍\s*Venue:\s*(.+)",
                r"Location:\s*(.+)",
            ]

            posts_count = 0
            events_count = 0

            for filename in json_files:
                ig_handle = filename.replace('.json', '')
                
                # Check if club exists by handle
                club = Club.objects.filter(ig_handle=ig_handle).first()
                if not club:
                    # Create a default club if not found in seed
                    club = Club.objects.create(
                        name=ig_handle.replace('_', ' ').replace('.', ' ').title(),
                        ig_handle=ig_handle,
                        institution=cyberjaya if 'cyber' in ig_handle.lower() or 'clsc' in ig_handle.lower() else mmumelaka
                    )

                with open(os.path.join(export_dir, filename), 'r', encoding='utf-8') as f:
                    try:
                        dataset = json.load(f)
                    except json.JSONDecodeError:
                        continue

                    if not isinstance(dataset, list):
                        continue

                    for item in dataset:
                        short_code = item.get('shortCode')
                        if not short_code: continue

                        timestamp_str = item.get('timestamp')
                        if timestamp_str:
                            try:
                                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            except:
                                timestamp = timezone.now()
                        else:
                            timestamp = timezone.now()

                        caption = item.get('caption', '') or ''
                        
                        post, created = Post.objects.update_or_create(
                            short_code=short_code,
                            defaults={
                                'club': club,
                                'caption': caption,
                                'timestamp': timestamp,
                            }
                        )
                        if created: posts_count += 1

                        # Event Detection
                        is_event = False
                        event_date = None
                        location = "Multimedia University"
                        
                        # Try to find date in caption
                        for pattern in date_patterns:
                            match = re.search(pattern, caption, re.IGNORECASE)
                            if match:
                                date_str = match.group(1)
                                try:
                                    # Handle 14th May 2026 (remove 'th', 'st', 'nd', 'rd')
                                    clean_date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
                                    # Try various formats
                                    for fmt in ["%d %B %Y", "%d/%m/%Y"]:
                                        try:
                                            event_date = datetime.strptime(clean_date_str, fmt).date()
                                            is_event = True
                                            break
                                        except: continue
                                    if is_event: break
                                except:
                                    continue
                        
                        if is_event or "register" in caption.lower() or "workshop" in caption.lower():
                            # It's likely an event even if date parsing failed
                            is_event = True
                            
                            # Try to find venue
                            for pattern in venue_patterns:
                                v_match = re.search(pattern, caption, re.IGNORECASE)
                                if v_match:
                                    location = v_match.group(1).split('\n')[0].strip()
                                    break
                            
                            # Create Event
                            event_obj, e_created = Event.objects.update_or_create(
                                post=post,
                                defaults={
                                    'club': club,
                                    'title': (caption.split('\n')[0][:250] or f"Event at {club.name}"),
                                    'event_date': event_date or timestamp.date(),
                                    'location': location[:250],
                                    'status': 'FINISHED' if (event_date and event_date < timezone.localdate()) else 'ONGOING'
                                }
                            )
                            if e_created: events_count += 1

            self.stdout.write(self.style.SUCCESS(f"Demo seed completed. Created {posts_count} posts and {events_count} events."))
