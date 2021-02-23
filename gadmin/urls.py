from django.urls import path
from . import views

app_name = 'gadmin'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('users/', views.UsersView.as_view(), name='users'),
    path('stats/', views.StatsView.as_view(), name='stats'),
    path('hardware/', views.hardware, name='hardware'),
    path('gbuck/', views.GBuckView.as_view(), name='gbuck'),
    path('guns/', views.GunsView.as_view(), name='guns'),
    path('skins/', views.SkinsView.as_view(), name='skins'),
]
