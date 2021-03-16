from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.game, name='index'),
    path('logout/', views.logout, name='logout'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('registrazione/', views.RegistrationView.as_view(), name='registration'),
]
