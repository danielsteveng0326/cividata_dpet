# municipio_ia/urls.py (URL principal)
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve
import os

# Vista de healthcheck para Railway
@csrf_exempt
def health_check(request):
    """
    Endpoint de healthcheck para Railway.
    Retorna 200 si la aplicación está funcionando.
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'cividata_dpet',
        'version': '1.0.0'
    }, status=200)

# Vista para servir archivos media en producción
def serve_media(request, path):
    """
    Sirve archivos media en producción.
    En desarrollo, Django lo hace automáticamente.
    """
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(open(file_path, 'rb'))
    else:
        raise Http404("Archivo no encontrado")

urlpatterns = [
    path('health/', health_check, name='health_check'),  # Healthcheck endpoint
    path('admin/', admin.site.urls),
    path('', include('peticiones.urls')),
]

# Servir archivos media
if settings.DEBUG:
    # En desarrollo, usar el método estándar de Django
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # En producción, usar vista personalizada
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve_media, name='media'),
    ]
