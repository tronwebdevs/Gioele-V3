from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api import views


urlpatterns = [
    path('', views.api_root, name='index'),
    path('users/', views.get_scoreboard, name='scoreboard'),
    # path('users/register', views.user_registration, name='registration'),
    # path('users/auth', views.user_authentication, name='login'),
    path('users/me', views.user_get_me, name='user_me'),
    path('users/<int:pk>', views.user_get, name='user'),
    path('shop/', views.shop_list_items, name='shop'),
    path('shop/guns/<str:pk>', views.ShopItemDetail.as_view(), name='shop_gun'),
    path('shop/skins/<str:pk>', views.ShopItemDetail.as_view(), name='shop_skin'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
