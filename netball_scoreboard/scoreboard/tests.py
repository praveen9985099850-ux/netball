from django.test import TestCase
from django.contrib.auth.models import User
from .models import Team, Player, Match, Score, Foul
from django.utils import timezone
from django.urls import reverse

class ScoreboardModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='scorer', password='password')
        self.team1 = Team.objects.create(name='Team A')
        self.team2 = Team.objects.create(name='Team B')
        self.player1 = Player.objects.create(name='Player 1', team=self.team1)
        self.match = Match.objects.create(
            team1=self.team1,
            team2=self.team2,
            start_time=timezone.now(),
            scorer=self.user
        )
        self.score = Score.objects.create(match=self.match, team=self.team1, score=10)
        self.foul = Foul.objects.create(match=self.match, player=self.player1, count=3)

    def test_team_creation(self):
        self.assertEqual(self.team1.name, 'Team A')
        self.assertEqual(str(self.team1), 'Team A')

    def test_player_creation(self):
        self.assertEqual(self.player1.name, 'Player 1')
        self.assertEqual(str(self.player1), 'Player 1 (Team A)')

    def test_match_creation(self):
        self.assertEqual(self.match.team1, self.team1)
        self.assertEqual(self.match.team2, self.team2)
        self.assertIn('Team A vs Team B', str(self.match))

    def test_score_creation(self):
        self.assertEqual(self.score.score, 10)
        self.assertIn('Team A: 10', str(self.score))

    def test_foul_creation(self):
        self.assertEqual(self.foul.count, 3)
        self.assertIn('Player 1: 3 fouls', str(self.foul))


class ScoreboardViewsTestCase(TestCase):
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

    def test_live_match_list_view(self):
        response = self.client.get(reverse('scoreboard:live_match_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scoreboard/live_match_list.html')

    def test_match_scoreboard_view(self):
        response = self.client.get(reverse('scoreboard:match_scoreboard', args=[self.match.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scoreboard/match_scoreboard.html')

    def test_scorer_dashboard_view_unauthenticated(self):
        response = self.client.get(reverse('scoreboard:scorer_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/scorer/')

    def test_scorer_dashboard_view_authenticated(self):
        self.client.login(username='scorer', password='password')
        response = self.client.get(reverse('scoreboard:scorer_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scoreboard/scorer_dashboard.html')
