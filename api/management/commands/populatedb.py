from django.core.management.base import BaseCommand, CommandError

from api.models import GUser, Gun, Skin, BulletPattern
from api.utils import SCHOOL_EMAIL_ADDRESS

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
    
    def handle(self, *args, **options):
        username = 'user_0'
        if 'username' in options:
            username = options['username']
        userpass = 'test_password'
        if 'userpass' in options:
            userpass = options['userpass']

        Skin.objects.create(
            name='Test skin 1',
            description='Nessuna descrizione',
            price=0
        )
        main_pattern = BulletPattern.objects.create(name='Main gun base pattern', function='this.y-=this.speedY;')
        side_pattern = BulletPattern.objects.create(
            name='Side gun base pattern',
            function='this.y-=this.speedY;this.x=this.constX+this.mult*Math.cos(this.arg*3.14/180);this.arg+=7;this.mult+=0.5;',
            behavior='this.constX=this.x;this.arg=90;this.mult=0;'
        )
        Gun.objects.create(
            name='Main gun 1',
            type=0,
            cooldown=1200,
            damage=100,
            description='Nessuna descrizione',
            price=0,
            shoot='mainGunBullets.push(new Bullet(player.x+player.width/2,player.y,8,pattern_0));mainGunBullets[mainGunBullets.length-1].behavior();',
            pattern=main_pattern
        )
        Gun.objects.create(
            name='Side gun 1',
            type=1,
            cooldown=1800,
            damage=200,
            description='Nessuna descrizione',
            price=1000,
            shoot='let tempx=player.x+player.width/2;sideGunBullets.push(new Bullet(tempx,player.y,3,pattern,behavior));let tempvar=0;let tempint=setInterval(function(){if(tempvar>=5){clearInterval(tempint);}sideGunBullets.push(new Bullet(tempx,player.y,3,pattern,behavior));tempvar++;},50);',
            pattern=side_pattern
        )

        GUser.objects.create_user(username=username, email=(username + SCHOOL_EMAIL_ADDRESS), password=userpass)

        self.stdout.write('Default guns and skins created sucessfully')
        self.stdout.write('Default user created:')
        self.stdout.write('username: %s' % username)
        self.stdout.write('password: %s' % ('*' * len(userpass)))
