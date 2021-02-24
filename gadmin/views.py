import platform
import subprocess
import hashlib

import psutil
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from django.contrib.auth import authenticate
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm

from api.utils import generate_short_id
from api.models import User, GUser, BannedUser, Gun, Skin, GameLog, VisitLog, Stat, PurchaseLog, AdminLog


def get_percentage(current, last):
    if last != 0:
        return str((current - last) * 100 / last) + '%'
    else:
        return '+0%'


def get_user(user_id):
    try:
        return GUser.objects.get(pk=user_id)
    except GUser.DoesNotExist:
        return None

def get_selected_items(dataset, user_dataset):
    dataset = list(map(lambda i: i.readable_dict(), dataset))
    for mi in dataset:
        mi['owned'] = False
        for ui in user_dataset:
            if mi['id'] == ui['id']:
                mi['owned'] = True
                break
    return dataset


def index(request):
    users_dataset = list(Stat.objects.filter(key='users'))[:16]
    visitors_dataset = list(Stat.objects.filter(key='visitors'))[:16]
    games_dataset = list(Stat.objects.filter(key='games'))[:16]
    visitors = VisitLog.objects.count()
    users = GUser.objects.count()
    matches = GameLog.objects.count()
    purchases = PurchaseLog.objects.count()
    context = {
        'stats': {
            'visitors': visitors,
            'users': users,
            'matches': matches,
            'purchases': purchases,
        },
        'percentages': {
            'users': get_percentage(users, users_dataset[-1].value),
            'visitors': get_percentage(visitors, visitors_dataset[-1].value),
            'matches': get_percentage(matches, games_dataset[-1].value),
        },
        'charts_data': {
            'users': users_dataset + [Stat(key='users',value=users)],
            'visitors': visitors_dataset + [Stat(key='visitors',value=visitors)],
            'games': games_dataset + [Stat(key='games',value=matches)],
        }
    }
    return render(request, 'gadmin/index.html', context)


class LoginView(generic.TemplateView):
    template_name = 'gadmin/login.html'

    def post(self, request):
        user = authenticate(username=request.POST.get(
            'username'), password=request.POST.get('password'))
        if user is not None and user.is_staff:
            request.session['admin_id'] = user.id
            request.session['admin_name'] = user.username
            return HttpResponseRedirect(reverse('gadmin:index'))
        context = {'message': 'Dati non validi'}
        return self.render_to_response(context)


def users(request):
    context = {
        'error': 'An error occurred' if request.GET.get('m') == 'err' else None,
        'message': 'Completed successfully' if request.GET.get('m') == 'ok' else None,
        'users': GUser.objects.filter(user__is_active=True),
        'banned': BannedUser.objects.all(),
    }
    return render(request, 'gadmin/users.html', context)


class UserBanView(generic.View):
    def get(self, request, pk):
        user = get_user(pk)
        if user is None:
            return HttpResponseRedirect(reverse('gadmin:users'))
        return render(request, 'gadmin/ban_user.html', { 'user': user })
    def post(self, request, pk):
        user = get_user(pk)
        username = request.POST.get('username')
        reason = request.POST.get('reason')
        if user is None or (reason is None or reason == '') or user.user.username != username:
            return HttpResponseRedirect(reverse('gadmin:users') + '?m=err')
        admin = User.objects.get(pk=request.session.get('admin_id'))
        user_id = user.user.id
        BannedUser.objects.ban(
            user_id=user_id,
            reason=reason,
            by=admin
        )
        AdminLog.objects.create(action=f'Banned user #{user_id}', by=admin)
        return HttpResponseRedirect(reverse('gadmin:users') + '?m=ok')


class UserInventoryView(generic.View):
    def get(self, request, pk=None):
        return HttpResponseRedirect(reverse('gadmin:users'))
    def post(self, request, pk=None):
        user = get_user(pk)
        if user is None:
            return HttpResponseRedirect(reverse('gadmin:users')  + '?m=err')
        user.inventory.main_guns = None
        for gid in request.POST.getlist('main_guns'):
            if len(Gun.objects.filter(pk=gid)) > 0:
                user.inventory.add_main_gun(gid)
        user.inventory.side_guns = None
        for gid in request.POST.getlist('side_guns'):
            if len(Gun.objects.filter(pk=gid)) > 0:
                user.inventory.add_side_gun(gid)
        user.inventory.skins = None
        for sid in request.POST.getlist('skins'):
            if len(Skin.objects.filter(pk=sid)) > 0:
                user.inventory.add_skin(sid)
        user.inventory.save()
        AdminLog.objects.create(
            action=f'Edited user #{user.user.id} inventory',
            by=User.objects.get(pk=request.session.get('admin_id'))
        )
        return HttpResponseRedirect(reverse('gadmin:users') + '?m=ok')


