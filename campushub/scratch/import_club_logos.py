import os
import json
import requests
import django
import sys
from django.core.files.base import ContentFile

# Setup Django
sys.path.append('c:\\Users\\zfhin\\OneDrive\\project\\CampusClubDiscovery\\campushub')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campushub.settings')
django.setup()

from core.models import Club

def import_logos():
    print("Starting logo import from JSON files...")
    export_dir = 'c:\\Users\\zfhin\\OneDrive\\project\\CampusClubDiscovery\\campushub\\export'
    
    # Track which clubs we've found logos for
    found_count = 0
    
    # Get all clubs with handles
    clubs = Club.objects.exclude(ig_handle__isnull=True).exclude(ig_handle='')
    
    for club in clubs:
        handle = club.ig_handle
        json_path = os.path.join(export_dir, f"{handle}.json")
        
        if not os.path.exists(json_path):
            # Try to find handle in ANY json file if specific one doesn't exist
            # But usually it should be in handle.json
            continue
            
        print(f"Searching for logo for {handle}...")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"Error reading {json_path}: {e}")
                continue
                
            profile_pic_url = None
            
            # Look through posts to find the profile pic
            for post in data:
                # Check taggedUsers
                for user in post.get('taggedUsers', []):
                    if user.get('username') == handle:
                        profile_pic_url = user.get('profile_pic_url')
                        break
                if profile_pic_url: break
                
                # Check coauthorProducers
                for user in post.get('coauthorProducers', []):
                    if user.get('username') == handle:
                        profile_pic_url = user.get('profile_pic_url')
                        break
                if profile_pic_url: break
                
                # Check latestComments
                for comment in post.get('latestComments', []):
                    if comment.get('ownerUsername') == handle:
                        profile_pic_url = comment.get('ownerProfilePicUrl')
                        break
                if profile_pic_url: break

            if profile_pic_url:
                print(f"Found logo for {handle}: {profile_pic_url}")
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    response = requests.get(profile_pic_url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        filename = f"{handle}.jpg"
                        club.logo.save(filename, ContentFile(response.content), save=True)
                        print(f"SUCCESS: Saved logo for {handle}")
                        found_count += 1
                        continue # Move to next club
                    else:
                        print(f"FAILED: Status {response.status_code} for {handle}")
                except Exception as e:
                    print(f"ERROR: Downloading logo for {handle}: {e}")
            else:
                print(f"SKIP: No logo found in JSON for {handle}")

            # Fallback to Institution logo if we reach here
            if club.institution and club.institution.logo:
                print(f"FALLBACK: Using institution logo for {handle}")
                # We need to copy the file to avoid sharing the same underlying file object
                # but in Django, we can just point to the same path or copy the content
                try:
                    institution_logo = club.institution.logo
                    club.logo.save(f"{handle}_fallback.png", institution_logo.file, save=True)
                    print(f"SUCCESS: Fallback applied for {handle}")
                except Exception as e:
                    print(f"ERROR: Fallback failed for {handle}: {e}")

    print(f"\nDone! Imported {found_count} club logos.")

if __name__ == '__main__':
    import_logos()
