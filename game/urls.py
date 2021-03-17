from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.GameView.as_view(), name='index'),
    path('logout/', views.logout, name='logout'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('registrazione/', views.RegistrationView.as_view(), name='registration'),
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
    path('profilo/', views.ProfileView.as_view(), name='profile'),
]
