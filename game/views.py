from django.shortcuts import render
from django.views import generic

class GameView(generic.TemplateView):
    template_name = 'game/index.html'
