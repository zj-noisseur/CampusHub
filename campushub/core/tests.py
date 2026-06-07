from unittest.mock import patch
from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.contrib.auth import get_user_model
from core.models import Club, Post, Event, Institution, State
from core.services.post_extraction import extract_details
from core.views.event_detail import event_detail, parse_date, parse_time

User = get_user_model()

class PostExtractionTestCase(TestCase):
    @patch('core.services.post_extraction.requests.post')
    def test_extract_details_api_call(self, mock_post):
        mock_post.return_value.json.return_value = {
            "venue": "Agmo Space",
            "date": "29th April 2026",
            "time": "8:00 PM – 10:30 PM",
            "link": "https://luma.com/test"
        }
        mock_post.return_value.status_code = 200
        
        result = extract_details("Some caption text here")
        
        self.assertEqual(result["venue"], "Agmo Space")
        self.assertEqual(result["date"], "29th April 2026")
        self.assertEqual(result["time"], "8:00 PM – 10:30 PM")
        self.assertEqual(result["link"], "https://luma.com/test")

    def test_parse_date_and_time(self):
        self.assertEqual(parse_date("29th April 2026").year, 2026)
        self.assertEqual(parse_date("29th April 2026").month, 4)
        self.assertEqual(parse_date("29th April 2026").day, 29)
        self.assertEqual(parse_time("8:00 PM").hour, 20)
        self.assertEqual(parse_time("10:30 PM").minute, 30)

    @patch('core.services.post_extraction.extract_details')
    def test_event_detail_creates_dummy_event_with_extracted_details(self, mock_extract):
        mock_extract.return_value = {
            "venue": "Agmo Space",
            "date": "29th April 2026",
            "time": "8:00 PM – 10:30 PM",
            "link": "https://luma.com/test"
        }
        
        # Setup model instances
        state = State.objects.create(name="Selangor")
        inst = Institution.objects.create(university_name="MMU", state=state)
        club = Club.objects.create(institution=inst, name="FCI Club", ig_handle="fci")
        post = Post.objects.create(
            club=club,
            short_code="abc",
            caption="Date: 29th April 2026 Time: 8:00 PM – 10:30 PM Venue: Agmo Space",
            timestamp=timezone.now()
        )
        
        # Setup request and user
        factory = RequestFactory()
        request = factory.get('/')
        user = User.objects.create_user(email="test@mmu.edu.my", student_name="Test Student", student_id="1211100000", password="pass")
        request.user = user
        
        response = event_detail(request, post_id=post.id)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify dummy event was created with details populated
        post.refresh_from_db()
        self.assertTrue(hasattr(post, 'events'))
        event = post.events
        self.assertEqual(event.location, "Agmo Space")
        self.assertEqual(event.event_date.year, 2026)
        self.assertEqual(event.event_date.month, 4)
        self.assertEqual(event.event_date.day, 29)
        self.assertEqual(event.start_time.hour, 20)
        self.assertEqual(event.end_time.hour, 22)


from django.urls import reverse

class Step3DashboardTestCase(TestCase):
    def setUp(self):
        self.state = State.objects.create(name="Selangor")
        self.inst = Institution.objects.create(university_name="MMU", state=self.state)
        self.club = Club.objects.create(institution=self.inst, name="FCI Club", ig_handle="fci")
        self.post = Post.objects.create(
            club=self.club,
            short_code="abc",
            caption="Date: 29th April 2026 Time: 8:00 PM – 10:30 PM Venue: Agmo Space",
            timestamp=timezone.now(),
            is_event=True
        )
        self.user = User.objects.create_superuser(
            email="admin@mmu.edu.my", 
            student_name="Admin User", 
            student_id="1211100001", 
            password="pass"
        )
        self.client.force_login(self.user)

    def test_dashboard_view(self):
        url = reverse('core:admin_data_extraction_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Step 3: Data Extraction")

    @patch('core.services.post_extraction.extract_details')
    def test_single_extraction_trigger(self, mock_extract):
        mock_extract.return_value = {
            "venue": "Test Venue",
            "date": "29th April 2026",
            "time": "8:00 PM – 10:30 PM",
            "link": "https://luma.com/test"
        }
        url = reverse('core:admin_extract_post_details', kwargs={'post_id': self.post.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Venue")

    def test_single_revert_trigger(self):
        self.post.extracted_details = {"venue": "Old Venue"}
        self.post.save()
        url = reverse('core:admin_revert_post_extraction', kwargs={'post_id': self.post.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.extracted_details, {})
