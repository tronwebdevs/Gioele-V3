import hashlib
from uuid import uuid4

from django.db import models
from django.contrib.auth.models import User

from .utils import generate_short_id
from .exceptions import ParseException
from .classes import UserSkin, UserGun


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
    main_guns = models.CharField(max_length=256, null=True, default=None)
    side_guns = models.CharField(max_length=256, null=True, default=None)
    skins = models.CharField(max_length=256, null=True, default=None)

    """
    Parser definition: all items owned by the player are sotred in the database in
    the format `item_1_id:level_item_1|item_2_id:level_item_2|...|item_N_id:level_item_N`.
    The string must be less than 256 characters long.
    """
    def parse_guns(self, field):
        result = []
        if field is None:
            return result
        arr = field.split('|')
        for item in arr:
            t = item.split(':')
            if len(t) != 2:
                raise ParseException()
            item_id = t[0]
            try:
                item_level = int(t[1])
            except ValueError:
                raise ParseException()
            result.append({
                'id': item_id,
                'level': item_level
            })
        return result

    """
    Get guns of supplied type from user inventory database table and joins results
    with the guns database table (to retrieve the guns' names).
    IMPORTANT: Guns' ID are hashed (md5) when sent to the frontend.
    """
    def _get_guns(self, g_type):
        if g_type == 'main':
            field = self.main_guns
        elif g_type == 'side':
            field = self.side_guns
        else:
            raise ParseException('Unspecified gun type in _get_guns()')
        result = []
        for gun in self.parse_guns(field):
            db_gun = Gun.objects.get(pk=gun['id'])
            hashed_id = hashlib.md5(gun['id'].encode()).hexdigest()
            result.append(
                UserGun(
                    id=hashed_id,
                    name=db_gun.name,
                    level=gun['level'],
                )
            )
        return result

    def get_main_guns(self):
        return self._get_guns('main')

    def get_main_guns_dict(self):
        return list(map(vars, self.get_main_guns()))

    def get_side_guns(self):
        return self._get_guns('side')

    def get_side_guns_dict(self):
        return list(map(vars, self.get_side_guns()))

    def get_skins(self):
        if self.skins is None:
            return list()
        skins_obj = []
        for skin in self.skins.split('|'):
            db_skin = Skin.objects.get(pk=skin)
            hashed_id = hashlib.md5(skin.encode()).hexdigest()
            skins_obj.append({
                'id': hashed_id,
                'name': db_skin.name,
            })
        return skins_obj

    def get_skins_dict(self):
        return self.get_skins()

    def get_displayable_id(self):
        return hashlib.md5(str(self.id).encode()).hexdigest()

    def __str__(self):
        return self.id.__str__()


class GUserManager(models.Manager):
    def create_user(self, username, email, password, **extra_fields):
        user = User.objects.create_user(username=username, password=password, email=email)
        inventory = UserInventory.objects.create(main_gun=None, side_gun=None, skins=None)
        guser = GUser(user=user, inventory=inventory)
        guser.save()
        return guser


class GUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='user')
    auth = models.BooleanField(default=False, verbose_name='Email authentication completed')
    level = models.FloatField(default=0)
    balance = models.FloatField(default=0)
    inventory = models.OneToOneField(UserInventory, on_delete=models.CASCADE, related_name='inventory')

    objects = GUserManager()

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
