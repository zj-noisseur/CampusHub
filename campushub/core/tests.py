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
            timestamp=timezone.now(),
            is_event=True
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


class ManagerDashboardExtractedDetailsTestCase(TestCase):
    def setUp(self):
        self.state = State.objects.create(name="Selangor")
        self.inst = Institution.objects.create(university_name="MMU", state=self.state)
        self.club = Club.objects.create(institution=self.inst, name="FCI Club", ig_handle="fci")
        
        # Create a user and a manager membership
        self.user = User.objects.create_user(
            email="manager@mmu.edu.my", 
            student_name="Club Manager", 
            student_id="1211100002", 
            password="pass"
        )
        
        # Add the manager to the club managers
        from core.models import ClubManager
        self.club_manager = ClubManager.objects.create(
            club=self.club,
            user=self.user,
            role="ROOT",
            is_active=True
        )
        
        self.post = Post.objects.create(
            club=self.club,
            short_code="def",
            caption="Event post details",
            timestamp=timezone.now(),
            is_event=True,
            extracted_details={
                "date": "29th May 2026",
                "venue": "Old Venue",
                "link": "https://old.link",
                "dates": ["29th May 2026", "30th May 2026"],
                "venues": ["Old Venue", "New Venue"],
                "links": ["https://old.link", "https://new.link"]
            }
        )
        
        # Create associated Event
        from core.views.event_detail import parse_date
        self.event = Event.objects.create(
            club=self.club,
            post=self.post,
            title="Imported Event",
            event_date=parse_date("29th May 2026"),
            location="Old Venue",
            requires_approval=True
        )
        
        self.client.force_login(self.user)

    def test_manager_dashboard_context_has_event_posts(self):
        url = reverse('core:manager_dashboard', kwargs={'club_id': self.club.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('event_posts', response.context)
        self.assertEqual(len(response.context['event_posts']), 1)

    def test_update_post_extracted_details_select_choices(self):
        url = reverse('core:update_post_extracted_details', kwargs={'club_id': self.club.id, 'post_id': self.post.id})
        post_data = {
            'date_choice': '30th May 2026',
            'venue_choice': 'New Venue',
            'link_choice': 'https://new.link',
            'custom_date': '',
            'custom_venue': '',
            'custom_link': ''
        }
        response = self.client.post(url, post_data)
        self.assertRedirects(response, reverse('core:manager_dashboard', kwargs={'club_id': self.club.id}))
        
        self.post.refresh_from_db()
        self.assertEqual(self.post.extracted_details['date'], '30th May 2026')
        self.assertEqual(self.post.extracted_details['venue'], 'New Venue')
        self.assertEqual(self.post.extracted_details['link'], 'https://new.link')
        
        self.event.refresh_from_db()
        self.assertEqual(self.event.event_date.year, 2026)
        self.assertEqual(self.event.event_date.month, 5)
        self.assertEqual(self.event.event_date.day, 30)
        self.assertEqual(self.event.location, 'New Venue')

    def test_update_post_extracted_details_custom_input(self):
        url = reverse('core:update_post_extracted_details', kwargs={'club_id': self.club.id, 'post_id': self.post.id})
        post_data = {
            'date_choice': '30th May 2026',
            'venue_choice': 'New Venue',
            'link_choice': 'https://new.link',
            'custom_date': '31st May 2026',
            'custom_venue': 'Super Custom Venue',
            'custom_link': 'https://custom.link'
        }
        response = self.client.post(url, post_data)
        self.assertRedirects(response, reverse('core:manager_dashboard', kwargs={'club_id': self.club.id}))
        
        self.post.refresh_from_db()
        self.assertEqual(self.post.extracted_details['date'], '31st May 2026')
        self.assertEqual(self.post.extracted_details['venue'], 'Super Custom Venue')
        self.assertEqual(self.post.extracted_details['link'], 'https://custom.link')
        
        self.event.refresh_from_db()
        self.assertEqual(self.event.event_date.year, 2026)
        self.assertEqual(self.event.event_date.month, 5)
        self.assertEqual(self.event.event_date.day, 31)
        self.assertEqual(self.event.location, 'Super Custom Venue')


class UpcomingEventExtractionGuardTestCase(TestCase):
    def setUp(self):
        self.state = State.objects.create(name="Selangor")
        self.inst = Institution.objects.create(university_name="MMU", state=self.state)
        self.club = Club.objects.create(institution=self.inst, name="FCI Club", ig_handle="fci")
        self.user = User.objects.create_superuser(
            email="admin@mmu.edu.my", 
            student_name="Admin User", 
            student_id="1211100001", 
            password="pass"
        )
        self.client.force_login(self.user)
        
        # Post that is NOT classified as event
        self.non_event_post = Post.objects.create(
            club=self.club,
            short_code="non",
            caption="Just regular announcement",
            timestamp=timezone.now(),
            is_event=False
        )

        # Post that IS classified as event
        self.event_post = Post.objects.create(
            club=self.club,
            short_code="eve",
            caption="Upcoming workshop details",
            timestamp=timezone.now(),
            is_event=True
        )

    def test_admin_extract_non_event_post_details_fails(self):
        url = reverse('core:admin_extract_post_details', kwargs={'post_id': self.non_event_post.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Post is not classified as an upcoming event.", status_code=400)

    @patch('core.services.tasks.extract_details.delay')
    @patch('core.services.post_categorization.predict_post_category')
    @patch('core.services.post_categorization.assign_event_status_to_post')
    def test_classify_post_skips_extraction_if_not_event(self, mock_assign, mock_predict, mock_extract_delay):
        mock_predict.return_value = 'MISC'
        
        # Simulate classification setting is_event to False
        def side_effect(post, *args, **kwargs):
            post.is_event = False
            post.save()
            return False
        mock_assign.side_effect = side_effect
        
        from core.services.tasks import classify_post
        result = classify_post(self.non_event_post.id)
        
        self.assertEqual(result['status'], 'success')
        mock_extract_delay.assert_not_called()

    @patch('core.services.tasks.extract_details.delay')
    @patch('core.services.post_categorization.predict_post_category')
    @patch('core.services.post_categorization.assign_event_status_to_post')
    def test_classify_post_triggers_extraction_if_event(self, mock_assign, mock_predict, mock_extract_delay):
        mock_predict.return_value = 'WORKSHOP'
        
        # Simulate classification setting is_event to True
        def side_effect(post, *args, **kwargs):
            post.is_event = True
            post.save()
            return True
        mock_assign.side_effect = side_effect
        
        from core.services.tasks import classify_post
        result = classify_post(self.event_post.id)
        
        self.assertEqual(result['status'], 'success')
        mock_extract_delay.assert_called_once_with(self.event_post.id)

    def test_extract_details_task_skips_if_not_event(self):
        from core.services.tasks import extract_details
        result = extract_details(self.non_event_post.id)
        self.assertEqual(result['status'], 'skipped_not_event')


class RetrieveJsonTestCase(TestCase):
    def setUp(self):
        self.state = State.objects.create(name="Selangor")
        self.inst = Institution.objects.create(university_name="MMU", state=self.state)
        self.club = Club.objects.create(institution=self.inst, name="FCI Club", ig_handle="fci")

    @patch('core.services.tasks.fetch_instagram_posts_via_apify')
    def test_retrieve_json_no_failed_extractions(self, mock_fetch):
        mock_fetch.return_value = []
        Post.objects.create(
            club=self.club,
            short_code="abc",
            caption="Normal caption",
            timestamp=timezone.now(),
            is_event=True,
            extracted_details={"venue": "Agmo"}
        )
        from core.services.tasks import retrieve_json
        from unittest.mock import MagicMock
        self_mock = MagicMock()
        
        retrieve_json.__wrapped__(self.club.id)
        mock_fetch.assert_called_once()
        
    @patch('core.services.tasks.fetch_instagram_posts_via_apify')
    def test_retrieve_json_with_failed_extractions(self, mock_fetch):
        mock_fetch.return_value = []
        Post.objects.create(
            club=self.club,
            short_code="def",
            caption="Failed extraction caption",
            timestamp=timezone.now(),
            is_event=True,
            extracted_details={}
        )
        from core.services.tasks import retrieve_json
        from unittest.mock import MagicMock
        self_mock = MagicMock()
        
        retrieve_json.__wrapped__(self.club.id)
        mock_fetch.assert_called_once()



