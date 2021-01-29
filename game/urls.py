from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.GameView.as_view(), name='index')
]
