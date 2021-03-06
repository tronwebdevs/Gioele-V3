from django.shortcuts import render
from django.views import generic
from django.shortcuts import redirect
from django.contrib.auth import authenticate

from gadmin.utils import valid_string, valid_email, valid_number
from api.models import BannedUser, GUser, Gun, Skin
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

def raise_if_not_valid(val, validator, message):
    if not validator(val):
        raise Exception(message)
    return val


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
            **get_messages(request, 'profile'),
        })

    def post(self, request):
        try:
            user = request.user.user
            new_username = raise_if_not_valid(request.POST.get('username'), valid_string, 'Username non valido')
            if len(GUser.objects.filter(user__username=new_username)) > 0:
                raise Exception('Questo username ?? gi?? in uso')
            else:
                user.username = new_username
            raw_pass = raise_if_not_valid(request.POST.get('password'), valid_string, 'Password errata')

            if not user.check_password(raw_pass):
                raise Exception('Password errata')

            post_new_pass = request.POST.get('npassword')
            if post_new_pass is not None and post_new_pass.strip() != '':
                new_raw_pass = raise_if_not_valid(request.POST.get('npassword'), valid_string, 'Nuova password errata')
                new_raw_cpass = raise_if_not_valid(request.POST.get('cnpassword'), valid_string, 'Conferma nuova password errata')
                if new_raw_pass != new_raw_cpass:
                    raise Exception('Le password non coincidono')
                else:
                    user.set_password(new_raw_pass)

            user.save()
        except Exception as e:
            request.session['u_profile_error'] = str(e)
        else:
            request.session['u_profile_message'] = 'Profilo aggiornato'

        return redirect('game:profile')


class ShopView(generic.TemplateView):
    template_name = 'game/shop.html'

    def get(self, request):
        uinv = request.user.inventory
        user_guns = list(map(lambda g: g['id'], uinv.get_main_guns() + uinv.get_side_guns()))
        user_skins = list(map(lambda s: s['id'], uinv.get_skins()))
        return self.render_to_response({
            'user': request.user,
            'main_guns': list(Gun.objects.filter(type=0)),
            'side_guns': list(Gun.objects.filter(type=1)),
            'skins': list(Skin.objects.all()),
            'user_guns': user_guns,
            'user_skins': user_skins,
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
