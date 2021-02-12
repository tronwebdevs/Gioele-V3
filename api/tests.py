import sys
import hashlib

from django.test import TestCase

from .exceptions import NotEnoughtCoins, AlreadyExist
from .models import GUser, Gun, Skin
from .classes import Parser

pstr_parser = Parser()

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
            price=10,
            name='test main gun',
            cooldown=1200,
            damage=10,
            max_level=10
        )
    )
    guns.append(
        Gun.objects.create(
            type=1,
            price=10,
            name='test side gun',
            cooldown=1200,
            damage=10,
            max_level=10
        )
    )
    skins = list()
    skins.append(
        Skin.objects.create(
            name='test skin 1',
            price=10
        )
    )
    return guns, skins

class GUserModelTest(TestCase):
    def test_create_user(self):
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
        user = create_test_user()
        guns, skins = create_test_guns_and_skins()

        hid1 = hashlib.md5(guns[0].id.encode()).hexdigest()
        user.buy_gun(hid1)
        hid2 = hashlib.md5(guns[1].id.encode()).hexdigest()
        user.buy_gun(hid2)

        user_main_guns = pstr_parser.string_to_dicts(user.inventory.main_guns, 'id', 'name')
        user_side_guns = pstr_parser.string_to_dicts(user.inventory.side_guns, 'id', 'name')
        self.assertEqual(user_main_guns[0]['id'], Gun.objects.filter(type=Gun.MAIN_GUN)[0].id)
        self.assertEqual(user_side_guns[0]['id'], Gun.objects.filter(type=Gun.SIDE_GUN)[0].id)

    def test_user_buys_skin(self):
        user = create_test_user()
        guns, skins = create_test_guns_and_skins()

        hid = hashlib.md5(skins[0].id.encode()).hexdigest()
        user.buy_skin(hid)
        user_skins = pstr_parser.string_to_list(user.inventory.skins)
        self.assertEqual(len(user_skins), 1)

    def test_user_buys_gun_already_exists(self):
        user = create_test_user()
        guns, skins = create_test_guns_and_skins()

        hid = hashlib.md5(guns[0].id.encode()).hexdigest()
        user.buy_gun(hid)

        self.assertRaises(AlreadyExist, user.buy_gun, hid)

    def test_user_buys_skin_already_exists(self):
        user = create_test_user()
        guns, skins = create_test_guns_and_skins()

        hid = hashlib.md5(skins[0].id.encode()).hexdigest()
        user.buy_skin(hid)

        self.assertRaises(AlreadyExist, user.buy_skin, hid)
