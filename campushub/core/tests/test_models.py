from django.test import TestCase
from core.models import Institution, Club

class InstitutionModelTest(TestCase):
    def test_create_institution(self):
        institution = Institution.objects.create(university_name='Test University', state='Test State')
        self.assertEqual(str(institution), 'Test University')

class ClubModelTest(TestCase):
    def test_create_club(self):
        institution = Institution.objects.create(university_name='Test University', state='Test State')
        club = Club.objects.create(institution=institution, name='Test Club')
        self.assertEqual(str(club), 'Test Club')