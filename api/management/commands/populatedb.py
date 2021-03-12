import json
import sys
from os.path import join

from django.core.management.base import BaseCommand, CommandError

from api.models import GUser, Gun, Skin, BulletPattern
from api.utils import SCHOOL_EMAIL_ADDRESS
from gioele_v3.settings import DEBUG

GAME_DATA_FILENAME = 'game_data.json'

class Command(BaseCommand):
    help = 'Auto-generate default guns and skins'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            help='Set default user username',
            type=str
        )
        parser.add_argument(
            '--userpass',
            help='Set default user password',
            type=str
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Load guns and skins from json file',
        )

    def load_guns_into_db(self, guns):
        if guns is None:
            self.stderr.write('[ERROR] Invalid gun list')
            return

        for i, gun in enumerate(guns):
            if 'name' in gun \
                and 'pattern' in gun \
                and 'description' in gun \
                and 'type' in gun \
                and 'price' in gun \
                and 'cooldown' in gun \
                and 'damage' in gun \
                and 'shoot' in gun \
                and 'behavior' in gun:
                pattern = BulletPattern.objects.create(
                    name='%s pattern' % gun['name'],
                    function=gun['pattern'],
                    behavior=gun['behavior']
                )
                Gun.objects.create(
                    name=gun['name'],
                    description=gun['description'],
                    type=int(gun['type']),
                    cooldown=gun['cooldown'],
                    damage=gun['damage'],
                    price=gun['price'],
                    shoot=gun['shoot'],
                    pattern=pattern
                )
            else:
                self.stderr.write('[ERROR] A gun read from json has invalid properties (%d)' % i)
    
    def load_skins_into_db(self, skins):
        if skins is None:
            self.stderr.write('[ERROR] Invalid skin list')
            return

        for i, skin in enumerate(skins):
            if 'name' in skin \
                and 'description' in skin \
                and 'price' in skin \
                and 'filename' in skin:
                Skin.objects.create(
                    name=skin['name'],
                    description=skin['description'],
                    price=skin['price'],
                    filename=skin['filename']
                )
            else:
                self.stderr.write('[ERROR] A skin read from json has invalid properties (%d)' % i)
    
    def handle(self, *args, **options):
        if not DEBUG:
            self.stderr.write('[ERROR] Cannot run this command in production')
            return

        username = 'user_0'
        if options.get('username') is not None:
            username = options['username']
        userpass = 'test_password'
        if options.get('userpass') is not None:
            userpass = options['userpass']

        if options['json']:
            file_path = join(sys.path[0], GAME_DATA_FILENAME)
            with open(file_path) as f:
                data = json.load(f)
            guns = data.get('guns')
            skins = data.get('skins')
        else:
            guns = [
                {
                    'name': 'Main gun 1',
                    'type': 0,
                    'cooldown': 1200,
                    'damage': 100,
                    'description': 'Nessuna descrizione',
                    'price': 0,
                    'shoot': 'mainGunBullets.push(new Bullet(player.x+player.width/2,player.y,8,pattern_0));mainGunBullets[mainGunBullets.length-1].behavior();',
                    'pattern': 'this.y-=this.speedY;',
                    'behavior': None,
                },
                {
                    'name': 'Side gun 1',
                    'type': 1,
                    'cooldown': 1800,
                    'damage': 200,
                    'description': 'Nessuna descrizione',
                    'price': 0,
                    'shoot': 'let tempx=player.x+player.width/2;sideGunBullets.push(new Bullet(tempx,player.y,3,pattern,behavior));let tempvar=0;let tempint=setInterval(function(){if(tempvar>=5){clearInterval(tempint);}sideGunBullets.push(new Bullet(tempx,player.y,3,pattern,behavior));tempvar++;},50);',
                    'pattern': 'this.y-=this.speedY;this.x=this.constX+this.mult*Math.cos(this.arg*3.14/180);this.arg+=7;this.mult+=0.5;',
                    'behavior': 'this.constX=this.x;this.arg=90;this.mult=0;',
                },
            ]
            skins = [
                {
                    'name': 'Test skin 1',
                    'description': 'Nessuna descrizione',
                    'filename': 'skin_01.png',
                    'price': 0,
                },
            ]

        self.load_guns_into_db(guns)
        self.load_skins_into_db(skins)

        GUser.objects.create_user(
            username=username,
            email=(username + SCHOOL_EMAIL_ADDRESS),
            password=userpass,
            auth=True
        )

        self.stdout.write('Default guns and skins created sucessfully')
        self.stdout.write('Default user created:')
        self.stdout.write('username: %s' % username)
        self.stdout.write('password: %s' % ('*' * len(userpass)))
