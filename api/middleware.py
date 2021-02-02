from django.http import HttpResponseForbidden
from jose import jwt

from .utils import JWT_SETTINGS, forge_auth_token


class AuthTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        authed = False
        response = None
        
        # Check if request is for API and isn't to authenticate
        if request.path.startswith('/api/') and request.path != '/api/users/auth' and (request.path != '/api/users/register' and request.method != 'PUT'):
            # Bad generated json but it's the only way in which this works
            auth_exception = HttpResponseForbidden('{"detail":"Token richiesto"}')
            auth_exception['Content-Type'] = 'application/json'
            # Check if request has token in headers
            if 'Authorization' not in request.headers or type(request.headers['Authorization']) is not str:
                return auth_exception
            # Check if token is valid
            spt_token = request.headers['Authorization'].split(' ')
            if len(spt_token) != 2 or spt_token[0] != 'Bearer' or type(spt_token[1]) is not str:
                return auth_exception

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
                return auth_exception
            
            # Useless control on user id and username types
            if type(data['id']) is not int or type(data['username']) is not str:
                return auth_exception
            
            request.user_id = data['id']
            request.user_username = data['username']
            authed = True

        # Get response view
        response = self.get_response(request)

        # Update token and add to response headers if authenticated
        if authed:
            response['Token'] = forge_auth_token(request.user_id, request.user_username)

        return response
