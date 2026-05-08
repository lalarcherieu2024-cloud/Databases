"""
WSGI config for costuras_paqui project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "costuras_paqui.settings")

application = get_wsgi_application()

