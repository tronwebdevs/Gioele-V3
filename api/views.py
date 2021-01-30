import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group
from django.http import Http404
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, permissions, status, exceptions

from .serializers import UserRegistrationSerializer, UserSerializer, VisitorSerializer, ScoreboardUserSerializer, DisplayUserSeializer
from .models import GUser, Visitor, UserInventory
from .utils import forge_auth_token

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

    # TODO: Code has to be clean up with a custom manager under GUser
    user = User.objects.create_user(username=data['username'], password=data['password'], email=data['email'])
    inventory = UserInventory.objects.create(main_gun=None, side_gun=None, skins=None)
    guser = GUser.objects.create(user=user, inventory=inventory)

    # TODO: send confirm email

    # reponse_user = UserSerializer(guser)
    # return Response(reponse_user.data, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def user_authentication(request, format=True):
    authentication_failed_exception = exceptions.NotAuthenticated(detail='Dati non validi')
    if 'username' not in request.data or 'password' not in request.data:
        raise authentication_failed_exception
    
    user = authenticate(username=request.data['username'], password=request.data['password'])
    if user is not None:
        try:
            guser = GUser.objects.get(pk=user.id)
        except GUser.DoesNotExist:
            guser = GUser(user=user, auth=1, score=0)
        serializer = DisplayUserSeializer(guser)
        token = forge_auth_token(user.id, user.get_username())
        return Response(data=serializer.data, headers={ 'Token': token })
    else:
        raise authentication_failed_exception

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
        serializer = DisplayUserSeializer(user)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request, pk, format=None):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
