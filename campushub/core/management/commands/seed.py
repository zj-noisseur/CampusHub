from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Institution, Club


class Command(BaseCommand):
    help = 'Seed MMU Melaka and Cyberjaya clubs and institutions'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Create / get institutions (exactly as in SQL)
            melaka, _ = Institution.objects.get_or_create(
                university_name='Multimedia University Melaka',
                state='Melaka'
            )
            cyberjaya, _ = Institution.objects.get_or_create(
                university_name='Multimedia University Cyberjaya',
                state='Selangor'
            )

            # All clubs with exact naming from your SQL file (no omissions, no changes)
            clubs_data = [
                # ==================== MELAKA CAMPUS ====================
                # Melaka Sports & Martial Arts Clubs (exact order from SQL)
                {'institution': melaka, 'name': 'Aerobic Club', 'ig_handle': None},
                {'institution': melaka, 'name': 'Archery Club', 'ig_handle': None},
                {'institution': melaka, 'name': 'Badminton Club', 'ig_handle': None},
                {'institution': melaka, 'name': 'Basketball Club', 'ig_handle': None},
                {'institution': melaka, 'name': 'Chess Club', 'ig_handle': None},
                {'institution': melaka, 'name': 'Fencing Club', 'ig_handle': None},
                {'institution': melaka, 'name': 'Flex & Fitness Club', 'ig_handle': None},
                {'institution': melaka, 'name': 'Football Club', 'ig_handle': None},
                {'institution': melaka, 'name': 'Rugby Club', 'ig_handle': '@mmuhornbills'},
                {'institution': melaka, 'name': 'Netball Club', 'ig_handle': '@mmumelakanetball'},
                {'institution': melaka, 'name': 'OUTRECS', 'ig_handle': None},
                {'institution': melaka, 'name': 'Road Runners Club', 'ig_handle': None},
                {'institution': melaka, 'name': 'Squash Club', 'ig_handle': None},
                {'institution': melaka, 'name': 'Swimming Club', 'ig_handle': '@mmu_swimming_club'},
                {'institution': melaka, 'name': 'Table Tennis Club', 'ig_handle': None},
                {'institution': melaka, 'name': 'Tennis Club', 'ig_handle': None},
                {'institution': melaka, 'name': 'Volleyball Club', 'ig_handle': None},
                {'institution': melaka, 'name': 'Water Sports Club', 'ig_handle': None},
                {'institution': melaka, 'name': 'Softball Club', 'ig_handle': None},
                {'institution': melaka, 'name': 'E-Games Club', 'ig_handle': None},
                {'institution': melaka, 'name': 'Aikido Club', 'ig_handle': '@mmu.aikido'},
                {'institution': melaka, 'name': 'Judo Club', 'ig_handle': '@mmu_judo_club'},
                {'institution': melaka, 'name': 'Karate Club', 'ig_handle': None},
                {'institution': melaka, 'name': 'Silat Cekak Pusaka Hanafi Club', 'ig_handle': None},
                {'institution': melaka, 'name': 'Taekwondo Club', 'ig_handle': None},
                {'institution': melaka, 'name': 'Wing Chun Club', 'ig_handle': '@wingchundoclubmmu'},
                {'institution': melaka, 'name': 'Wushu Club', 'ig_handle': None},

                # Melaka Non-sports Clubs & Societies (exact order from SQL)
                {'institution': melaka, 'name': 'Accounting Club', 'ig_handle': '@mmuac.malacca'},
                {'institution': melaka, 'name': 'Arabic Culture Society', 'ig_handle': None},
                {'institution': melaka, 'name': 'Animals And Pets Society', 'ig_handle': None},
                {'institution': melaka, 'name': 'Buddhist Society', 'ig_handle': None},
                {'institution': melaka, 'name': 'Business Society', 'ig_handle': '@mmu_businesssociety'},
                {'institution': melaka, 'name': 'Chinese Language Society', 'ig_handle': None},
                {'institution': melaka, 'name': 'Chinese Orchestra Society', 'ig_handle': None},
                {'institution': melaka, 'name': 'Choir Club', 'ig_handle': None},
                {'institution': melaka, 'name': 'Editorial Squad', 'ig_handle': None},
                {'institution': melaka, 'name': 'Engineering Society', 'ig_handle': '@mmu_engineeringsociety'},
                {'institution': melaka, 'name': 'Golden Key Society', 'ig_handle': None},
                {'institution': melaka, 'name': 'Indian Cultural Society', 'ig_handle': '@icsmmumalacca'},
                {'institution': melaka, 'name': 'Institusi Usrah', 'ig_handle': None},
                {'institution': melaka, 'name': 'International Student Society', 'ig_handle': None},
                {'institution': melaka, 'name': 'IT Society', 'ig_handle': '@itsocietymmumelaka'},
                {'institution': melaka, 'name': 'Korean Cultural Society', 'ig_handle': None},
                {'institution': melaka, 'name': 'Malaysian Red Crescent Society', 'ig_handle': None},
                {'institution': melaka, 'name': 'MMU Christian Society', 'ig_handle': None},
                {'institution': melaka, 'name': 'MMU IEM', 'ig_handle': None},
                {'institution': melaka, 'name': 'MMU IET', 'ig_handle': None},
                {'institution': melaka, 'name': 'MMusic Society', 'ig_handle': '@mmusic_society_melaka_campus'},
                {'institution': melaka, 'name': 'Multimedia Arts & Theater Club', 'ig_handle': None},
                {'institution': melaka, 'name': 'Multimedia Initiative Language of English', 'ig_handle': None},
                {'institution': melaka, 'name': 'Multimedia University Law Society', 'ig_handle': None},
                {'institution': melaka, 'name': 'Robotics Club', 'ig_handle': '@mmuroboticsclub'},
                {'institution': melaka, 'name': 'Sekretariat Rakan Muda', 'ig_handle': None},
                {'institution': melaka, 'name': 'St. John Ambulance', 'ig_handle': None},
                {'institution': melaka, 'name': "Voice's Debating Society", 'ig_handle': None},
                {'institution': melaka, 'name': 'Student College Committee', 'ig_handle': None},
                {'institution': melaka, 'name': 'Student Representative Council', 'ig_handle': None},

                # ==================== CYBERJAYA CAMPUS ====================
                # Cyberjaya Sports, Martial Arts & Non-sports Clubs (exact order from SQL)
                {'institution': cyberjaya, 'name': 'Rugby Club', 'ig_handle': '@mmuhornbillsreds'},
                {'institution': cyberjaya, 'name': 'Basketball Club', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Netball Club', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Badminton Club', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Volleyball Club', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'OARS', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Swimming Club', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Chess Club', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Soccer Club', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Archery Club', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Water Sports Club', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'MMU E-Sport Club', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Silat Cekak Club', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Aikido Club', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Buddhist Society Club', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Chinese Language Society', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Christian Society', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Communicators For Life (CFL)', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Creative Multimedia Club (CMC)', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Cyberjaya Accounting Club (CAC)', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'D.I.C.E', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Deejay Club', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Editorial Squad Cyberjaya', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Engineering Society', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Faculty of Management Society', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Cinematics Arts Society', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Indian Cultural Society', 'ig_handle': '@icsmmucyber'},
                {'institution': cyberjaya, 'name': 'International Student Society (ISS)', 'ig_handle': '@iss_mmucyber'},
                {'institution': cyberjaya, 'name': 'IT Society', 'ig_handle': '@itsocietymmu'},
                {'institution': cyberjaya, 'name': 'Japanese Cultural Society', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Korean Language Society', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'MMU Game Developers Club', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Rentak Dance Club', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Sekretariat Rakan Muda (SRM)', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Sekretariat Sekolah@MMU', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Sekretariat Rukun Negara', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Theatre at Multimedia University (TAMU)', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'University Peer Group (UPG)', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Usrah Institution', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Voices Debating Society', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Enactus MMU', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Student College Committee', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Student Representative Council', 'ig_handle': None},
            ]

            # Create clubs (idempotent – safe to run multiple times)
            for data in clubs_data:
                Club.objects.get_or_create(
                    institution=data['institution'],
                    name=data['name'],
                    defaults={'ig_handle': data['ig_handle']}
                )

        self.stdout.write(self.style.SUCCESS('✅ Successfully seeded all MMU clubs for both campuses!'))