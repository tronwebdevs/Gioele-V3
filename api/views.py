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
from .models import GUser, VisitLog, UserInventory, Gun, Skin
from .utils import forge_auth_token
from .exceptions import AlreadyExist, NotEnoughtCoins


@api_view(['GET'])
def api_root(request, format=True):
    return Response(data={
        'name': 'Gioele V3 API',
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
def shop_list_items(reqeust, format=None):
    def to_display(item):
        obj = item.to_dict()
        hashes = item.get_hashes()
        obj['shoot'] = hashes['shoot']
        obj['pattern'] = hashes['pattern']
        obj['behavior'] = hashes['behavior']
        return obj

    def get_gun_list(type):
        return list(
            map(
                to_display,
                filter(lambda g: g.pattern is not None, Gun.objects.filter(type=type))
            )
        )
    
    return Response(data={
        'main_guns': get_gun_list(0),
        'side_guns': get_gun_list(1),
        'skins': list(map(lambda s: s.to_dict(), Skin.objects.all()))
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
            data = self._get_item(Gun, pk).to_dict()
            data['behavior'] = data['pattern']['behavior']
            data['pattern'] = data['pattern']['function']
        elif item_type == 'skins':
            data = self._get_item(Skin, pk).to_dict()
        else:
            raise exceptions.NotFound("Item type doesn't exists")
        return Response(data=data)
    
    def post(self, request, pk, format=None):
        try:
            guser = GUser.objects.get(user_id=request.user_id)
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
            excp = exceptions.APIException('Possiedi già questo oggetto')
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


@api_view(['POST'])
def visit(request):
    lang = request.data.get('l')
    browser = request.data.get('ua')
    platform = request.data.get('p')
    screen_width = request.data.get('sw')
    screen_height = request.data.get('sh')
    referrer = request.data.get('r')
    has_touchscreen = request.data.get('ts')
    if lang is not None and \
        browser is not None and \
        platform is not None and \
        screen_width is not None and \
        screen_height is not None and \
        referrer is not None and \
        has_touchscreen is not None:

        visit_id = request.get_cookie('visit_id')
        try:
            visit_log = VisitLog.objects.get(pk=uuid.UUID(visit_id))
            visit_log.lang = lang
            visit_log.browser = browser
            visit_log.platform = platform
            visit_log.screen_width = screen_width
            visit_log.screen_height = screen_height
            visit_log.referrer = referrer
            visit_log.has_touchscreen = has_touchscreen
            visit_log.updated_at = timezone.now()
            visit_log.save()
            print('Visit log updated')
        except VisitLog.DoesNotExist:
            print('Visit id not found')
    return Response(status=status.HTTP_204_NO_CONTENT)
