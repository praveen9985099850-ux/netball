from django.urls import path
from . import views

app_name = 'scorer'

urlpatterns = [
    path('', views.scorer_dashboard, name='dashboard'),
    path('match/<int:match_id>/update/', views.update_score, name='update_score'),
    path('match/<int:match_id>/timer/start/', views.start_timer, name='start_timer'),
    path('match/<int:match_id>/timer/pause/', views.pause_timer, name='pause_timer'),
    path('match/<int:match_id>/timer/end_quarter/', views.end_quarter, name='end_quarter'),
]
