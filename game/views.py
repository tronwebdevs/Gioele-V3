from django.shortcuts import render
from django.views import generic
from django.urls import reverse
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect

from api.models import BannedUser, GUser


class LoginView(generic.TemplateView):
    template_name = 'game/login.html'

    def post(self, request):
        error = None
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
                request.session['user_id'] = guser.user.id
            except GUser.DoesNotExist:
                error = {
                    'code': 3,
                    'message': 'Giocatore non trovato (utente valido)',
                }

        if error is None:
            return HttpResponseRedirect(reverse('game:index'))
        else:
            return self.render_to_response({ 'error': error }, status=403)


def game(request):
    return render(request, 'game/index.html', { 'user': request.user })


def logout(request):
    del request.session['user_id']

    return HttpResponseRedirect(reverse('game:login'))
