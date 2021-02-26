import sys
import hashlib

from django.test import TestCase

from .exceptions import NotEnoughtCoins, AlreadyExist
from .models import GUser, Gun, Skin
from .utils import parser

def create_test_user():
    user = GUser.objects.create_user(username='test', password='test', email='test@test.com')
    user.balance = sys.maxsize
    user.save()
    return user

def create_test_guns_and_skins():
    guns = list()
    guns.append(
        Gun.objects.create(
            type=0,
            price=0,
            name='default main gun',
            cooldown=1200,
            damage=10
        )
    )
    guns.append(
        Gun.objects.create(
            type=0,
            price=10,
            name='test main gun 1',
            cooldown=1200,
            damage=10
        )
    )
    guns.append(
        Gun.objects.create(
            type=1,
            price=10,
            name='test side gun 1',
            cooldown=1800,
            damage=20
        )
    )
    skins = list()
    skins.append(
        Skin.objects.create(
            name='default skin',
            price=0
        )
    )
    skins.append(
        Skin.objects.create(
            name='test skin 1',
            price=10
        )
    )
    return guns, skins

class GUserModelTest(TestCase):
    def test_create_user(self):
        create_test_guns_and_skins()
        created = create_test_user()
        self.assertEqual(created.user.username, 'test')
        self.assertEqual(created.user.email, 'test@test.com')

    def test_create_guns_and_skins(self):
        guns, skins = create_test_guns_and_skins()
        db_guns = Gun.objects.all()
        db_skins = Skin.objects.all()

        self.assertEqual(list(db_guns), guns)
        self.assertEqual(list(db_skins), skins)

    def test_user_buys_gun(self):
        guns, skins = create_test_guns_and_skins()
        user = create_test_user()

        hid1 = hashlib.md5(guns[1].id.encode()).hexdigest()
        user.buy_gun(hid1)
        hid2 = hashlib.md5(guns[2].id.encode()).hexdigest()
        user.buy_gun(hid2)

        user_main_guns = parser.string_to_dicts(user.inventory.main_guns, 'id', 'name')
        user_side_guns = parser.string_to_dicts(user.inventory.side_guns, 'id', 'name')
        self.assertEqual(user_main_guns[1]['id'], Gun.objects.filter(type=Gun.MAIN_GUN)[1].id)
        self.assertEqual(user_side_guns[0]['id'], Gun.objects.filter(type=Gun.SIDE_GUN)[0].id)

    def test_user_buys_skin(self):
        guns, skins = create_test_guns_and_skins()
        user = create_test_user()

        hid = hashlib.md5(skins[1].id.encode()).hexdigest()
        user.buy_skin(hid)
        user_skins = parser.string_to_list(user.inventory.skins)
        self.assertEqual(len(user_skins), 2)

    def test_user_buys_gun_already_exists(self):
        guns, skins = create_test_guns_and_skins()
        user = create_test_user()

        hid = hashlib.md5(guns[1].id.encode()).hexdigest()
        user.buy_gun(hid)

        self.assertRaises(AlreadyExist, user.buy_gun, hid)

    def test_user_buys_skin_already_exists(self):
        guns, skins = create_test_guns_and_skins()
        user = create_test_user()

        hid = hashlib.md5(skins[1].id.encode()).hexdigest()
        user.buy_skin(hid)

        self.assertRaises(AlreadyExist, user.buy_skin, hid)
