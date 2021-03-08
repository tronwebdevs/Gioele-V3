from django.shortcuts import redirect


class AdminAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        admin_id = request.session.get('admin_id', None)
        admin_name = request.session.get('admin_name', None)
        if request.path.startswith('/admin/') and request.path != '/admin/login/' \
            and (admin_id is None or admin_name is None):
            return redirect('gadmin:login')

        return self.get_response(request)
