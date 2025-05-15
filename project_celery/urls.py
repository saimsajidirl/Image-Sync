from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from app_app_celery.views import upload_image

urlpatterns = [
    path('', upload_image, name='upload-image'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
