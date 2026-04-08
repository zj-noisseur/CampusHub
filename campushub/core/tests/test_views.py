from django.test import TestCase, Client
from django.urls import reverse
from core.models import Institution, Club

class InstitutionViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        Institution.objects.create(university_name='Test University', state='Test State')

    def test_institution_list_view(self):
        response = self.client.get(reverse('institution_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test University')

class ClubViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        institution = Institution.objects.create(university_name='Test University', state='Test State')
        Club.objects.create(institution=institution, name='Test Club')

    def test_club_list_view(self):
        response = self.client.get(reverse('club_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Club')