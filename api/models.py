from django.db import models
from django.contrib.auth.models import User


class Visitor(models.Model):
    ip = models.CharField(max_length=16)
    platform = models.CharField(max_length=128)
    lang = models.CharField(max_length=6)
    browser = models.CharField(max_length=256)
    screen_width = models.IntegerField(default=-1)
    screen_height = models.IntegerField(default=-1)
    referrer = models.CharField(max_length=512, null=True)
    has_touchscreen = models.BooleanField(default=False)
    has_ad_blocker = models.BooleanField(default=False)
    user_id = models.IntegerField(default=-1)
    visit_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id


class GUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='user')
    auth = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    balance = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Gioele User'
    
    def get_visits(self):
        return Visitor.objects.filter(user_id=self.id)

    def __str__(self):
        return self.user.username


class Game(models.Model):
    user = models.ForeignKey(GUser, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    score = models.IntegerField()
    shooted_primary = models.IntegerField()
    shooted_secondary = models.IntegerField()
    killed = models.IntegerField()
    powerups = models.CharField(max_length=128)