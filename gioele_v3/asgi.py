"""
ASGI config for gioele_v3 project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter

import api.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gioele_v3.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddleware(
        URLRouter(
            api.routing.websocket_urlpatterns,
        )
    )
})
