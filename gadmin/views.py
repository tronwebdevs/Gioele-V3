import platform
import subprocess
import hashlib

import psutil
from django.shortcuts import render
from django.views import generic
from django.contrib.auth import authenticate
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm

from gadmin.utils import valid_string, valid_number, raise_if_not_valid, get_percentage
from api.utils import generate_short_id
from api.models import User, GUser, BannedUser, Gun, Skin, GameLog, \
                        VisitLog, Stat, PurchaseLog, AdminLog, BulletPattern


def get_user(user_id):
    try:
        return GUser.objects.get(pk=user_id)
    except GUser.DoesNotExist:
        return None

def get_selected_items(dataset, user_dataset):
    dataset = list(map(lambda i: i.to_dict(), dataset))
    for mi in dataset:
        mi['owned'] = False
        for ui in user_dataset:
            if mi['id'] == ui['id']:
                mi['owned'] = True
                break
    return dataset

def get_messages(request, key):
    err_key = key + '_error'
    error = request.session.get(err_key)
    if error is not None:
        del request.session[err_key]
    mess_key = key + '_message'
    message = request.session.get(mess_key)
    if message is not None:
        del request.session[mess_key]
    return { 'error': error, 'message': message }
    


def index(request):
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
            }
    }
    if Stat.objects.filter(key='users').count() > 0:
        users_dataset = list(Stat.objects.filter(key='users'))[:16]
        visitors_dataset = list(Stat.objects.filter(key='visitors'))[:16]
        games_dataset = list(Stat.objects.filter(key='games'))[:16]
        context['percentages'] = {
            'users': get_percentage(users, users_dataset[-1].value),
            'visitors': get_percentage(visitors, visitors_dataset[-1].value),
            'matches': get_percentage(matches, games_dataset[-1].value),
        }
        context['charts_data'] = {
            'users': users_dataset + [Stat(key='users',value=users)],
            'visitors': visitors_dataset + [Stat(key='visitors',value=visitors)],
            'games': games_dataset + [Stat(key='games',value=matches)],
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
            return redirect('gadmin:index')
        else:
            return self.render_to_response({ 'message': 'Dati non validi' })


def users(request):
    return render(request, 'gadmin/users.html', {
        'users': GUser.objects.filter(user__is_active=True),
        'banned': BannedUser.objects.all(),
        **get_messages(request, 'users')
    })


class UserBanView(generic.View):
    def get(self, request, pk):
        user = get_user(pk)
        if user is None:
            return redirect('gadmin:users')
        return render(request, 'gadmin/ban_user.html', {
            'user': user,
            **get_messages(request, 'banuser')
        })

    def post(self, request, pk):
        user = get_user(pk)
        try:
            if user is None:
                return redirect('gadmin:users')
            
            username = request.POST.get('username')
            reason = raise_if_not_valid(request.POST.get('reason'), valid_string, 'Reason')
            if user.user.username != username:
                raise Exception('Username validation failed')

            admin = User.objects.get(pk=request.session.get('admin_id'))
            user_id = user.user.id
            BannedUser.objects.ban(
                user_id=user_id,
                reason=reason,
                by=admin
            )
            AdminLog.objects.create(action=f'Banned user #{user_id}', by=admin)
        except Exception as e:
            request.session['banuser_error'] = str(e)
            return redirect('gadmin:user', pk=pk)
        
        request.session['users_message'] = 'Operation completed successfully'
        return redirect('gadmin:users')


class UserInventoryView(generic.View):
    def get(self, request, pk=None):
        return redirect('gadmin:user', pk=pk)

    def post(self, request, pk=None):
        user = get_user(pk)
        if user is None:
            request.session['users_error'] = 'User not found'
            return redirect('gadmin:users')
        
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
        request.session['user_message'] = 'Operation completed successfully'
        return redirect('gadmin:user', pk=pk)


class UserModelView(generic.TemplateView):
    template_name = 'gadmin/user_form.html'

    def get(self, request, pk=None):
        if pk is not None:
            user = get_user(pk)
            if user is None:
                request.session['users_error'] = 'User not found'
                return redirect('gadmin:users')
        else:
            user = GUser(type=0, price=0, cooldown=0, damage=0)
        
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

        return self.render_to_response({
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
            **get_messages(request, 'user'),
        })

    def post(self, request, pk=None):
        user_list = GUser.objects.filter(pk=pk)
        extra = ['message', 'User updated successfully']
        if len(user_list) == 0:
            user = GUser(id=pk)
        else:
            user = user_list[0]
        try:
            user.user.username = raise_if_not_valid(request.POST.get('username'), valid_string, 'Username')
            user.user.email = raise_if_not_valid(request.POST.get('email'), valid_string, 'Email')
            user.user.save()
            user.auth = request.POST.get('auth') == 'on'
            items = ('main_gun', 'side_gun', 'skin')
            for item in items:
                val = request.POST.get(item)
                if not valid_string(val):
                    val = None
                setattr(user, item, val)
            user.balance = float(request.POST.get('balance'))
            user.save()
        except Exception as e:
            extra[0] = 'error'
            extra[1] = str(e)

        request.session[f'user_{extra[0]}'] = extra[1]

        AdminLog.objects.create(
            action=f'Edited user #{user.user.id} profile',
            by=User.objects.get(pk=request.session.get('admin_id'))
        )

        return redirect('gadmin:user', pk=pk)


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
        'git': {
            'commit': commit_hash,
            'message': commit_message,
            'author': commit_author,
        },
    }
    if Stat.objects.filter(key='cpu').count() > 0:
        context['charts_data'] = {
            'cpu': list(Stat.objects.filter(key='cpu'))[:10],
            'mem': list(Stat.objects.filter(key='mem'))[:10],
        }
    return render(request, 'gadmin/hardware.html', context)


