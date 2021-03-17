from django.shortcuts import render
from django.views import generic
from django.shortcuts import redirect
from django.contrib.auth import authenticate

from api.models import BannedUser, GUser
from gioele_v3.settings import DEBUG


def get_messages(request, key):
    err_key = 'u_' + key + '_error'
    error = request.session.get(err_key)
    if error is not None:
        del request.session[err_key]
    mess_key = 'u_' + key + '_message'
    message = request.session.get(mess_key)
    if message is not None:
        del request.session[mess_key]
    return { 'error': error, 'message': message }


class LoginView(generic.TemplateView):
    template_name = 'game/login.html'

    def get(self, request, *args, **kwargs):
        if request.session.get('user_id') is not None:
            return redirect('game:index')
        messages = get_messages(request, 'login')
        if messages.get('error') is not None:
            code, mess = messages['error'].split('|')
            messages['code'] = code
            messages['error'] = mess

        return self.render_to_response(messages)

    def post(self, request):
        error = None
        guser = None
        user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
        if user is None:
            error = '1|Username o password errati'
        elif not user.is_active:
            banned = BannedUser.objects.get(user__user=user)
            error = '2|Sei stato bannato per: "%s"' % banned.reason
        elif user.is_staff:
            if DEBUG:
                error = '3|Gli admin non possono giocare'
            else:
                error = '1|Username o password errati'
        else:
            try:
                guser = GUser.objects.get(user=user)
                if not guser.auth:
                    error = '4|Devi completare l\'autenticazione via email, controlla la tua casella di posta della scuola'
                else:
                    request.session['user_id'] = guser.id
            except GUser.DoesNotExist:
                error = 'Giocatore non trovato (utente valido)'

        if error is None and guser is not None:
            guser.log_login(request.session['visit_id'])
            redirect_to = 'game:index'
        else:
            request.session['u_login_error'] = error
            redirect_to = 'game:login'
        return redirect(redirect_to)


class RegistrationView(generic.TemplateView):
    template_name = 'game/registration.html'

    def get(self, request, *args, **kwargs):
        if request.session.get('user_id') is not None:
            return redirect('game:index')

        return self.render_to_response(get_messages(request, 'register'))

    def post(self, request):
        request.session['u_register_error'] = 'Not implemented yet'

        redirect_to = 'game:registration'
        return redirect(redirect_to)


class LeaderboardView(generic.TemplateView):
    template_name = 'game/leaderboard.html'

    def get(self, request):
        return self.render_to_response({
            'users': list(GUser.objects.order_by('level'))[0:10],
        })


class ProfileView(generic.TemplateView):
    template_name = 'game/profile.html'

    def get(self, request):
        return self.render_to_response({
            'user': request.user,
            'user_skins': request.user.inventory.get_skins(),
            'user_guns': request.user.inventory.get_main_guns(),
        })


class GameView(generic.TemplateView):
    template_name = 'game/game.html'

    def get(self, request):
        return self.render_to_response({
            'user': request.user,
            'debug': DEBUG,
        })


def logout(request):
    del request.session['user_id']

    return redirect('game:login')
