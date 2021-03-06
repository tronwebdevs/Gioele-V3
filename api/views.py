import datetime
import hashlib
import uuid

from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group
from django.http import Http404
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, permissions, status, exceptions

from .serializers import UserRegistrationSerializer
from .models import GUser, UserInventory, Gun, Skin
from .utils import forge_auth_token
from .exceptions import AlreadyExist, NotEnoughtCoins


@api_view(['GET'])
def api_root(request, format=True):
    return Response(data={
        'name': 'Gioele V3 API',
        'status': 200,
    })

@api_view(['PUT'])
def user_registration(request, format=True):
    data = request.data
    serializer = UserRegistrationSerializer(data=data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    guser = GUser.objects.create_user(
        username=data.get('username'),
        password=data.get('password'),
        email=data.get('email')
    )

    # TODO: send confirm email

    return Response(data=guser.to_simple_dict())

@api_view(['POST'])
def user_authentication(request, format=True):
    user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
    # Prevent admins from authenticating as gamers
    if user is not None and not user.is_staff:
        try:
            guser = GUser.objects.get(pk=user.id)
        except GUser.DoesNotExist:
            guser = GUser(user=user, auth=1, score=0)
        token = forge_auth_token(user.id, user.get_username())
        return Response(data=guser.to_simple_dict(), headers={ 'Token': token })
    else:
        raise exceptions.NotAuthenticated(detail='Dati non validi')

@api_view(['GET'])
def get_scoreboard(request, format=True):
    # Get best 10 users on database based on (higher) level
    data = list(
        map(
            lambda u: ({ 'id': u.id, 'username': u.username, 'level': u.level }),
            list(GUser.objects.filter(auth=True).order_by('-level'))[:10]
        )
    )
    return Response(data=data)

@api_view(['GET'])
def user_get(request, pk, format=True):
    try:
        user = GUser.objects.get(pk=pk)
    except GUser.DoesNotExist:
        raise Http404()
    return Response(data=user.to_simple_dict())

@api_view(['GET'])
def user_get_me(request, format=True):
    return user_get(request._request, request.user_id, format)

@api_view(['GET'])
def shop_list_items(request):
    items_format = request.GET.get('functions')
    def to_display(items):
        return list(
            map(
                lambda s: s.to_safe_dict(), items
            )
        )

    def get_gun_list(type):
        return list(
            map(
                lambda g: g.to_safe_dict(hash_funcs=(items_format != 'plain')),
                filter(lambda g: g.pattern is not None, Gun.objects.filter(type=type))
            )
        )
    
    return Response(data={
        'main_guns': get_gun_list(0),
        'side_guns': get_gun_list(1),
        'skins': to_display(Skin.objects.all()),
    })


class ShopItemDetail(APIView):
    """
    Buy an item in the shop
    """
    def _get_item(self, Item, pk):
        item = None
        try:
            item = Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            raise exceptions.NotFound('Oggetto non trovato')
        return item

    def get(self, request, pk, format=None):
        item_type = request.path.split('/')[-2]
        data = None
        if item_type == 'guns':
            data = self._get_item(Gun, pk).to_safe_dict()
        elif item_type == 'skins':
            data = self._get_item(Skin, pk).to_safe_dict()
        else:
            raise exceptions.NotFound("Item type doesn't exists")
        return Response(data=data)
    
    def post(self, request, pk, format=None):
        try:
            guser = GUser.objects.get(user_id=request.user.id)
            item_type = request.path.split('/')[-2]
            if item_type == 'guns':
                item = guser.buy_gun(pk)
            else:
                item = guser.buy_skin(pk)
        except (Gun.DoesNotExist, Skin.DoesNotExist):
            raise exceptions.NotFound('Oggetto non trovato')
        except GUser.DoesNotExist:
            raise exceptions.NotFound('Utente non trovato')
        except AlreadyExist:
            excp = exceptions.APIException('Possiedi gi?? questo oggetto')
            excp.status_code = status.HTTP_409_CONFLICT
            raise excp
        except NotEnoughtCoins:
            excp = exceptions.APIException('Non hai abbastanza gbucks')
            excp.status_code = status.HTTP_402_PAYMENT_REQUIRED
            raise excp
        else:
            return Response(data={
                'user': guser.to_simple_dict(),
                'item': item.to_safe_dict()
            })
