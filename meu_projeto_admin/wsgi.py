"""
WSGI config for meu_projeto_admin project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Adicione esta linha AQUI para configurar o locale
import meu_projeto_admin.locale_setup 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meu_projeto_admin.settings')

application = get_wsgi_application()