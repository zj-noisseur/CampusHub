import os
import django
import sys

# Add the project directory to sys.path
sys.path.append('c:\\Users\\zfhin\\OneDrive\\project\\CampusClubDiscovery\\campushub')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campushub.settings')
django.setup()

from core.models import State, Institution, Club

def fix_logos():
    print("Fixing State and Institution logos...")
    
    # Fix States
    states_data = {
        'Melaka': 'states/melacca.png',
        'Selangor': 'states/selangor.png',
        'Perak': 'states/perak.png'
    }
    
    for state_name, file_path in states_data.items():
        state = State.objects.filter(name=state_name).first()
        if state:
            state.flag = file_path
            state.save()
            print(f"Updated State: {state_name} with {file_path}")

    # Fix Institutions
    inst_data = {
        'Multimedia University Melaka': 'institutions/mmu_malacca.png',
        'Multimedia University Cyberjaya': 'institutions/mmu_cyberjaya.png'
    }
    
    for inst_name, file_path in inst_data.items():
        inst = Institution.objects.filter(university_name=inst_name).first()
        if inst:
            inst.logo = file_path
            inst.save()
            print(f"Updated Institution: {inst_name} with {file_path}")

    # Assign default club logos
    placeholder_logo = 'club_logos/images_3.jpg'
    Club.objects.filter(logo='').update(logo=placeholder_logo)
    Club.objects.filter(logo__isnull=True).update(logo=placeholder_logo)
    print(f"Assigned placeholder logo to clubs.")

    # Assign some categories
    import random
    categories = ['RECRUITMENT', 'COMPETITION', 'WORKSHOP', 'PAST_EVENT', 'MISC']
    for club in Club.objects.all():
        if club.category == 'MISC':
            club.category = random.choice(categories)
            club.save()

    print("Done!")

if __name__ == '__main__':
    fix_logos()
