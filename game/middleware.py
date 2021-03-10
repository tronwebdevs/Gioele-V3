import json

from django.http import HttpResponseRedirect, HttpResponseServerError, HttpResponseForbidden

from api.models import VisitLog, GUser


class GameMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):# or request.path.startswith('/api/'):
            return self.get_response(request)

        visit_id = request.session.get('visit_id')
        try:
            visit = VisitLog.objects.get(pk=visit_id)
        except VisitLog.DoesNotExist:
            # Register new visit on database
            visit = VisitLog.objects.create(
                ip='127.0.0.1',
                platform='',
                lang='',
                browser='',
                screen_width=0,
                screen_height=0,
                referrer=None,
            )
            request.session['visit_id'] = str(visit.id)
            
        # Set custom internal header used in views' response generation
        request.visit = visit

        user_id = request.session.get('user_id')
        if request.path != '/login/':
            if user_id is None:
                if request.path.startswith('/api/'):
                    return HttpResponseForbidden(
                        json.dumps({ 'detail': 'Token richiesto' }),
                        content_type='application/json'
                    )
                else:
                    return HttpResponseRedirect('/login')
            
            try:
                user = GUser.objects.get(pk=user_id)
            except GUser.DoesNotExist:
                return HttpResponseServerError('Unexpected user\'s id')
            request.user = user
        
        response = self.get_response(request)
        response.set_cookie('visit_id', str(visit_id))
        return response
