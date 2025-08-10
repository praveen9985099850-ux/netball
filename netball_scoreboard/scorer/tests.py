from django.test import TestCase
from django.contrib.auth.models import User
from public.models import Team, Match
from django.utils import timezone
from django.urls import reverse

class ScorerViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='scorer', password='password')
        self.team1 = Team.objects.create(name='Team A')
        self.team2 = Team.objects.create(name='Team B')
        self.match = Match.objects.create(
            team1=self.team1,
            team2=self.team2,
            start_time=timezone.now(),
            status='live',
            scorer=self.user
        )

    def test_scorer_dashboard_view_unauthenticated(self):
        response = self.client.get(reverse('scorer:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/scorer/')

    def test_scorer_dashboard_view_authenticated(self):
        self.client.login(username='scorer', password='password')
        response = self.client.get(reverse('scorer:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scorer/scorer_dashboard.html')

    def test_timer_control_views(self):
        self.client.login(username='scorer', password='password')

        # Start timer
        response = self.client.post(reverse('scorer:start_timer', args=[self.match.id]))
        self.assertEqual(response.status_code, 204)
        self.match.refresh_from_db()
        self.assertEqual(self.match.timer_status, 'running')

        # Pause timer
        response = self.client.post(reverse('scorer:pause_timer', args=[self.match.id]))
        self.assertEqual(response.status_code, 204)
        self.match.refresh_from_db()
        self.assertEqual(self.match.timer_status, 'paused')

        # End quarter
        response = self.client.post(reverse('scorer:end_quarter', args=[self.match.id]))
        self.assertEqual(response.status_code, 204)
        self.match.refresh_from_db()
        self.assertEqual(self.match.quarter, 2)
        self.assertEqual(self.match.timer_status, 'stopped')
