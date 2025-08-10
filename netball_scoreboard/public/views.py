from django.shortcuts import render, get_object_or_404
from .models import Match, Score, Foul

def live_match_list(request):
    live_matches = Match.objects.filter(status='live')
    return render(request, 'public/live_match_list.html', {'live_matches': live_matches})

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
        return render(request, 'public/_scoreboard_content.html', context)

    return render(request, 'public/match_scoreboard.html', context)
