from django.shortcuts import render
from django.views import generic
from django.shortcuts import redirect
from django.contrib.auth import authenticate

from api.models import BannedUser, GUser


class LoginView(generic.TemplateView):
    template_name = 'game/login.html'

    def get(self, request, *args, **kwargs):
        if request.session.get('user_id') is not None:
            return redirect('game:index')

        return super().get(request, *args, **kwargs)

    def post(self, request):
        error = None
        guser = None
        user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
        if user is None:
            error = {
                'code': 1,
                'message': 'Username o password errati',
            }
        elif not user.is_active:
            banned = BannedUser.objects.get(user__user=user)
            error = {
                'code': 2,
                'message': 'Sei stato bannato per: "%s"' % banned.reason,
            }
        elif user.is_staff:
            error = {
                'code': 3,
                'message': 'Gli admin non possono giocare',
            }
        else:
            try:
                guser = GUser.objects.get(user=user)
                request.session['user_id'] = guser.id
            except GUser.DoesNotExist:
                error = {
                    'code': 3,
                    'message': 'Giocatore non trovato (utente valido)',
                }

        if error is None and guser is not None:
            guser.log_login(request.session['visit_id'])
            return redirect('game:index')
        else:
            return self.render_to_response({ 'error': error }, status=403)


def game(request):
    return render(request, 'game/index.html', { 'user': request.user })


def logout(request):
    del request.session['user_id']

    return redirect('game:login')
