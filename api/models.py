import hashlib
from uuid import uuid4

from django.db import models
from django.contrib.auth.models import User

from .utils import generate_short_id, parser
from .exceptions import ParseException, AlreadyExist, NotEnoughtCoins
from .classes import UserSkin, UserGun


# GAME RELATED MODELS
class BulletPattern(models.Model):
    id = models.CharField(primary_key=True, max_length=4, editable=False, default=generate_short_id)
    name = models.CharField(max_length=128)
    function = models.CharField(max_length=1024)
    behavior = models.CharField(max_length=1024, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def to_safe_dict(self):
        return {
            'id': self.id,
            'function': self.function,
            'behavior': self.behavior,
        }
    
    def to_dict(self):
        return {
            **self.to_safe_dict(),
            'name': self.name,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
        }


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
    description = models.CharField(max_length=256)
    cooldown = models.IntegerField()
    damage = models.IntegerField()
    shoot = models.CharField(max_length=1024)
    pattern = models.ForeignKey(BulletPattern, on_delete=models.SET_NULL, null=True)

    def get_displayable_id(self):
        return hashlib.md5(str(self.id).encode()).hexdigest()

    def to_safe_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cooldown': self.cooldown,
            'damage': self.damage,
            'shoot': self.shoot,
            'pattern': None if self.pattern is None else self.pattern.to_safe_dict(),
        }

    def to_dict(self):
        obj = {
            **self.to_safe_dict(),
            'type': self.type,
            'price': self.price,
            'description': self.description,
        }
        if self.pattern is not None:
            obj['pattern'] = self.pattern.to_dict()
        return obj

    def __str__(self):
        return self.name


class Skin(models.Model):
    id = models.CharField(primary_key=True, max_length=4, editable=False, default=generate_short_id)
    description = models.CharField(max_length=256)
    name = models.CharField(max_length=128)
    price = models.FloatField()

    def get_displayable_id(self):
        return hashlib.md5(str(self.id).encode()).hexdigest()

    def to_safe_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    def to_dict(self):
        return {
            **self.to_safe_dict(),
            'price': self.price,
            'description': self.description,
        }

    def __str__(self):
        return self.name


class Ability(models.Model):
    id = models.CharField(primary_key=True, max_length=4, editable=False, default=generate_short_id)
    description = models.CharField(max_length=256)
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
    abilities = models.CharField(max_length=256, null=True, default=None)

    """
    Get guns of supplied type from user inventory database table and joins results
    with the guns database table (to retrieve the guns' names).
    IMPORTANT: Guns' ID are hashed (md5) when sent to the frontend.
    """
    def _get_guns(self, g_type, hash_id=True):
        field = self.main_guns if g_type == 'main' else self.side_guns
        result = []
        for gun in parser.string_to_dicts(field, 'id', 'level'):
            db_gun = Gun.objects.get(pk=gun['id'])
            gun_id = gun['id']
            if hash_id:
                gun_id = hashlib.md5(gun['id'].encode()).hexdigest()
            result.append(
                UserGun(
                    id=gun_id,
                    name=db_gun.name,
                    level=gun['level'],
                )
            )
        return result

    def _get_listed_items(self, Item, field, hash_id=True):
        if field is None:
            return list()
        obj_list = []
        for item in parser.string_to_list(field):
            db_item = Item.objects.get(pk=item)
            skin_id = item
            if hash_id:
                skin_id = hashlib.md5(item.encode()).hexdigest()
            obj_list.append({
                'id': skin_id,
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

    def get_main_guns(self, hash_id=True):
        return self._get_guns('main', hash_id)

    def get_main_guns_dict(self, hash_id=True):
        return list(map(vars, self.get_main_guns(hash_id)))

    def add_main_gun(self, gun_id):
        self._add_gun(gun_id, 'main')

    def get_side_guns(self, hash_id=True):
        return self._get_guns('side', hash_id)

    def get_side_guns_dict(self, hash_id=True):
        return list(map(vars, self.get_side_guns(hash_id)))

    def add_side_gun(self, gun_id):
        self._add_gun(gun_id, 'side')

    def get_skins(self, hash_id=True):
        return self._get_listed_items(Skin, self.skins, hash_id)

    def get_skins_dict(self, hash_id=True):
        return self.get_skins(hash_id)

    def add_skin(self, skin_id):
        skins = parser.string_to_list(self.skins)
        skins.append(skin_id)
        self.skins = parser.list_to_string(skins)

    def get_abilities(self):
        return self._get_listed_items(Ability, self.abilities)

    def get_abilities_dict(self):
        return self.get_abilities()

    def get_displayable_id(self):
        return hashlib.md5(str(self.id).encode()).hexdigest()

    def __str__(self):
        return str(self.id)


class GUserManager(models.Manager):
    def create_user(self, username, email, password, **extra_fields):
        db_skins = Skin.objects.all()
        db_guns = Gun.objects.filter(type=Gun.MAIN_GUN)
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
        guser = GUser(user=user, inventory=inventory)
        # Use the first skin (default) as user's first skin
        guser.skin = db_skins[0].id
        # Get the first gun (main) as user's first gun
        guser.main_gun = db_guns[0].id
        # Store user on database
        guser.save()
        return guser


class GUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='user')
    auth = models.BooleanField(default=False, verbose_name='Email authentication completed')
    level = models.FloatField(default=0)
    balance = models.FloatField(default=0)
    skin = models.CharField(max_length=4)
    main_gun = models.CharField(max_length=4)
    side_gun = models.CharField(max_length=4, null=True, default=None)
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

        # Save transaction log
        PurchaseLog.objects.create(by=self, price=db_item.price, item=db_item.id)

        return db_item

    def buy_gun(self, hashed_gun_id):
        all_guns = parser.string_to_dicts(self.inventory.main_guns, 'id', 'name') 
        all_guns += parser.string_to_dicts(self.inventory.side_guns, 'id', 'name')
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
        for s in parser.string_to_list(self.inventory.skins):
            if hashlib.md5(s.encode()).hexdigest() == hashed_skin_id:
                raise AlreadyExist()
        skin = self._get_item_from_shop(Skin, hashed_skin_id)
        self.inventory.add_skin(skin.id)
        self.inventory.save()
    
    # def get_visits(self):
    #     return Visitor.objects.filter(user_id=self.id)

    def __str__(self):
        return self.user.username


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

    def __str__(self):
        return self.user.user.username + ': ' + self.reason


class VisitLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
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
    updated_at = models.DateTimeField(auto_now_add=True)

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
    shooted_main_hit = models.IntegerField()
    shooted_side = models.IntegerField()
    shooted_side_hit = models.IntegerField()
    killed = models.CharField(max_length=256)
    powerups = models.CharField(max_length=256)
    abilities = models.CharField(max_length=256)
    skin = models.CharField(max_length=4)
    main_gun = models.CharField(max_length=4)
    side_gun = models.CharField(max_length=4, null=True, default=None)

    def __str__(self):
        return str(self.id)


class PurchaseLog(models.Model):
    by = models.OneToOneField(GUser, on_delete=models.CASCADE)
    item = models.CharField(max_length=4)
    price = models.FloatField()
    datetime = models.DateTimeField(auto_now_add=True)


class Stat(models.Model):
    key = models.CharField(max_length=16)
    value = models.FloatField()
    at = models.DateTimeField(auto_now_add=True, editable=False)


class AdminLog(models.Model):
    action = models.CharField(max_length=256)
    by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    datetime = models.DateTimeField(auto_now_add=True)
