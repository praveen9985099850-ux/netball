from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'scoreboard'

urlpatterns = [
    path('', views.live_match_list, name='live_match_list'),
    path('match/<int:match_id>/', views.match_scoreboard, name='match_scoreboard'),
    path('scorer/', views.scorer_dashboard, name='scorer_dashboard'),
    path('scorer/match/<int:match_id>/update/', views.update_score, name='update_score'),
    path('login/', auth_views.LoginView.as_view(template_name='scoreboard/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='scoreboard:live_match_list'), name='logout'),
]
