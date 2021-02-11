import json
from http.cookies import SimpleCookie

from django.http import HttpResponseForbidden
from channels.db import database_sync_to_async
from jose import jwt

from .utils import JWT_SETTINGS, forge_auth_token
from .models import GUser

def authenticator(headers, key):
    auth_exception = Exception('Token richiesto')
    # Check if request has token in headers
    if key not in headers or type(headers[key]) is not str:
        raise auth_exception
    
    # If headers if from API request split on space, if it comes from other source
    # split on | (cookie are not allowed to have whitespaces)
    if key == 'Authorization':
        spt_token = headers[key].split(' ')
    else:
        spt_token = headers[key].split('|')
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
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        authed = False
        response = None
        
        # Check if request is for API and isn't to authenticate
        if request.path.startswith('/api/') and request.path != '/api/users/auth' and (request.path != '/api/users/register' and request.method != 'PUT'):
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

@database_sync_to_async
def get_user(user_id):
    return GUser.objects.get(pk=user_id)


class WebSocketAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        cookies = SimpleCookie()
        for i, header in enumerate(scope['headers']):
            if header[0] == b'cookie':
                cookies.load(scope['headers'][i][1].decode())
                break
        headers = dict()
        for c in cookies:
            headers[c] = cookies[c].value
        data = authenticator(headers=headers, key='token')
        scope["user"] = await get_user(data['id'])
        return await self.app(scope, receive, send)