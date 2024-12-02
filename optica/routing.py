from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/turnos/$', consumers.TurnoConsumer.as_asgi()),
]
