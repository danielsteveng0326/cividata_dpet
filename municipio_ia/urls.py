# municipio_ia/urls.py (URL principal)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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

urlpatterns = [
    path('health/', health_check, name='health_check'),  # Healthcheck endpoint
    path('admin/', admin.site.urls),
    path('', include('peticiones.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
