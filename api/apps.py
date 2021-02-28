from django.apps import AppConfig
from django.db.utils import OperationalError
from .utils import log


def log_fatal(*lines):
    log('root', '--------------------------------------------------', 'ERROR')
    log('root', '', 'ERROR')
    for line in lines:
        log('root', '   %s' % line, 'ERROR')
    log('root', '', 'ERROR')
    log('root', '--------------------------------------------------', 'ERROR')


class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        from .models import Gun, Skin

        try:
            if Gun.objects.count() == 0:
                log_fatal(
                    'No default gun set, please set one or run',
                    'populate_db.sh to auto generate one.'
                )
            else:
                log('root', 'Default gun found', 'SUCCESS')
            
            if Skin.objects.count() == 0:
                log_fatal(
                    'No default skin set, please set one or run',
                    'populate_db.sh to auto generate one.'
                )
            else:
                log('root', 'Default skin found', 'SUCCESS')
        except OperationalError:
            log_fatal(
                'Database is empty, please run:',
                'python manage.py migrate'
            )
