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

from .serializers import UserRegistrationSerializer, UserSerializer, VisitLogSerializer, ScoreboardUserSerializer, DisplayUserSerializer, GunSerializer, SkinSerializer
from .models import GUser, VisitLog, UserInventory, Gun, Skin
from .utils import forge_auth_token
from .exceptions import AlreadyExist, NotEnoughtCoins

@api_view(['GET'])
def api_root(request, format=True):
    base_url = 'http://127.0.0.1:8000/api/'
    paths = (
        'users/',
        'users/register/',
        'users/0/',
        'visitors/',
    )
    if settings.DEBUG:
        resp_data = {
            'name': 'Gioele V3 API',
            'version': '0.0.1',
            'paths': [base_url + p for p in paths],
        }
    else:
        resp_data = { 'name': 'Gioele V3 API', }
    return Response(resp_data)

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

    user_serializer = DisplayUserSerializer(guser)
    return Response(user_serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def user_authentication(request, format=True):
    user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
    # Prevent admins from authenticating as gamers
    if user is not None and not user.is_staff:
        try:
            guser = GUser.objects.get(pk=user.id)
        except GUser.DoesNotExist:
            guser = GUser(user=user, auth=1, score=0)
        serializer = DisplayUserSerializer(guser)
        token = forge_auth_token(user.id, user.get_username())
        return Response(data=serializer.data, headers={ 'Token': token })
    else:
        raise exceptions.NotAuthenticated(detail='Dati non validi')

@api_view(['GET'])
def get_scoreboard(request, format=True):
    # Get best 10 users on database based on (best) score
    queryset = GUser.objects.filter(auth=True).order_by('-score')[:10]
    serializer = ScoreboardUserSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def user_get_me(request, format=True):
    return UserDetail().get(request, request.user_id, format)


class UserDetail(APIView):
    """
    Retrieve, update or delete a user instance
    """
    def get_object(self, pk):
        try:
            return GUser.objects.get(pk=pk)
        except GUser.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = DisplayUserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, pk, format=None):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['GET'])
def shop_list_items(reqeust, format=None):
    def to_display(item):
        return {
            'id': item.get_displayable_id(),
            'name': item.name,
            'price': item.price,
        }
    
    data = dict()
    guns = Gun.objects.all()
    main_guns = filter(lambda g: g.type == 0, guns)
    data['main_guns'] = list(map(to_display, main_guns))
    side_guns = filter(lambda g: g.type == 1, guns)
    data['side_guns'] = list(map(to_display, side_guns))
    data['skins'] = list(map(to_display, Skin.objects.all()))
    return Response(data=data)


class ShopItemDetail(APIView):
    """
    Buy an item in the shop
    """
    def _get_item(self, Item, hashed_id):
        item = None
        for i in Item.objects.all():
            if hashlib.md5(i.id.encode()).hexdigest() == hashed_id:
                item = i
        if item is None:
            raise exceptions.NotFound('Oggetto non trovato')
        return item

    def _get_item_serializer(self, path, pk):
        item_type = path.split('/')[-2]
        serializer = None
        if item_type == 'guns':
            serializer = GunSerializer(self._get_item(Gun, pk))
        elif item_type == 'skins':
            serializer = SkinSerializer(self._get_item(Skin, pk))
        else:
            raise exceptions.NotFound("Item type doesn't exists")
        return serializer

    def get(self, request, pk, format=None):
        serializer = self._get_item_serializer(request.path, pk)
        return Response(serializer.data)
    
    def post(self, request, pk, format=None):
        serializer = self._get_item_serializer(request.path, pk)
        user = GUser.objects.get(pk=request.user_id)
        item_type = request.path.split('/')[-2]
        try:
            if item_type == 'guns':
                user.buy_gun(pk)
            else:
                user.buy_skin(pk)
        except AlreadyExist:
            excp = exceptions.APIException('Possiedi già questo oggetto')
            excp.status_code = status.HTTP_409_CONFLICT
            raise excp
        except NotEnoughtCoins:
            excp = exceptions.APIException('Non hai abbastanza gbucks')
            excp.status_code = status.HTTP_402_PAYMENT_REQUIRED
            raise excp
        duser = DisplayUserSerializer(user)
        data = {'user': duser.data, 'item': serializer.data}
        return Response(data=data)

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