import os
import django
import sys

# Setup Django
sys.path.append('c:\\Users\\zfhin\\OneDrive\\project\\CampusClubDiscovery\\campushub')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campushub.settings')
django.setup()

from core.models import Club

def link_existing_logos():
    print("Starting smart local logo linking...")
    logo_dir = 'c:\\Users\\zfhin\\OneDrive\\project\\CampusClubDiscovery\\campushub\\media\\club_logos'
    
    if not os.path.exists(logo_dir):
        print(f"Error: Directory {logo_dir} does not exist.")
        return

    all_files = os.listdir(logo_dir)
    print(f"Total files in logo_dir: {len(all_files)}")
    
    found_count = 0
    missing_files = 0
    
    # Get all clubs
    clubs = Club.objects.all()
    print(f"Checking {clubs.count()} clubs...")
    
    for club in clubs:
        if club.logo: # Skip if already has logo from previous run
            found_count += 1
            continue

        handle = club.ig_handle
        if not handle:
            missing_files += 1
            continue
            
        found_file = None
        
        # 1. Try exact match first (case insensitive maybe?)
        for fname in all_files:
            if fname.lower() == f"{handle}.jpg".lower() or \
               fname.lower() == f"{handle}.png".lower() or \
               fname.lower() == f"{handle}.jpeg".lower():
                found_file = fname
                break
        
        # 2. Try prefix match (for suffixes or fallbacks)
        if not found_file:
            for fname in all_files:
                if fname.lower().startswith(handle.lower()):
                    found_file = fname
                    break
        
        if found_file:
            relative_path = os.path.join('club_logos', found_file)
            club.logo = relative_path
            club.save()
            print(f"LINKED: {handle} -> {relative_path}")
            found_count += 1
        else:
            missing_files += 1

    print(f"\nDone! Now {found_count} clubs have logos.")
    print(f"Remaining {missing_files} clubs without logos.")

if __name__ == '__main__':
    link_existing_logos()
