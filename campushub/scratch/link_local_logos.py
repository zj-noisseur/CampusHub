import os
import django
import sys

# Setup Django
sys.path.append('c:\\Users\\zfhin\\OneDrive\\project\\CampusClubDiscovery\\campushub')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campushub.settings')
django.setup()

from core.models import Club

def link_existing_logos():
    print("Starting local logo linking...")
    logo_dir = 'c:\\Users\\zfhin\\OneDrive\\project\\CampusClubDiscovery\\campushub\\media\\club_logos'
    
    found_count = 0
    missing_files = 0
    
    # Get all clubs
    clubs = Club.objects.all()
    print(f"Checking {clubs.count()} clubs...")
    
    for club in clubs:
        handle = club.ig_handle
        if not handle:
            continue
            
        # Possible filenames
        filenames = [f"{handle}.jpg", f"{handle}.png", f"{handle}.jpeg"]
        
        found_file = None
        for fname in filenames:
            full_path = os.path.join(logo_dir, fname)
            if os.path.exists(full_path):
                found_file = fname
                break
        
        if found_file:
            # Update the logo field with the relative path
            # In Django, ImageField stores the path relative to MEDIA_ROOT
            relative_path = os.path.join('club_logos', found_file)
            club.logo = relative_path
            club.save()
            print(f"LINKED: {handle} -> {relative_path}")
            found_count += 1
        else:
            # print(f"MISSING: No file found for {handle}")
            missing_files += 1

    print(f"\nDone! Linked {found_count} clubs to existing logos.")
    print(f"Missing files for {missing_files} clubs (might not have had logos).")

if __name__ == '__main__':
    link_existing_logos()
