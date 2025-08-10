from django.urls import path
from . import views

app_name = 'public'

urlpatterns = [
    path('', views.live_match_list, name='live_match_list'),
    path('match/<int:match_id>/', views.match_scoreboard, name='match_scoreboard'),
]
