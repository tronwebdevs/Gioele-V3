from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = [
    path('', views.api_root),
    path('users/', views.get_scoreboard),
    path('users/register', views.user_registration),
    path('users/auth', views.user_authentication),
    path('users/me', views.user_get_me),
    path('users/<int:pk>', views.UserDetail.as_view()),
    path('shop/', views.shop_list_items),
    path('shop/guns/<str:pk>', views.ShopItemDetail.as_view()),
    path('shop/skins/<str:pk>', views.ShopItemDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
