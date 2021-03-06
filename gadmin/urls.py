from django.urls import path
from . import views

app_name = 'gadmin'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('logs/', views.LogsView.as_view(), name='logs'),
    path('users/', views.UsersView.as_view(), name='users'),
    path('users/<str:pk>/', views.UserModelView.as_view(), name='user'),
    path('users/<str:pk>/inventory', views.UserInventoryView.as_view(), name='user_inventory'),
    path('users/<str:pk>/ban', views.UserBanView.as_view(), name='ban_user'),
    path('new_user/', views.UserModelView.as_view(), name='new_user'),
    path('stats/', views.StatsView.as_view(), name='stats'),
    path('hardware/', views.HardwareView.as_view(), name='hardware'),
    path('gbucks/', views.GBucksView.as_view(), name='gbucks'),
    path('guns/', views.GunsView.as_view(), name='guns'),
    path('guns/<str:pk>/', views.GunModelView.as_view(), name='gun'),
    path('new_gun/', views.GunModelView.as_view(), name='new_gun'),
    path('skins/', views.SkinsView.as_view(), name='skins'),
    path('skins/<str:pk>/', views.SkinModelView.as_view(), name='skin'),
    path('new_skin/', views.SkinModelView.as_view(), name='new_skin'),
    path('patterns/<str:pk>/', views.PatternModelView.as_view(), name='pattern'),
    path('new_pattern/', views.PatternModelView.as_view(), name='new_pattern'),
]
