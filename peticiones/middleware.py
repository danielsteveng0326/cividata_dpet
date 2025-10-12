# peticiones/middleware.py
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve


class AdminAccessMiddleware:
    """
    Middleware que restringe el acceso al admin de Django
    solo al superuser con cédula 1020458606
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Verificar si la ruta es del admin
        if request.path.startswith('/admin/'):
            # Si el usuario está autenticado
            if request.user.is_authenticated:
                # Verificar si es el superuser autorizado
                if not (request.user.cedula == '1020458606' and request.user.is_superuser):
                    messages.error(request, 'No tienes permisos para acceder al panel de administración de Django')
                    return redirect('index')
            # Si no está autenticado, Django redirigirá al login del admin
        
        response = self.get_response(request)
        return response
