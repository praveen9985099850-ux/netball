from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from public.models import Match, Score, Foul, Player
from django.utils import timezone
from datetime import timedelta

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
    return render(request, 'scorer/scorer_dashboard.html', context)

@login_required
def update_score(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    if request.method == 'POST':
        if match.scorer != request.user:
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

    return HttpResponseRedirect(reverse('public:match_scoreboard', args=[match_id]))

@login_required
def start_timer(request, match_id):
    match = get_object_or_404(Match, id=match_id, scorer=request.user)
    if request.method == 'POST' and match.timer_status != 'running':
        if match.timer_status == 'stopped':
            match.quarter_end_time = timezone.now() + timedelta(minutes=match.quarter_duration)
        elif match.timer_status == 'paused':
            match.quarter_end_time = timezone.now() + match.remaining_time_on_pause
        match.timer_status = 'running'
        match.save()

    response = HttpResponse(status=204)
    response['HX-Trigger'] = 'timerUpdated'
    return response

@login_required
def pause_timer(request, match_id):
    match = get_object_or_404(Match, id=match_id, scorer=request.user)
    if request.method == 'POST' and match.timer_status == 'running':
        match.remaining_time_on_pause = match.quarter_end_time - timezone.now()
        match.timer_status = 'paused'
        match.save()

    response = HttpResponse(status=204)
    response['HX-Trigger'] = 'timerUpdated'
    return response

@login_required
def end_quarter(request, match_id):
    match = get_object_or_404(Match, id=match_id, scorer=request.user)
    if request.method == 'POST':
        if match.quarter < 4:
            match.quarter += 1
            match.timer_status = 'stopped'
            match.quarter_end_time = None
            match.remaining_time_on_pause = None
        else:
            match.status = 'finished'
        match.save()

    response = HttpResponse(status=204)
    response['HX-Trigger'] = 'timerUpdated'
    return response
