import re

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

def is_valid_word(word):
    for regex in BADWORDS:
        if re.search(regex, word):
            return False
    return True