class StatsView(generic.TemplateView):
    template_name = 'gadmin/stats.html'


class GBucksView(generic.TemplateView):
    template_name = 'gadmin/gbucks.html'


class GunsView(generic.TemplateView):
    template_name = 'gadmin/guns.html'

    def get(self, request):
        return self.render_to_response({
            'guns': Gun.objects.all(),
            'patterns': BulletPattern.objects.all(),
            **get_messages(request, 'guns'),
        })


class GunModelView(generic.TemplateView):
    template_name = 'gadmin/gun_form.html'

    def get(self, request, pk=None):
        if pk is not None:
            try:
                gun = Gun.objects.get(pk=pk)
            except Gun.DoesNotExist as e:
                request.session['gun_error'] = str(e)
        else:
            gun = Gun(type=0, price=0, cooldown=0, damage=0)
        
        patterns = list(map(lambda bp: bp.to_dict(), BulletPattern.objects.all()))
        return self.render_to_response({
            'gun': gun.to_dict(),
            'patterns': patterns,
            **get_messages(request, 'gun'),
        })

    def post(self, request, pk=None, *args, **kwargs):
        gun_list = Gun.objects.filter(pk=pk)

        form_type = request.POST.get('form_type')
        if form_type != 'bullets' and form_type != 'info':
            return redirect('gadmin:guns')

        if len(gun_list) == 0:
            gun = Gun(id=pk)
            action = 'Create'
        else:
            gun = gun_list[0]
            action = 'Edit'
        
        try:
            if form_type == 'info':
                gun.name = raise_if_not_valid(request.POST.get('name'), valid_string, 'Name')
                gun_type = int(request.POST.get('type'))
                if gun_type != 0 and gun_type != 1:
                    raise Exception('Type: Invalid value')
                gun.type = gun_type
                gun.description = raise_if_not_valid(request.POST.get('description'), valid_string, 'Description')
                gun.price = float(request.POST.get('price'))
                gun.damage = int(request.POST.get('damage'))
                gun.cooldown = int(request.POST.get('cooldown'))
            else:
                conf_pass = request.POST.get('conf_pass')
                auth_user = authenticate(
                    username=request.session.get('admin_name'),
                    password=conf_pass
                )
                if auth_user is None or auth_user.id != request.session.get('admin_id'):
                    raise Exception('Authentication failed')
                else:
                    gun.shoot = raise_if_not_valid(request.POST.get('shoot'), valid_string, 'Shoot')
                    gun.pattern = BulletPattern.objects.get(pk=request.POST.get('pattern'))
            gun.save()
            AdminLog.objects.create(
                action=f'{action}ed gun #{gun.id}',
                by=User.objects.get(pk=request.session.get('admin_id'))
            )
            request.session['gun_message'] = 'Operation completed successfully'
        except Exception as e:
            request.session['gun_error'] = str(e)

        return redirect('gadmin:gun', pk=pk)