class UserModelView(generic.TemplateView):
    template_name = 'gadmin/user_form.html'

    def _craft_context(self, user):
        user_games = GameLog.objects.filter(user=user).order_by('exp_gained')
        games = None
        if len(user_games) > 0:
            games = {
                'count': len(user_games),
                'best': user_games[0],
            }
        user_purchases = PurchaseLog.objects.filter(by=user).order_by('price')
        purchases = None
        if len(user_purchases) > 0:
            purchases = {
                'count': len(user_purchases),
                'highest': user_purchases[0],
            }
        ban = None
        if not user.user.is_active:
            ban = BannedUser.objects.get(user=user)
        return {
            'user': user,
            'main_guns': get_selected_items(
                Gun.objects.filter(type=0),
                user.inventory.get_main_guns_dict(hash_id=False)
            ),
            'side_guns': get_selected_items(
                Gun.objects.filter(type=1),
                user.inventory.get_side_guns_dict(hash_id=False)
            ),
            'skins': get_selected_items(
                Skin.objects.all(),
                user.inventory.get_skins_dict(hash_id=False)
            ),
            'games': games,
            'purchases': purchases,
            'ban': ban,
        }

    def get(self, request, pk=None):
        if pk is not None:
            user = get_user(pk)
            if user is None:
                return HttpResponseRedirect(reverse('gadmin:users'))
        else:
            user = GUser(type=0, price=0, cooldown=0, damage=0)
        return self.render_to_response(self._craft_context(user))

    def post(self, request, pk):
        user_list = GUser.objects.filter(pk=pk)
        extra = ['message', 'User updated successfully']
        if len(user_list) == 0:
            user = GUser(id=pk)
        else:
            user = user_list[0]
        try:
            user.user.username = request.POST.get('username')
            user.user.email = request.POST.get('email')
            user.user.save()
            user.auth = request.POST.get('auth') == 'on'
            items = ('main_gun', 'side_gun', 'skin')
            for item in items:
                given_val = request.POST.get(item)
                val = None if given_val == '' else given_val
                setattr(user, item, val)
            user.balance = request.POST.get('balance')
            user.save()
        except Exception as e:
            extra[0] = 'error'
            extra[1] = str(e)
        context = self._craft_context(user)
        context[extra[0]] = extra[1]
        AdminLog.objects.create(
            action=f'Edited user #{user.user.id} profile',
            by=User.objects.get(pk=request.session.get('admin_id'))
        )
        return self.render_to_response(context)


def hardware(request):
    commit_hash = subprocess.check_output(
        ['git', 'log', '-1', '--pretty=%H']).strip().decode()
    commit_message = subprocess.check_output(
        ['git', 'log', '-1', '--pretty=%B']).strip().decode()
    commit_author = subprocess.check_output(
        ['git', 'log', '-1', '--pretty=%an']).strip().decode()
    context = {
        'psutil': psutil,
        'system': platform,
        'charts_data': {
            'cpu': Stat.objects.filter(key='cpu')[:10],
            'mem': Stat.objects.filter(key='mem')[:10],
        },
        'git': {
            'commit': commit_hash,
            'message': commit_message,
            'author': commit_author,
        },
    }
    return render(request, 'gadmin/hardware.html', context)


class StatsView(generic.TemplateView):
    template_name = 'gadmin/stats.html'


class GBuckView(generic.TemplateView):
    template_name = 'gadmin/gbuck.html'


class GunsView(generic.ListView):
    model = Gun
    template_name = 'gadmin/guns.html'


class GunModelView(generic.TemplateView):
    template_name = 'gadmin/gun_form.html'

    def get(self, request, pk=None):
        if pk is not None:
            try:
                gun = Gun.objects.get(pk=pk)
            except Gun.DoesNotExist:
                return HttpResponseRedirect(reverse('gadmin:guns'))
        else:
            gun = Gun(type=0, price=0, cooldown=0, damage=0)
        return self.render_to_response({ 'gun': gun })

    def post(self, request, *args, **kwargs):
        pk = request.path.split('/')[-2]
        gun_list = Gun.objects.filter(pk=pk)
        if len(gun_list) == 0:
            gun = Gun(id=pk)
            action = 'Create'
        else:
            gun = gun_list[0]
            action = 'Edit'
        try:
            gun.name = request.POST.get('name')
            gun.type = request.POST.get('type')
            gun.description = request.POST.get('description')
            gun.price = request.POST.get('price')
            gun.damage = request.POST.get('damage')
            gun.cooldown = request.POST.get('cooldown')
            gun.save()
        except Exception as e:
            return self.render_to_response({ 'gun': gun, 'message': str(e) })
        
        AdminLog.objects.create(
            action=f'{action}ed gun #{gun.id}',
            by=User.objects.get(pk=request.session.get('admin_id'))
        )

        return HttpResponseRedirect(reverse('gadmin:guns'))


class SkinsView(generic.ListView):
    model = Skin
    template_name = 'gadmin/skins.html'


class SkinModelView(generic.TemplateView):
    template_name = 'gadmin/skin_form.html'

    def get(self, request, pk=None):
        if pk is not None:
            try:
                skin = Skin.objects.get(pk=pk)
            except Skin.DoesNotExist:
                return HttpResponseRedirect(reverse('gadmin:skins'))
        else:
            skin = Skin(price=0)
        return self.render_to_response({ 'skin': skin })

    def post(self, request, *args, **kwargs):
        pk = request.path.split('/')[-2]
        skin_list = Skin.objects.filter(pk=pk)
        if len(skin_list) == 0:
            skin = Skin(id=pk)
            action = 'Create'
        else:
            skin = skin_list[0]
            action = 'Edit'
        try:
            skin.name = request.POST.get('name')
            skin.description = request.POST.get('description')
            skin.price = request.POST.get('price')
            skin.save()
        except Exception as e:
            return self.render_to_response({ 'skin': skin, 'message': str(e) })

        AdminLog.objects.create(
            action=f'{action}ed skin #{skin.id}',
            by=User.objects.get(pk=request.session.get('admin_id'))
        )

        return HttpResponseRedirect(reverse('gadmin:skins'))


def admin_logs(request):
    return render(request, 'gadmin/admin_logs.html', { 'logs': AdminLog.objects.all() })


def logout(request):
    del request.session['admin_id']
    del request.session['admin_name']

    return HttpResponseRedirect(reverse('gadmin:login'))
