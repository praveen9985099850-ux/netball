from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Player(models.Model):
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')

    def __str__(self):
        return f"{self.name} ({self.team.name})"

class Match(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('live', 'Live'),
        ('finished', 'Finished'),
    )
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    start_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')
    scorer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='matches')

    def __str__(self):
        return f"{self.team1} vs {self.team2} at {self.start_time}"

class Score(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='scores')
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('match', 'team')

    def __str__(self):
        return f"{self.team.name}: {self.score} in {self.match}"

class Foul(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='fouls')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='fouls')
    count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('match', 'player')

    def __str__(self):
        return f"{self.player.name}: {self.count} fouls in {self.match}"