class PatternModelView(generic.TemplateView):
    template_name = 'gadmin/pattern_form.html'

    def get(self, request, pk=None):
        if pk is not None:
            try:
                pattern = BulletPattern.objects.get(pk=pk)
            except BulletPattern.DoesNotExist as e:
                perror = request.session.get('pattern_error')
                if perror is None:
                    perror = str(e)
                else:
                    del request.session['pattern_error']

                request.session['guns_error'] = perror
                return redirect('gadmin:guns')
        else:
            pattern = BulletPattern(name='', function='', behavior=None)
        
        return self.render_to_response({
            'pattern': pattern.to_dict(),
            **get_messages(request, 'pattern'),
        })

    def post(self, request, pk=None, *args, **kwargs):
        pattern_list = BulletPattern.objects.filter(pk=pk)

        if len(pattern_list) == 0:
            pattern = BulletPattern(id=pk)
            action = 'Create'
        else:
            pattern = pattern_list[0]
            action = 'Edit'
        
        try:
            conf_pass = request.POST.get('conf_pass')
            auth_user = authenticate(
                username=request.session.get('admin_name'),
                password=conf_pass
            )
            if auth_user is None or auth_user.id != request.session.get('admin_id'):
                raise Exception('Authentication failed')

            pattern.name = raise_if_not_valid(request.POST.get('name'), valid_string, 'Name')
            pattern.function = raise_if_not_valid(request.POST.get('function'), valid_string, 'Function')
            pattern.behavior = raise_if_not_valid(request.POST.get('behavior'), valid_string, 'Function')
            pattern.updated_at = timezone.now()
            pattern.save()
            AdminLog.objects.create(
                action=f'{action}ed pattern #{pattern.id}',
                by=User.objects.get(pk=request.session.get('admin_id'))
            )
            request.session['pattern_message'] = 'Operation completed successfully'
        except Exception as e:
            request.session['pattern_error'] = str(e)

        return redirect('gadmin:pattern', pk=pk)


class SkinsView(generic.TemplateView):
    template_name = 'gadmin/skins.html'

    def get(self, request):
        return self.render_to_response({
            'skins': Skin.objects.all(),
            **get_messages(request, 'skins'),
        })


class SkinModelView(generic.TemplateView):
    template_name = 'gadmin/skin_form.html'

    def get(self, request, pk=None):
        if pk is not None:
            try:
                skin = Skin.objects.get(pk=pk)
            except Skin.DoesNotExist as e:
                skin_error = request.session.get('skin_error')
                if skin_error is None:
                    skin_error = str(e)
                else:
                    del request.session['skin_error']

                request.session['skins_error'] = skin_error
                return redirect('gadmin:skins')
        else:
            skin = Skin(price=0)
        
        return self.render_to_response({
            'skin': skin,
            **get_messages(request, 'skin'),
        })

    def post(self, request, pk=None, *args, **kwargs):
        skin_list = Skin.objects.filter(pk=pk)
        if len(skin_list) == 0:
            skin = Skin(id=pk)
            action = 'Create'
        else:
            skin = skin_list[0]
            action = 'Edit'
        try:
            skin.name = raise_if_not_valid(request.POST.get('name'), valid_string, 'Name')
            skin.description = raise_if_not_valid(request.POST.get('description'), valid_string, 'Description')
            skin.price = float(request.POST.get('price'))
            skin.save()
            AdminLog.objects.create(
                action=f'{action}ed skin #{skin.id}',
                by=User.objects.get(pk=request.session.get('admin_id'))
            )
            request.session['skin_message'] = 'Operation completed successfully'
        except Exception as e:
            request.session['skin_error'] = str(e)

        return redirect('gadmin:skin', pk=pk)


def admin_logs(request):
    return render(request, 'gadmin/admin_logs.html', { 'logs': AdminLog.objects.all() })


def logout(request):
    del request.session['admin_id']
    del request.session['admin_name']

    return redirect('gadmin:login')
