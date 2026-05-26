"""ASGI config for the local banking MVP."""
import os

from django.core.asgi import get_asgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bankapp.settings")

application = get_asgi_application()
