import psutil
from django.core.management.base import BaseCommand, CommandError

from api.models import Stat, VisitLog, GameLog, GUser, PurchaseLog

class Command(BaseCommand):
    help = 'Update stats'
    
    def handle(self, *args, **options):
        Stat.objects.create(key='cpu', value=psutil.cpu_percent())
        Stat.objects.create(key='mem', value=psutil.virtual_memory().percent)
        Stat.objects.create(key='visitors', value=VisitLog.objects.count())
        Stat.objects.create(key='users', value=GUser.objects.count())
        Stat.objects.create(key='games', value=GameLog.objects.count())
        Stat.objects.create(key='purchases', value=PurchaseLog.objects.count())

        self.stdout.write('Updated stats sucessfully')