import json
from http.cookies import SimpleCookie

from django.http import HttpResponseForbidden
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from jose import jwt

from .utils import JWT_SETTINGS, forge_auth_token
from .models import GUser

def authenticator(headers, key):
    auth_exception = Exception('Token richiesto')
    # Check if request has token in headers
    if key not in headers or type(headers[key]) is not str:
        raise auth_exception
    
    spt_token = headers[key].split(' ')
    # Check if token is valid
    if len(spt_token) != 2 or spt_token[0] != 'Bearer' or type(spt_token[1]) is not str:
        raise auth_exception

    try:
        # Verify and decode token
        data = jwt.decode(
            spt_token[1],
            JWT_SETTINGS['secret'],
            algorithms=[JWT_SETTINGS['algorithm']],
            audience=JWT_SETTINGS['audience'],
            issuer=JWT_SETTINGS['issuer']
        )
    except:
        raise auth_exception
    
    # Useless control on user id and username types
    if type(data['id']) is not int or type(data['username']) is not str:
        raise auth_exception

    return data


class AuthTokenMiddleware:
    _paths_blacklist = ('/api/users/auth', '/api/users/register', '/api/vl')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        authed = False
        response = None
        
        # Check if request is for API and isn't to authenticate
        if request.path.startswith('/api/') and request.path not in self._paths_blacklist:
            try:
                data = authenticator(headers=request.headers, key='Authorization')
                request.user_id = data['id']
                request.user_username = data['username']
                authed = True
            except:
                resp = HttpResponseForbidden(json.dumps({ 'detail': 'Token richiesto' }))
                resp['Content-Type'] = 'application/json'
                return resp

        # Get response view
        response = self.get_response(request)

        # Update token and add to response headers if authenticated
        if authed:
            response['Token'] = forge_auth_token(request.user_id, request.user_username)

        return response


class WebSocketAuthMiddleware:
    def __init__(self, app):
        self.app = app

    @database_sync_to_async
    def get_user(self, user_id):
        return GUser.objects.get(pk=user_id)
    
    @database_sync_to_async
    def get_from_session(self, session, key):
        return session.get(key)

    async def __call__(self, scope, receive, send):
        visit_id = await self.get_from_session(scope['session'], 'visit_id')
        scope['visit_id'] = visit_id

        user_id = await self.get_from_session(scope['session'], 'user_id')
        try:
            scope['user'] = await self.get_user(user_id)
        except GUser.DoesNotExist:
            scope['user'] = AnonymousUser()

        return await self.app(scope, receive, send)