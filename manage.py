from django.core.wsgi import get_wsgi_application
import os
import sys

path = '/home/brianbrand/Superres'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'Superres.settings'

application = get_wsgi_application()
