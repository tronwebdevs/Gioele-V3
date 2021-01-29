from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = [
    path('', views.api_root),
    path('users/', views.get_scoreboard),
    path('users/register', views.user_registration),
    path('users/auth', views.user_authentication),
    path('users/<int:pk>', views.UserDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
