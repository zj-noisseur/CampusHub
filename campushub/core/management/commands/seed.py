from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Institution, Club, State


class Command(BaseCommand):
    help = 'Seed MMU Melaka and Cyberjaya clubs and institutions'

    def handle(self, *args, **options):
        with transaction.atomic():
            selangor, _ = State.objects.get_or_create(name='Selangor')
            melaka, _ = State.objects.get_or_create(name='Melaka')
            perak, _ = State.objects.get_or_create(name='Perak')

            mmumelaka, _ = Institution.objects.get_or_create(
                university_name='Multimedia University Melaka',
                state=melaka
            )
            cyberjaya, _ = Institution.objects.get_or_create(
                university_name='Multimedia University Cyberjaya',
                state=selangor
            )

            clubs_data = [
                # Verified Melaka (with previous updates)
                {'institution': mmumelaka, 'name': 'Aerobic Club', 'ig_handle': 'aerobicsclub_mmu'},
                {'institution': mmumelaka, 'name': 'Archery Club', 'ig_handle': 'mmu_archeryclub'},
                {'institution': mmumelaka, 'name': 'Badminton Club', 'ig_handle': "mmubadmintonclub97"},
                {'institution': mmumelaka, 'name': 'Basketball Club', 'ig_handle': 'mmubc_melaka'},
                {'institution': mmumelaka, 'name': 'Chess Club', 'ig_handle': 'mmuchessclub'},
                {'institution': mmumelaka, 'name': 'Fencing Club', 'ig_handle': 'mmu_fencingmelaka'},
                {'institution': mmumelaka, 'name': 'Flex & Fitness Club', 'ig_handle': 'mmu_ffc_melaka'},
                {'institution': mmumelaka, 'name': 'Football Club', 'ig_handle': 'mmumelakafc'},
                {'institution': mmumelaka, 'name': 'Rugby Club', 'ig_handle': 'mmuhornbills'},
                {'institution': mmumelaka, 'name': 'Netball Club', 'ig_handle': 'mmumelakanetball'},
                {'institution': mmumelaka, 'name': 'OUTRECS', 'ig_handle': None},
                {'institution': mmumelaka, 'name': 'Road Runners Club', 'ig_handle': 'mmuroadrunners'},
                {'institution': mmumelaka, 'name': 'Squash Club', 'ig_handle': None},
                {'institution': mmumelaka, 'name': 'Swimming Club', 'ig_handle': 'mmu_swimming_club'},
                {'institution': mmumelaka, 'name': 'Table Tennis Club', 'ig_handle': 'mmutabletennis_melaka'},
                {'institution': mmumelaka, 'name': 'Tennis Club', 'ig_handle': None},
                {'institution': mmumelaka, 'name': 'Volleyball Club', 'ig_handle': 'mmuvc_melaka'},
                {'institution': mmumelaka, 'name': 'Water Sports Club', 'ig_handle': 'mmuwatersports'},
                {'institution': mmumelaka, 'name': 'Softball Club', 'ig_handle': 'softballclub.mmumelaka'},
                {'institution': mmumelaka, 'name': 'E-Games Club', 'ig_handle': 'egamesmmu'},
                {'institution': mmumelaka, 'name': 'Aikido Club', 'ig_handle': 'mmu.aikido'},
                {'institution': mmumelaka, 'name': 'Judo Club', 'ig_handle': 'mmu_judo_club'},
                {'institution': mmumelaka, 'name': 'Karate Club', 'ig_handle': None},
                {'institution': mmumelaka, 'name': 'Silat Cekak Pusaka Hanafi Club', 'ig_handle': 'pusakahanafimmumelaka'},
                {'institution': mmumelaka, 'name': 'Taekwondo Club', 'ig_handle': 'mmutaekwondo'},
                {'institution': mmumelaka, 'name': 'Wing Chun Club', 'ig_handle': 'wingchundoclubmmu'},
                {'institution': mmumelaka, 'name': 'Wushu Club', 'ig_handle': 'wushummu_mlk'},
                {'institution': mmumelaka, 'name': 'Accounting Club', 'ig_handle': 'mmuac.malacca'},
                {'institution': mmumelaka, 'name': 'Arabic Culture Society', 'ig_handle': 'acs_melaka'},
                {'institution': mmumelaka, 'name': 'Animals And Pets Society', 'ig_handle': 'mmu_animalsandpetssociety'},
                {'institution': mmumelaka, 'name': 'Buddhist Society', 'ig_handle': 'mmu_buddy'},
                {'institution': mmumelaka, 'name': 'Business Society', 'ig_handle': 'mmu_businesssociety'},
                {'institution': mmumelaka, 'name': 'Chinese Language Society Multimedia University Melaka', 'ig_handle': 'clsm_official'},
                {'institution': mmumelaka, 'name': 'Cultural and Literature Division Chinese Language Society Multimedia University Melaka', 'ig_handle': 'cld_mmu'},
                {'institution': mmumelaka, 'name': 'Recreational Division Chinese Language Society Multimedia University Melaka', 'ig_handle': 'cls_rd'},
                {'institution': mmumelaka, 'name': 'Information and Multimedia Division Chinese Language Society Multimedia University Melaka', 'ig_handle': '29th_imd'},
                {'institution': mmumelaka, 'name': 'Chinese Orchestra Society', 'ig_handle': 'mmucosmalacca'},
                {'institution': mmumelaka, 'name': 'Choir Club', 'ig_handle': 'mmuchoirclub'},
                {'institution': mmumelaka, 'name': 'Editorial Squad', 'ig_handle': 'mmustudentpress'},
                {'institution': mmumelaka, 'name': 'Engineering Society', 'ig_handle': 'mmu_engineeringsociety'},
                {'institution': mmumelaka, 'name': 'Golden Key Society', 'ig_handle': 'mmu.gks'},
                {'institution': mmumelaka, 'name': 'Indian Cultural Society', 'ig_handle': 'icsmmumalacca'},
                {'institution': mmumelaka, 'name': 'Institusi Usrah', 'ig_handle': 'iu_melaka'},
                {'institution': mmumelaka, 'name': 'International Student Society', 'ig_handle': 'iss_mmu_melaka'},
                {'institution': mmumelaka, 'name': 'IT Society', 'ig_handle': 'itsocietymmumelaka'},
                {'institution': mmumelaka, 'name': 'Korean Cultural Society', 'ig_handle': 'kcsmmumelaka'},
                {'institution': mmumelaka, 'name': 'Malaysian Red Crescent Society', 'ig_handle': 'malaysianredcrescentmmu'},
                {'institution': mmumelaka, 'name': 'MMU Christian Society', 'ig_handle': 'csschristmmu'},
                {'institution': mmumelaka, 'name': 'MMU IEM', 'ig_handle': 'iem_mmumelaka'},
                {'institution': mmumelaka, 'name': 'MMU IET', 'ig_handle': 'iet_mmumelaka'},
                {'institution': mmumelaka, 'name': 'MMusic Society', 'ig_handle': 'mmusic_society_melaka_campus'},
                {'institution': mmumelaka, 'name': 'Multimedia Arts & Theater Club', 'ig_handle': 'mata_mmu'},
                {'institution': mmumelaka, 'name': 'Multimedia Initiative Language of English', 'ig_handle': 'milemmu'},
                {'institution': mmumelaka, 'name': 'Multimedia University Law Society', 'ig_handle': 'mmulawsociety'},
                {'institution': mmumelaka, 'name': 'Robotics Club', 'ig_handle': 'mmuroboticsclub'},
                {'institution': mmumelaka, 'name': 'Sekretariat Rakan Muda', 'ig_handle': None},
                {'institution': mmumelaka, 'name': 'St. John Ambulance', 'ig_handle': None},
                {'institution': mmumelaka, 'name': "Voice's Debating Society", 'ig_handle': 'voicesmmu'},
                {'institution': mmumelaka, 'name': 'Student College Committee', 'ig_handle': 'sccmmu_melaka'},
                {'institution': mmumelaka, 'name': 'Student Representative Council', 'ig_handle': 'srcmmu_melaka'},

                # Updated Cyberjaya
                {'institution': cyberjaya, 'name': 'Rugby Club', 'ig_handle': 'mmuhornbillsreds'},
                {'institution': cyberjaya, 'name': 'Basketball Club', 'ig_handle': 'mmubc_cyberjaya'},
                {'institution': cyberjaya, 'name': 'Netball Club', 'ig_handle': 'mmunetbees'},
                {'institution': cyberjaya, 'name': 'Badminton Club', 'ig_handle': 'badmintonclubmmucyber'},
                {'institution': cyberjaya, 'name': 'Volleyball Club', 'ig_handle': 'volbees_mmu'},
                {'institution': cyberjaya, 'name': 'OARS', 'ig_handle': 'oarsmmucyber'},
                {'institution': cyberjaya, 'name': 'Swimming Club', 'ig_handle': 'mmuswimmingclub'},
                {'institution': cyberjaya, 'name': 'Chess Club', 'ig_handle': 'mmucyberjayachessclub'},
                {'institution': cyberjaya, 'name': 'Soccer Club', 'ig_handle': 'mmufccyber'},
                {'institution': cyberjaya, 'name': 'Archery Club', 'ig_handle': 'mmucyberjayarchery'},
                {'institution': cyberjaya, 'name': 'Water Sports Club', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'MMU E-Sport Club', 'ig_handle': 'mmuesports'},
                {'institution': cyberjaya, 'name': 'Silat Cekak Club', 'ig_handle': 'psscmmmucyb'},
                {'institution': cyberjaya, 'name': 'Aikido Club', 'ig_handle': 'mmu.aikido_club'},
                {'institution': cyberjaya, 'name': 'Buddhist Society Club', 'ig_handle': 'buddhistsociety.mmu'},
                {'institution': cyberjaya, 'name': 'Chinese Language Society', 'ig_handle': 'official_clsc_mmu'},
                {'institution': cyberjaya, 'name': 'Literature Division Chinese Language Society Multimedia University', 'ig_handle': 'clsc_literature.div'},
                {'institution': cyberjaya, 'name': 'Cultural Division Chinese Language Society Multimedia University', 'ig_handle': 'clsc_cultural.div'},
                {'institution': cyberjaya, 'name': 'Recreational Division Chinese Language Society Multimedia University', 'ig_handle': 'clsc_recreational.div'},
                {'institution': cyberjaya, 'name': 'Information Technology and Multimedia Division Chinese Language Society Multimedia University', 'ig_handle': 'clsc_it.media.div'},
                {'institution': cyberjaya, 'name': 'Christian Society', 'ig_handle': 'mmucscyber'},
                {'institution': cyberjaya, 'name': 'Communicators For Life (CFL)', 'ig_handle': 'cflmmucyber'},
                {'institution': cyberjaya, 'name': 'Creative Multimedia Club (CMC)', 'ig_handle': 'cmcmmu'},
                {'institution': cyberjaya, 'name': 'Cyberjaya Accounting Club (CAC)', 'ig_handle': 'cac.mmu'},
                {'institution': cyberjaya, 'name': 'D.I.C.E', 'ig_handle': 'mmu.dice'},
                {'institution': cyberjaya, 'name': 'Deejay Club', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Editorial Squad Cyberjaya', 'ig_handle': None},
                {'institution': cyberjaya, 'name': 'Engineering Society', 'ig_handle': 'engsoc_mmucyb'},
                {'institution': cyberjaya, 'name': 'Faculty of Management Society', 'ig_handle': 'fom.mmu'},
                {'institution': cyberjaya, 'name': 'Cinematics Arts Society', 'ig_handle': 'cinematicartssociety'},
                {'institution': cyberjaya, 'name': 'Indian Cultural Society', 'ig_handle': 'icsmmucyber'},
                {'institution': cyberjaya, 'name': 'International Student Society (ISS)', 'ig_handle': 'iss_mmucyber'},
                {'institution': cyberjaya, 'name': 'IT Society', 'ig_handle': 'itsocietymmu'},
                {'institution': cyberjaya, 'name': 'Japanese Cultural Society', 'ig_handle': 'jcsmmu'},
                {'institution': cyberjaya, 'name': 'Korean Culture Club', 'ig_handle': 'kcc_cyber'},
                {'institution': cyberjaya, 'name': 'MMU Game Developers Club', 'ig_handle': 'gdcmmu'},
                {'institution': cyberjaya, 'name': 'Rentak Dance Club', 'ig_handle': 'rentakmmu'},
                {'institution': cyberjaya, 'name': 'Sekretariat Rakan Muda (SRM)', 'ig_handle': 'srmcyber'},
                {'institution': cyberjaya, 'name': 'Sekretariat SekolahMMU', 'ig_handle': 'sekolahmmu'},
                {'institution': cyberjaya, 'name': 'Theatre at Multimedia University (TAMU)', 'ig_handle': 'tamucyb'},
                {'institution': cyberjaya, 'name': 'University Peer Group (UPG)', 'ig_handle': 'upgcyber'},
                {'institution': cyberjaya, 'name': 'Usrah Institution', 'ig_handle': 'iucyber'},
                {'institution': cyberjaya, 'name': 'Voices Debating Society', 'ig_handle': 'voices_mmu'},
                {'institution': cyberjaya, 'name': 'Student Representative Council', 'ig_handle': 'srcmmu_cyber'},
                {'institution': cyberjaya, 'name': 'IEEE Multimedia University', 'ig_handle': 'ieeemmusb'}
            ]

            for data in clubs_data:
                Club.objects.update_or_create(
                    institution=data['institution'],
                    name=data['name'],
                    defaults={'ig_handle': data['ig_handle']}
                )

        self.stdout.write(self.style.SUCCESS('✅ Database updated with verified handles only.'))