# Gioele-V3

![Gioele V3 Game Screenshot](./screenshot.png)

Giovanni + Maurizio = Gioele V3

Enjoy.

### Installation

Required:

 - ![redis server](https://redis.io/)
 - python 3.9+
 - ![python virtual environment](https://docs.python.org/3/library/venv.html)

```
~$ python3 -m venv env
~$ source env/bin/activate
(env) ~$ pip install -r requirements.txt
(env) ~$ python manage.py migrate
(env) ~$ python manage,py populatedb
```

To run (make sure redis is running):

```
(env) ~$ python manage,py runserver
```

by TronWeb, for IIS TronZanella.
