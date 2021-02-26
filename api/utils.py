import datetime
import inspect
import random
import re
import string
import threading

from django.utils import timezone
from jose import jwt

BADWORDS = (
    #sezione generale
    'merd', 'cazz', 'negr', 'stupr', 'bastard',
    'bocchinar', 'culo', 'coglion', 'puttana',
    'troia', 'mignotta', 'fottut', 'handicap',
    'mongolo', 'suicid', 'sborr', 'scopa', 'stronz',
    'zoccol', 'succhia', 'mannaggia', 'tette',
    #sezione sessualità
    'ricchione', 'froci', 'culatton', 'culaton',
    'finocchi', 'lesbic', 'gay',
    #sezione Chiesa Cattolica
    'madonna', 'diopo', 'dioladr', 'diostra', 'diobastard', 
    'dioca', 'diof', 'dioim', 'diom', 'dios', 'padrepio',
    #sezione QVANDO C'ERA LVI
    'fascis', 'nazi', 'mussolini', 'hitler', 'benito',
    'adolf', 'partigian', 'lager', 'gulag', 'stalin',
    'lenin', 'ebrei', 'auschwitz',
    #sezione Politica (senza leader politici)
    'comunis', 'liberalis', 'anarchi',
    #sezione internazionale
    'faggot', 'nigger', 'retard', 'fuck', 'shit',
    'kurwa', # polski
    'bitch', 'hooker', 'whore',
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

def log(who, message, ltype='INFO'):
    func = inspect.stack()[1].function
    tname = THREADS.get(threading.get_ident())
    if tname is None:
        if len(THREADS) == 0:
            tname = 'Thread-0'
            THREADS[threading.get_ident()] = tname
        else:
            tname = 'Thread-' + str(int(THREADS[list(THREADS.keys())[-1]].split('-')[-1]) + 1)
            THREADS[threading.get_ident()] = tname
    color = '\033[92m'
    if ltype == 'WARNING':
        color = '\033[93m'
    print('%s[%s/%s][%s][%s] %s' % (color, tname, func, ltype, who, message))
