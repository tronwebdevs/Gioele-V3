import platform
import subprocess

import psutil
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from django.contrib.auth import authenticate
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm

from api.utils import generate_short_id
from api.models import GUser, BannedUser, Gun, Skin, GameLog, VisitLog, Stat, PurchaseLog


def index(request):
    context = {
        'stats': {
            'visitors': VisitLog.objects.count(),
            'users': GUser.objects.count(),
            'matches': GameLog.objects.count(),
            'purchases': PurchaseLog.objects.count()
        },
        'charts_data': {
            'users': Stat.objects.filter(key='users'),
            'visitors': Stat.objects.filter(key='visitors'),
            'games': Stat.objects.filter(key='games'),
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
        'users': GUser.objects.filter(user__is_active=True),
        'banned': BannedUser.objects.all(),
    }
    return render(request, 'gadmin/users.html', context)


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
            'cpu': Stat.objects.filter(key='cpu'),
            'mem': Stat.objects.filter(key='mem'),
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


def new_gun(request):
    gun = Gun(type=0, price=0, name='', description='', cooldown=0, damage=0)
    return render(request, 'gadmin/gun_form.html', {'gun': gun })


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
        else:
            gun = gun_list[0]
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
        else:
            skin = skin_list[0]
        try:
            skin.name = request.POST.get('name')
            skin.description = request.POST.get('description')
            skin.price = request.POST.get('price')
            skin.save()
        except Exception as e:
            return self.render_to_response({ 'skin': skin, 'message': str(e) })

        return HttpResponseRedirect(reverse('gadmin:skins'))


def logout(request):
    del request.session['admin_id']
    del request.session['admin_name']

    return HttpResponseRedirect(reverse('gadmin:login'))
