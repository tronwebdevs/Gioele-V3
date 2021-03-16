import hashlib
import base64
from uuid import uuid4, UUID

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from .utils import generate_short_id, parser
from .exceptions import ParseException, AlreadyExist, NotEnoughtCoins
from .classes import Displayable


# GAME RELATED MODELS
class BulletPattern(models.Model, Displayable):
    id = models.CharField(primary_key=True, max_length=4, editable=False, default=generate_short_id)
    name = models.CharField(max_length=128)
    function = models.CharField(max_length=1024)
    behavior = models.CharField(max_length=1024, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()


class Gun(models.Model, Displayable):
    _MAIN_GUN = 0
    _SIDE_GUN = 1
    _GUN_TYPES = [
        (_MAIN_GUN, 'main'),
        (_SIDE_GUN, 'side'),
    ]

    id = models.CharField(primary_key=True, max_length=4, editable=False, default=generate_short_id)
    type = models.SmallIntegerField(
        choices=_GUN_TYPES,
    )
    price = models.FloatField()
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=256)
    cooldown = models.IntegerField()
    damage = models.IntegerField()
    shoot = models.CharField(max_length=1024)
    pattern = models.ForeignKey(BulletPattern, on_delete=models.PROTECT, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def to_safe_dict(self, exclude=('type'), hash_funcs=False):
        data = super().to_safe_dict(exclude)
        if hash_funcs:
            hashes = self.get_hashes()
            data['shoot'] = hashes['shoot']
            data['pattern']['function'] = hashes['pattern']
            data['pattern']['behavior'] = hashes['behavior']
        else:
            data['shoot'] = base64.b64encode(self.shoot.encode('ascii')).decode()
            data['pattern']['function'] = base64.b64encode(self.pattern.function.encode('ascii')).decode()
            if self.pattern.behavior is not None:
                data['pattern']['behavior'] = base64.b64encode(self.pattern.behavior.encode('ascii')).decode()
        return data

    def get_hashes(self):
        shoot = hashlib.md5(self.shoot.encode()).hexdigest()
        pattern = hashlib.md5(self.pattern.function.encode()).hexdigest()
        behavior = None
        if self.pattern.behavior is not None:
            behavior = hashlib.md5(self.pattern.behavior.encode()).hexdigest()
        return {
            'shoot': shoot,
            'pattern': pattern,
            'behavior': behavior,
        }


class Skin(models.Model, Displayable):
    id = models.CharField(primary_key=True, max_length=4, editable=False, default=generate_short_id)
    description = models.CharField(max_length=256)
    name = models.CharField(max_length=128)
    price = models.FloatField()
    filename = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def to_safe_dict(self, exclude=()):
        return super().to_safe_dict(exclude)


class Ability(models.Model, Displayable):
    id = models.CharField(primary_key=True, max_length=4, editable=False, default=generate_short_id)
    description = models.CharField(max_length=256)
    name = models.CharField(max_length=128)
    price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def to_safe_dict(self):
        return super().to_safe_dict(('price', 'description'))


# USER RELATED MODELS
class UserInventory(models.Model, Displayable):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    main_guns = models.CharField(max_length=256, null=True, default=None)
    side_guns = models.CharField(max_length=256, null=True, default=None)
    skins = models.CharField(max_length=256, null=True, default=None)
    abilities = models.CharField(max_length=256, null=True, default=None)

    objects = models.Manager()

    """
    Get guns of supplied type from user inventory database table and joins results
    with the guns database table (to retrieve the guns' names).
    """
    def _get_guns(self, g_type):
        field = self.main_guns if g_type == 'main' else self.side_guns
        result = []
        for gun in parser.string_to_dicts(field, 'id', 'level'):
            db_gun = Gun.objects.get(pk=gun['id'])
            result.append({
                'id': db_gun.id,
                'name': db_gun.name,
                'level': gun['level'],
            })
        return result

    def _get_listed_items(self, Item, field):
        if field is None:
            return list()
        obj_list = []
        for item in parser.string_to_list(field):
            db_item = Item.objects.get(pk=item)
            obj_list.append({
                'id': db_item.id,
                'name': db_item.name,
            })
        return obj_list

    def _add_gun(self, gun_id, g_type):
        field = self.main_guns if g_type == 'main' else self.side_guns
        guns = parser.string_to_dicts(field, 'id', 'level')
        guns.append({
            'id': gun_id,
            'level': 1
        })
        if g_type == 'main':
            self.main_guns = parser.dicts_to_string(guns)
        else:
            self.side_guns = parser.dicts_to_string(guns)

    def get_main_guns(self):
        return self._get_guns('main')

    def add_main_gun(self, gun_id):
        self._add_gun(gun_id, 'main')

    def get_side_guns(self):
        return self._get_guns('side')

    def add_side_gun(self, gun_id):
        self._add_gun(gun_id, 'side')

    def get_skins(self):
        return self._get_listed_items(Skin, self.skins)

    def add_skin(self, skin_id):
        skins = parser.string_to_list(self.skins)
        skins.append(skin_id)
        self.skins = parser.list_to_string(skins)

    def get_abilities(self):
        return self._get_listed_items(Ability, self.abilities)

    def to_dict(self, safe=False):
        return {
            'id': str(self.id),
            'main_guns': self.get_main_guns(),
            'side_guns': self.get_side_guns(),
            'skins': self.get_skins(),
            'abilities': self.get_abilities(),
        }


class GUserManager(models.Manager):
    def create_user(self, username, email, password, **extra_fields):
        db_skins = Skin.objects.all()
        db_guns = Gun.objects.filter(type=Gun._MAIN_GUN)
        # This two checks should never fail as the first thing to do in production should be
        # creating a default skin and gun for every user. This should be achieved by creating
        # them directly in the database or by django shell
        if len(db_skins) < 1:
            raise Exception('You need to create a default skin (admin)')
        if len(db_guns) < 1:
            raise Exception('You need to create a default main gun (admin)')

        # Create user (auth)
        user = User.objects.create_user(username=username, password=password, email=email)
        # Create empty user inventory
        inventory = UserInventory.objects.create(
            main_guns=parser.dict_to_string({ db_guns[0].id: 1 }),
            side_guns=None,
            skins=parser.list_to_string([ db_skins[0].id ])
        )
        guser = GUser(user=user, inventory=inventory, **extra_fields)
        # Use the first skin (default) as user's first skin
        guser.skin = db_skins.first()
        # Get the first gun (main) as user's first gun
        guser.main_gun = db_guns.first()
        # Store user on database
        guser.save()
        return guser


class GUser(models.Model, Displayable):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='user')
    auth = models.BooleanField(default=False, verbose_name='Email authentication completed')
    level = models.FloatField(default=0)
    balance = models.FloatField(default=0)
    skin = models.ForeignKey(Skin, on_delete=models.PROTECT, related_name='+')
    main_gun = models.ForeignKey(Gun, on_delete=models.PROTECT, related_name='+')
    side_gun = models.ForeignKey(Gun, on_delete=models.PROTECT, null=True, default=None, related_name='+')
    inventory = models.OneToOneField(UserInventory, on_delete=models.CASCADE, related_name='inventory')

    objects = GUserManager()

    class Meta:
        verbose_name = 'Gioele User'

    @property
    def id(self):
        return self.user.id

    @property
    def username(self):
        return self.user.username

    @property
    def email(self):
        return self.user.email

    @property
    def is_active(self):
        return self.user.is_active

    def log_login(self, visit_id):
        visit_log = VisitLog.objects.get(pk=UUID(visit_id))
        LoginLog.objects.create(user=self, visit=visit_log)

    def _get_item_from_shop(self, Item, item_id):
        db_item = Item.objects.get(pk=item_id)
        rest = self.balance - db_item.price
        if rest < 0:
            raise NotEnoughtCoins()

        self.balance = rest
        self.save()

        # Save transaction log
        PurchaseLog.objects.create(by=self, price=db_item.price, item=db_item.id)

        return db_item

    def buy_gun(self, gun_id):
        all_guns = parser.string_to_dicts(self.inventory.main_guns, 'id', 'name') 
        all_guns += parser.string_to_dicts(self.inventory.side_guns, 'id', 'name')

        dupes = [i for i in range(len(all_guns)) if all_guns[i]['id'] == gun_id]
        if len(dupes) > 0:
            raise AlreadyExist()

        gun = self._get_item_from_shop(Gun, gun_id)

        if gun.type == 0:
            self.inventory.add_main_gun(gun.id)
        else:
            self.inventory.add_side_gun(gun.id)

        self.inventory.save()

        return gun

    def buy_skin(self, skin_id):
        all_skins = parser.string_to_list(self.inventory.skins)
        
        dupes = [i for i in range(len(all_skins)) if all_skins[i] == skin_id]
        if len(dupes) > 0:
            raise AlreadyExist()

        skin = self._get_item_from_shop(Skin, skin_id)

        self.inventory.add_skin(skin.id)
        self.inventory.save()

        return skin
    
    def get_visits(self):
        return VisitLog.objects.filter(user_id=self.id)

    def _fix_dict_conv(self, data):
        data['id'] = self.user.id
        data['username'] = self.user.username
        data['email'] = self.user.email
        data['main_gun'] = self.main_gun.id
        data['side_gun'] = None
        if self.side_gun is not None:
            data['side_gun'] = self.side_gun.id
        data['skin'] = self.skin.id
        data.pop('user', None)
        return data

    def to_dict(self, safe=False):
        data = super().to_dict(safe)
        return self._fix_dict_conv(data)

    def to_safe_dict(self):
        data = super().to_safe_dict(('user', 'inventory'))
        return self._fix_dict_conv(data)

    def to_simple_dict(self):
        data = self.to_dict(True)
        return self._fix_dict_conv(data)


