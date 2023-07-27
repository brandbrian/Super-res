# Superres/urls.py

from django.urls import path
from .views import ImageProcessingView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('https://brianbrand.pythonanywhere.com/Super-res/process_image/',
         ImageProcessingView.as_view(), name='process_image'),
]

# This is only needed when DEBUG is True (during development), PythonAnywhere will serve the media files in production.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
