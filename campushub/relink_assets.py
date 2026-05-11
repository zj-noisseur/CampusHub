import os
import django
import re

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campushub.settings')
django.setup()

from core.models import Club

def clean_string(s):
    # Remove all non-alphanumeric characters and lowercase
    return re.sub(r'[^a-z0-9]', '', s.lower())

def relink_assets():
    logos_dir = 'media/club_logos'
    banners_dir = 'media/club_banners'
    
    if not os.path.exists(logos_dir):
        print(f"Error: {logos_dir} not found")
        return
        
    logos = os.listdir(logos_dir)
    banners = os.listdir(banners_dir) if os.path.exists(banners_dir) else []
    
    relinked_logos = 0
    relinked_banners = 0
    
    clubs = Club.objects.all()
    print(f"Scanning {len(logos)} logos for {len(clubs)} clubs...")
    
    for club in clubs:
        club_slug = clean_string(club.name)
        # Handle cases like "Aerobic" vs "Aerobics" by taking the first 6 chars
        club_prefix = club_slug[:6] if len(club_slug) > 6 else club_slug
        
        # Match Logo
        for logo_file in logos:
            clean_file = clean_string(logo_file).replace('fallback', '').replace('jpg', '').replace('png', '')
            # Match if club name is in file OR file name is in club name OR they share a prefix
            if club_slug in clean_file or clean_file in club_slug or (len(club_prefix) >= 5 and club_prefix in clean_file):
                club.logo = f'club_logos/{logo_file}'
                relinked_logos += 1
                break
        
        # Match Banner
        for banner_file in banners:
            clean_banner = clean_string(banner_file).replace('jpg', '').replace('png', '')
            if club_slug in clean_banner or clean_banner in club_slug or (len(club_prefix) >= 5 and club_prefix in clean_banner):
                club.banner = f'club_banners/{banner_file}'
                relinked_banners += 1
                break
        
        club.save()
        
    print(f"DONE: Successfully re-linked {relinked_logos} logos and {relinked_banners} banners.")

if __name__ == '__main__':
    relink_assets()
