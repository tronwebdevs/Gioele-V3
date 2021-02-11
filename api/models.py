import hashlib
from uuid import uuid4

from django.db import models
from django.contrib.auth.models import User

from .utils import generate_short_id
from .exceptions import ParseException, AlreadyExist, NotEnoughtCoins
from .classes import UserSkin, UserGun, Parser

pstr_parser = Parser()


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
    description = models.CharField(max_length=256, default='')
    cooldown = models.IntegerField()
    damage = models.IntegerField()
    max_level = models.IntegerField()

    def get_displayable_id(self):
        return hashlib.md5(str(self.id).encode()).hexdigest()

    def __str__(self):
        return self.name


class Skin(models.Model):
    id = models.CharField(primary_key=True, max_length=4, editable=False, default=generate_short_id)
    description = models.CharField(max_length=256, default='')
    name = models.CharField(max_length=128)
    price = models.FloatField()

    def get_displayable_id(self):
        return hashlib.md5(str(self.id).encode()).hexdigest()

    def __str__(self):
        return self.name


# USER RELATED MODELS
class UserInventory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    main_guns = models.CharField(max_length=256, null=True, default=None)
    side_guns = models.CharField(max_length=256, null=True, default=None)
    skins = models.CharField(max_length=256, null=True, default=None)

    """
    Get guns of supplied type from user inventory database table and joins results
    with the guns database table (to retrieve the guns' names).
    IMPORTANT: Guns' ID are hashed (md5) when sent to the frontend.
    """
    def _get_guns(self, g_type):
        field = self.main_guns if g_type == 'main' else self.side_guns
        result = []
        for gun in pstr_parser.to_dict_list(field, 'id', 'level'):
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

    def _add_gun(self, gun_id, g_type):
        field = self.main_guns if g_type == 'main' else self.side_guns
        guns = pstr_parser.to_dict_list(field, 'id', 'level')
        guns.append({
            'id': gun_id,
            'level': 1
        })
        if g_type == 'main':
            self.main_guns = pstr_parser.from_dict_list(guns)
        else:
            self.side_guns = pstr_parser.from_dict_list(guns)

    def get_main_guns(self):
        return self._get_guns('main')

    def get_main_guns_dict(self):
        return list(map(vars, self.get_main_guns()))

    def add_main_gun(self, gun_id):
        self._add_gun(gun_id, 'main')

    def get_side_guns(self):
        return self._get_guns('side')

    def get_side_guns_dict(self):
        return list(map(vars, self.get_side_guns()))

    def add_side_gun(self, gun_id):
        self._add_gun(gun_id, 'side')

    def get_skins(self):
        if self.skins is None:
            return list()
        skins_obj = []
        for skin in pstr_parser.to_str_list(self.skins):
            db_skin = Skin.objects.get(pk=skin)
            hashed_id = hashlib.md5(skin.encode()).hexdigest()
            skins_obj.append({
                'id': hashed_id,
                'name': db_skin.name,
            })
        return skins_obj

    def get_skins_dict(self):
        return self.get_skins()

    def add_skin(self, skin_id):
        skins = pstr_parser.to_str_list(self.skins)
        skins.append(skin_id)
        self.skins = pstr_parser.from_str_list(skins)

    def get_displayable_id(self):
        return hashlib.md5(str(self.id).encode()).hexdigest()

    def __str__(self):
        return str(self.id)


class GUserManager(models.Manager):
    def create_user(self, username, email, password, **extra_fields):
        user = User.objects.create_user(username=username, password=password, email=email)
        inventory = UserInventory.objects.create(main_guns=None, side_guns=None, skins=None)
        guser = GUser(user=user, inventory=inventory)
        guser.save()
        return guser


class GUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='user')
    auth = models.BooleanField(default=False, verbose_name='Email authentication completed')
    level = models.FloatField(default=0)
    balance = models.FloatField(default=0)
    skin = models.CharField(max_length=4, default='')
    inventory = models.OneToOneField(UserInventory, on_delete=models.CASCADE, related_name='inventory')

    objects = GUserManager()

    class Meta:
        verbose_name = 'Gioele User'

    def log_login(self, visit_id):
        visit_log = VisitLog.objects.get(pk=visit_id)
        LoginLog.objects.create(user=self, visit=visit_log)

    def _get_item_from_shop(self, Item, hashed_item_id):
        db_item = None
        for item in Item.objects.all():
            db_item_id = hashlib.md5(item.id.encode()).hexdigest()
            if db_item_id == hashed_item_id:
                db_item = item
                break
        if db_item is None:
            raise Item.DoesNotExist()

        rest = self.balance - db_item.price
        if rest < 0:
            raise NotEnoughtCoins()

        self.balance = rest
        self.save()

        return db_item

    def buy_gun(self, hashed_gun_id):
        all_guns = pstr_parser.to_dict_list(self.inventory.main_guns, 'id', 'name') 
        all_guns += pstr_parser.to_dict_list(self.inventory.side_guns, 'id', 'name')
        for gun in all_guns:
            if hashlib.md5(gun['id'].encode()).hexdigest() == hashed_gun_id:
                raise AlreadyExist()

        gun = self._get_item_from_shop(Gun, hashed_gun_id)

        if gun.type == 0:
            self.inventory.add_main_gun(gun.id)
        else:
            self.inventory.add_side_gun(gun.id)

        self.inventory.save()

    def buy_skin(self, hashed_skin_id):
        for s in pstr_parser.to_str_list(self.inventory.skins):
            if hashlib.md5(s.encode()).hexdigest() == hashed_skin_id:
                raise AlreadyExist()
        skin = self._get_item_from_shop(Skin, hashed_skin_id)
        self.inventory.add_skin(skin.id)
        self.inventory.save()
    
    # def get_visits(self):
    #     return Visitor.objects.filter(user_id=self.id)

    def __str__(self):
        return self.user.username


class VisitLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    ip = models.CharField(max_length=16)
    platform = models.CharField(max_length=128)
    lang = models.CharField(max_length=6)
    browser = models.CharField(max_length=256)
    screen_width = models.IntegerField(default=-1)
    screen_height = models.IntegerField(default=-1)
    referrer = models.CharField(max_length=512, null=True)
    has_touchscreen = models.BooleanField(default=False)
    has_ad_blocker = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField()

    def __str__(self):
        return str(self.id)


class LoginLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(GUser, on_delete=models.CASCADE)
    visit = models.ForeignKey(VisitLog, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class GameLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(GUser, on_delete=models.CASCADE)
    visit = models.ForeignKey(VisitLog, on_delete=models.CASCADE)
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()
    exp_gained = models.IntegerField()
    gbucks_earned = models.IntegerField()
    shooted_main = models.IntegerField()
    shooted_side = models.IntegerField()
    killed = models.CharField(max_length=128)
    powerups = models.CharField(max_length=128)
    skin = models.CharField(max_length=4)

    def __str__(self):
        return str(self.id)
