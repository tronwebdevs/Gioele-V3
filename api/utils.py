import datetime
import inspect
import random
import re
import string
import threading
import asyncio

import aioredis
from asgiref.sync import async_to_sync
from django.utils import timezone
from gioele_v3.settings import DEBUG, CHANNEL_LAYERS
from jose import jwt

from api.classes import Parser

BADWORDS = (
    #sezione generale
    'merd', 'cazz', 'negr', 'stupr', 'bastard',
    'bocchinar', 'culo', 'coglion', 'puttana',
    'troia', 'mignotta', 'fottut', 'handicap',
    'mongolo', 'suicid', 'sborr', 'scopa', 'stronz',
    'zoccol', 'succhia', 'mannaggia', 'tette',
    #sezione sessualità
    'ricchione', 'froci', 'culatton', 'culaton',
    'finocchi', 'lesbic', 'gay', 'lgbt',
    #sezione Chiesa Cattolica
    'madonna', 'diopo', 'dioladr', 'diostra', 'diobastard', 
    'dioca', 'diof', 'dioim', 'diom', 'dios', 'padrepio',
    #sezione QVANDO C'ERA LVI
    'fascis', 'nazi', 'mussolini', 'hitler', 'benito',
    'adolf', 'partigian', 'lager', 'gulag', 'stalin',
    'lenin', 'ebrei', 'auschwitz',
    #sezione Politica (senza leader politici)
    'comunis', 'liberalis', 'anarchi', 'draghi', 'renzi',
    'salvini', 'zingaretti',
    #sezione internazionale
    'faggot', 'nigger', 'retard', 'fuck', 'shit',
    'kurwa', # polski
    'bitch', 'hooker', 'whore', 'cunt', 'cum',
    #sottosezione NAPOLI
    'mammt', 'bucchin', 'uagliò', 'uaglio', 'kitte',
    #sezione malattie
    'aids', 'hiv', 'coronavirus', 'covid', 'wuhan',
    #sezione personalizzata
    'mvja27',
)
SCHOOL_EMAIL_ADDRESS = '@tronzanella.edu.it'
THREADS = {}

# 
# REMEMBER TO EDIT THIS SETTINGS
#
JWT_SETTINGS = {
    'secret': 'PLACEHOLDER_TEXT_HERE',
    'algorithm': 'HS256',
    'issuer': 'com.example.API',
    'audience': 'com.example.Fronted',
}

parser = Parser()

# Hippity hoppity, your code is now MY property
# credits: https://stackoverflow.com/a/287944
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def is_valid_word(word):
    for regex in BADWORDS:
        if re.search(regex, word):
            return False
    return True

def forge_auth_token(userid, username):
    now_datetime = timezone.now()
    issued_at = round(now_datetime.timestamp() * 1000)
    expiration = round((now_datetime + datetime.timedelta(minutes=5)).timestamp() * 1000)
    return jwt.encode(
        {
            'iss': JWT_SETTINGS['issuer'],
            'aud': JWT_SETTINGS['audience'],
            'iat': int(issued_at),
            'exp': int(expiration),
            'id': userid,
            'username': username,
        },
        JWT_SETTINGS['secret'],
        algorithm=JWT_SETTINGS['algorithm']
    )

def generate_short_id(verify_set=None):
    gen_set = string.ascii_uppercase + string.ascii_lowercase + string.ascii_letters
    generated = ''.join(random.choice(gen_set) for _ in range(4))
    if verify_set is not None:
        res = verify_set.filter(pk=generated)
        if not res.empty():
            return generate_short_id(verify_set)
    return generated

def redis_broadcast(user_id, data):
    if not DEBUG:
        return

    channel = 'general'

    redis_settings = CHANNEL_LAYERS['default']['CONFIG']['hosts'][0]
    channel_name = 'giorgio:games:%s' % channel
    pub = async_to_sync(aioredis.create_redis)('redis://%s:%i' % (redis_settings[0], redis_settings[1]))
    res = async_to_sync(pub.publish_json)(channel_name, data)
    pub.close()
    return res

def log(who, message, ltype='INFO', force_color=None, broadcast_id=None):
    # Only print logs if DEBUG is set to true
    if not DEBUG:
        return
    
    func = inspect.stack()[1].function
    tname = THREADS.get(threading.get_ident())
    if tname is None:
        if len(THREADS) == 0:
            tname = 'Thread-0'
            THREADS[threading.get_ident()] = tname
        else:
            tname = 'Thread-' + str(int(THREADS[list(THREADS.keys())[-1]].split('-')[-1]) + 1)
            THREADS[threading.get_ident()] = tname
    color = bcolors.OKBLUE
    if who == 'Giorgio':
        color = bcolors.OKGREEN
    
    if ltype == 'WARNING':
        color = bcolors.WARNING
    elif ltype == 'ERROR':
        color = bcolors.FAIL
    elif ltype == 'SUCCESS':
        color = bcolors.OKGREEN
    
    if force_color is not None:
        color = force_color

    msg = '%s[%s/%s][%s][%s] %s%s' % (color, tname, func, ltype, who, message, bcolors.ENDC)

    if broadcast_id is not None:
        redis_broadcast(broadcast_id, { 't':0, 'm': msg })

    print(msg)
