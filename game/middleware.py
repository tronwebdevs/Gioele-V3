import json

from django.http import HttpResponseRedirect, HttpResponseServerError, HttpResponseForbidden, HttpRequest
from user_agents import parse

from api.models import VisitLog, GUser


class GameMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ua = parse(request.META.get('HTTP_USER_AGENT'))

        if ua.is_bot:
            return HttpResponseForbidden()
        
        if request.path.startswith('/admin/'):
            return self.get_response(request)

        visit_id = request.session.get('visit_id')
        try:
            visit = VisitLog.objects.get(pk=visit_id)
        except VisitLog.DoesNotExist:
            device_type = -1
            if ua.is_pc:
                device_type = 0
            elif ua.is_mobile:
                device_type = 1
            elif ua.is_tablet:
                device_type = 2
            # Register new visit on database
            visit = VisitLog.objects.create(
                ip=request.META.get('REMOTE_ADDR'),
                os=ua.os.family,
                browser=ua.browser.family + '/' + ua.browser.version_string,
                device=ua.device.model or '',
                device_brand=ua.device.brand or '',
                device_type=device_type,
                has_touchscreen=ua.is_touch_capable,
                referrer=request.META.get('HTTP_REFERER') or '',
            )
            request.session['visit_id'] = str(visit.id)
            
        # Set custom internal header used in views' response generation
        request.visit = visit

        user_id = request.session.get('user_id')
        if request.path != '/login/' and request.path != '/registrazione/':
            if user_id is None:
                if request.path.startswith('/api/'):
                    return HttpResponseForbidden(
                        json.dumps({ 'detail': 'Login richiesto' }),
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