class BannedUserManager(models.Manager):
    def ban(self, user_id, reason, by, **extra_fields):
        user = GUser.objects.get(pk=user_id)
        user.user.is_active = False
        user.user.save()
        return BannedUser.objects.create(user=user, reason=reason, by=by) 


class BannedUser(models.Model):
    user = models.OneToOneField(GUser, on_delete=models.CASCADE)
    reason = models.CharField(max_length=256)
    by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='by', null=True)
    datetime = models.DateTimeField(auto_now_add=True)

    objects = BannedUserManager()


class VisitLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(GUser, on_delete=models.SET_NULL, null=True, default=None)
    ip = models.CharField(max_length=16)
    platform = models.CharField(max_length=128)
    lang = models.CharField(max_length=6)
    browser = models.CharField(max_length=256)
    screen_width = models.IntegerField()
    screen_height = models.IntegerField()
    referrer = models.CharField(max_length=512, null=True)
    has_touchscreen = models.BooleanField(default=False)
    has_ad_blocker = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()


class LoginLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(GUser, on_delete=models.CASCADE)
    visit = models.ForeignKey(VisitLog, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()


class GameLogManager(models.Manager):
    def register_log(self, giorgio, shooted_main, shooted_side):
        game_log = GameLog(id=giorgio.game_id)
        game_log.user = giorgio.user
        game_log.time_start = giorgio.start_time
        game_log.time_end = timezone.now()
        game_log.exp_gained = giorgio.player.exp
        game_log.gbucks_earned = giorgio.player.gbucks
        game_log.shooted_main = shooted_main
        game_log.main_hit = giorgio.player.main_hit
        game_log.shooted_side = shooted_side
        game_log.side_hit = giorgio.player.side_hit
        game_log.main_gun = giorgio.player.main_gun
        game_log.side_gun = giorgio.player.side_gun
        game_log.visit = VisitLog.objects.get(pk=giorgio.visit_id)
        game_log.killed = parser.dict_to_string(giorgio.player.killed)
        game_log.powerups = parser.dict_to_string(giorgio.player.expired_powerups)
        game_log.abilities = parser.dict_to_string(giorgio.player.used_abilities)
        game_log.skin = giorgio.user.skin
        game_log.save()
        return game_log


class GameLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    user = models.ForeignKey(GUser, on_delete=models.CASCADE)
    visit = models.ForeignKey(VisitLog, on_delete=models.CASCADE)
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()
    exp_gained = models.IntegerField()
    gbucks_earned = models.IntegerField()
    shooted_main = models.IntegerField()
    main_hit = models.IntegerField()
    shooted_side = models.IntegerField()
    side_hit = models.IntegerField()
    killed = models.CharField(max_length=256)
    powerups = models.CharField(max_length=256)
    abilities = models.CharField(max_length=256)
    skin = models.ForeignKey(Skin, on_delete=models.PROTECT, related_name='+')
    main_gun = models.ForeignKey(Gun, on_delete=models.PROTECT, related_name='+')
    side_gun = models.ForeignKey(Gun, on_delete=models.PROTECT, null=True, default=None, related_name='+')

    objects = GameLogManager()


class PurchaseLog(models.Model):
    by = models.ForeignKey(GUser, on_delete=models.CASCADE)
    item = models.CharField(max_length=4)
    price = models.FloatField()
    datetime = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()


class Stat(models.Model):
    key = models.CharField(max_length=16)
    value = models.FloatField()
    at = models.DateTimeField(auto_now_add=True, editable=False)

    objects = models.Manager()


class AdminLog(models.Model):
    action = models.CharField(max_length=256)
    by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    datetime = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
