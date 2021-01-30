from uuid import uuid4

from django.db import models
from django.contrib.auth.models import User

from .utils import generate_short_id

# USER RELATED MODELS
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


class UserInventory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    main_gun = models.CharField(max_length=256, null=True, default=None)
    side_gun = models.CharField(max_length=256, null=True, default=None)
    skins = models.CharField(max_length=256, null=True, default=None)

    def __str__(self):
        return self.id.__str__()


class GUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='user')
    auth = models.BooleanField(default=False, verbose_name='Email authentication completed')
    level = models.FloatField(default=0)
    balance = models.FloatField(default=0)
    inventory = models.OneToOneField(UserInventory, on_delete=models.CASCADE, related_name='inventory')

    class Meta:
        verbose_name = 'Gioele User'
    
    def get_visits(self):
        return Visitor.objects.filter(user_id=self.id)

    def __str__(self):
        return self.user.username


class Match(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(GUser, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    score = models.IntegerField()
    shooted_primary = models.IntegerField()
    shooted_secondary = models.IntegerField()
    killed = models.IntegerField()
    powerups = models.CharField(max_length=128)

    def __str__(self):
        return self.id.__str__()


# GAME RELATED MODELS
class Gun(models.Model):
    MAIN_GUN = 0
    SIDE_GUN = 1
    GUN_TYPES = [
        (MAIN_GUN, 'main'),
        (SIDE_GUN, 'side'),
    ]

    id = models.CharField(primary_key=True, max_length=4, editable=False, default=generate_short_id)
    type = models.SmallIntegerField(
        choices=GUN_TYPES,
    )
    price = models.FloatField()
    name = models.CharField(max_length=128)
    cooldown = models.IntegerField()
    damage = models.IntegerField()
    max_level = models.IntegerField()

    def __str__(self):
        return self.name


class Skin(models.Model):
    id = models.CharField(primary_key=True, max_length=4, editable=False, default=generate_short_id)
    name = models.CharField(max_length=128)
    price = models.FloatField()

    def __str__(self):
        return self.name
