import sys
import asyncio

import aioredis
from asgiref.sync import async_to_sync
from django.apps import AppConfig
from django.db.utils import OperationalError
from gioele_v3.settings import CHANNEL_LAYERS
from .utils import log


redis_settings = CHANNEL_LAYERS['default']['CONFIG']['hosts'][0]

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
        if sys.argv[1] != 'runserver':
            return

        redis = async_to_sync(aioredis.create_redis_pool)('redis://%s:%i' % (redis_settings[0], redis_settings[1]))
        # async_to_sync(redis.delete)('asgi:group:*')
        # TODO: fix this to only delete `asgi:group:*` keys
        async_to_sync(redis.flushdb)()
        log('root', 'Flushed database', 'SUCCESS')
        
        from .models import Gun, Skin

        try:
            if Gun.objects.count() == 0:
                log_fatal(
                    'No default gun set, please set one or run',
                    './tools/populate_db.sh to auto generate one.'
                )
            else:
                log('root', 'Default gun found', 'SUCCESS')
            
            if Skin.objects.count() == 0:
                log_fatal(
                    'No default skin set, please set one or run',
                    './tools/populate_db.sh to auto generate one.'
                )
            else:
                log('root', 'Default skin found', 'SUCCESS')
        except OperationalError:
            log_fatal(
                'Database is empty, please run:',
                './tools/populate_db.sh'
            )
