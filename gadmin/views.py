import platform
import subprocess

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from django.contrib.auth import authenticate
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm

from api.models import GUser, Gun, Skin, GameLog, VisitLog


def index(request):
    visitors_count = VisitLog.objects.count()
    users_count = GUser.objects.count()
    matches_count = GameLog.objects.count()
    context = {
        'stats': {
            'visitors': visitors_count,
            'users': users_count,
            'matches': matches_count,
        }
    }
    return render(request, 'gadmin/index.html', context)


class LoginView(generic.TemplateView):
    template_name = 'gadmin/login.html'

    def post(self, request):
        user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
        if user is not None and user.is_staff:
            request.session['admin_id'] = user.id
            request.session['admin_name'] = user.username
            return HttpResponseRedirect(reverse('gadmin:index'))
        context = { 'message': 'Dati non validi' }
        return self.render_to_response(context)


class UsersView(generic.ListView):
    model = GUser
    template_name = 'gadmin/users.html'


def hardware(request):
    commit_hash = subprocess.check_output(
        ['git', 'log', '-1', '--pretty=%H']).strip().decode()
    commit_message = subprocess.check_output(
        ['git', 'log', '-1', '--pretty=%B']).strip().decode()
    commit_author = subprocess.check_output(
        ['git', 'log', '-1', '--pretty=%an']).strip().decode()
    context = {
        'system': platform,
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


class SkinsView(generic.ListView):
    model = Skin
    template_name = 'gadmin/skins.html'


def logout(request):
    del request.session['admin_id']
    del request.session['admin_name']

    return HttpResponseRedirect(reverse('gadmin:login'))