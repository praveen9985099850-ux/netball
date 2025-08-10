from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Match, Score, Foul, Player

def live_match_list(request):
    live_matches = Match.objects.filter(status='live')
    return render(request, 'scoreboard/live_match_list.html', {'live_matches': live_matches})

def match_scoreboard(request, match_id):
    match = get_object_or_404(
        Match.objects.prefetch_related('team1__players', 'team2__players'),
        id=match_id
    )
    scores = Score.objects.filter(match=match).order_by('team__name')
    fouls = {foul.player_id: foul.count for foul in Foul.objects.filter(match=match)}

    context = {
        'match': match,
        'scores': scores,
        'fouls': fouls,
    }

    if request.htmx:
        return render(request, 'scoreboard/_scoreboard_content.html', context)

    return render(request, 'scoreboard/match_scoreboard.html', context)

@login_required
def scorer_dashboard(request):
    assigned_matches = Match.objects.filter(scorer=request.user, status='live').prefetch_related(
        'scores', 'team1__players', 'team2__players', 'fouls'
    )

    matches_data = []
    for match in assigned_matches:
        scores = {score.team_id: score.score for score in match.scores.all()}
        fouls = {foul.player_id: foul.count for foul in match.fouls.all()}
        matches_data.append({
            'match': match,
            'scores': scores,
            'fouls': fouls,
        })

    all_matches = Match.objects.filter(status='live')
    context = {
        'matches_data': matches_data,
        'all_matches': all_matches,
    }
    return render(request, 'scoreboard/scorer_dashboard.html', context)

from django.http import HttpResponse

@login_required
def update_score(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    if request.method == 'POST':
        # Only the assigned scorer can update the score
        if match.scorer != request.user:
            # Handle unauthorized attempt
            return HttpResponse(status=403)

        team1_score = request.POST.get('team1_score')
        team2_score = request.POST.get('team2_score')

        score1, _ = Score.objects.get_or_create(match=match, team=match.team1)
        score1.score = team1_score
        score1.save()

        score2, _ = Score.objects.get_or_create(match=match, team=match.team2)
        score2.score = team2_score
        score2.save()

        for key, value in request.POST.items():
            if key.startswith('player_foul_'):
                player_id = key.replace('player_foul_', '')
                player = get_object_or_404(Player, id=player_id)
                foul, _ = Foul.objects.get_or_create(match=match, player=player)
                foul.count = value
                foul.save()

        response = HttpResponse(status=204)
        response['HX-Trigger'] = 'scoreUpdated'
        return response

    # If not a POST request, redirect to the scoreboard
    return HttpResponseRedirect(reverse('scoreboard:match_scoreboard', args=[match_id]))
