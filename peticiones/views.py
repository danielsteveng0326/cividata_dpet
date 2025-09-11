# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from .models import Peticion, ProcesamientoIA
from .forms import PeticionForm
from .services.gemini_service import GeminiTranscriptionService
import threading


def index(request):
    """Vista principal con estadísticas"""
    total_peticiones = Peticion.objects.count()
    sin_responder = Peticion.objects.filter(estado='sin_responder').count()
    respondidas = Peticion.objects.filter(estado='respondido').count()
    
    peticiones_recientes = Peticion.objects.order_by('-fecha_radicacion')[:5]
    
    context = {
        'total_peticiones': total_peticiones,
        'sin_responder': sin_responder,
        'respondidas': respondidas,
        'peticiones_recientes': peticiones_recientes,
    }
    return render(request, 'peticiones/index.html', context)


def crear_peticion(request):
    """Vista para crear nueva petición"""
    if request.method == 'POST':
        form = PeticionForm(request.POST, request.FILES)
        if form.is_valid():
            peticion = form.save()
            
            # Procesar PDF con IA en segundo plano
            def procesar_en_background():
                gemini_service = GeminiTranscriptionService()
                gemini_service.procesar_peticion_completa(peticion)
            
            # Ejecutar procesamiento en hilo separado
            thread = threading.Thread(target=procesar_en_background)
            thread.daemon = True
            thread.start()
            
            messages.success(
                request, 
                f'Petición creada exitosamente con radicado: {peticion.radicado}. '
                f'El documento está siendo procesado por IA.'
            )
            return redirect('detalle_peticion', radicado=peticion.radicado)
    else:
        form = PeticionForm()
    
    return render(request, 'peticiones/crear_peticion.html', {'form': form})


class ListaPeticiones(ListView):
    """Vista para listar todas las peticiones"""
    model = Peticion
    template_name = 'peticiones/lista_peticiones.html'
    context_object_name = 'peticiones'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Peticion.objects.all()
        
        # Filtros de búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(radicado__icontains=search) |
                Q(peticionario_nombre__icontains=search) |
                Q(peticionario_id__icontains=search)
            )
        
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        fuente = self.request.GET.get('fuente')
        if fuente:
            queryset = queryset.filter(fuente=fuente)
        
        return queryset.order_by('-fecha_radicacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['estado_filtro'] = self.request.GET.get('estado', '')
        context['fuente_filtro'] = self.request.GET.get('fuente', '')
        return context


def detalle_peticion(request, radicado):
    """Vista detalle de una petición específica"""
    peticion = get_object_or_404(Peticion, radicado=radicado)
    
    # Obtener información del procesamiento IA si existe
    try:
        procesamiento_ia = peticion.procesamiento_ia
    except ProcesamientoIA.DoesNotExist:
        procesamiento_ia = None
    
    context = {
        'peticion': peticion,
        'procesamiento_ia': procesamiento_ia,
    }
    return render(request, 'peticiones/detalle_peticion.html', context)


@csrf_exempt
def reprocesar_peticion(request, radicado):
    """Vista AJAX para reprocesar una petición con IA"""
    if request.method == 'POST':
        peticion = get_object_or_404(Peticion, radicado=radicado)
        
        def reprocesar_en_background():
            gemini_service = GeminiTranscriptionService()
            gemini_service.reanalizar_peticion(peticion)
        
        # Ejecutar reprocesamiento en hilo separado
        thread = threading.Thread(target=reprocesar_en_background)
        thread.daemon = True
        thread.start()
        
        return JsonResponse({
            'success': True,
            'message': 'Reprocesamiento iniciado correctamente'
        })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


def cambiar_estado_peticion(request, radicado):
    """Vista para cambiar el estado de una petición"""
    if request.method == 'POST':
        peticion = get_object_or_404(Peticion, radicado=radicado)
        nuevo_estado = request.POST.get('nuevo_estado')
        
        if nuevo_estado in ['sin_responder', 'respondido']:
            peticion.estado = nuevo_estado
            peticion.save()
            
            messages.success(
                request, 
                f'Estado de la petición {radicado} actualizado a: {peticion.get_estado_display()}'
            )
        else:
            messages.error(request, 'Estado inválido')
    
    return redirect('detalle_peticion', radicado=radicado)


def editar_peticionario(request, radicado):
    """Vista para editar los datos del peticionario"""
    peticion = get_object_or_404(Peticion, radicado=radicado)
    
    if request.method == 'POST':
        form = EditarPeticionarioForm(request.POST, instance=peticion)
        if form.is_valid():
            form.save()
            messages.success(
                request, 
                f'Datos del peticionario actualizados correctamente para {radicado}'
            )
            
            # Si es una petición AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Datos actualizados correctamente',
                    'peticionario_nombre': peticion.peticionario_nombre or '',
                    'peticionario_id': peticion.peticionario_id or '',
                    'peticionario_telefono': peticion.peticionario_telefono or '',
                    'peticionario_correo': peticion.peticionario_correo or '',
                    'peticionario_direccion': peticion.peticionario_direccion or ''
                })
            
            return redirect('lista_peticiones')
        else:
            # Si hay errores en formulario AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
            
            messages.error(request, 'Error al actualizar los datos')
    else:
        form = EditarPeticionarioForm(instance=peticion)
    
    # Para peticiones normales (no AJAX)
    context = {
        'form': form,
        'peticion': peticion
    }
    return render(request, 'peticiones/editar_peticionario.html', context)


@csrf_exempt
def obtener_datos_peticionario(request, radicado):
    """Vista AJAX para obtener los datos actuales del peticionario"""
    if request.method == 'GET':
        peticion = get_object_or_404(Peticion, radicado=radicado)
        
        return JsonResponse({
            'success': True,
            'peticionario_nombre': peticion.peticionario_nombre or '',
            'peticionario_id': peticion.peticionario_id or '',
            'peticionario_telefono': peticion.peticionario_telefono or '',
            'peticionario_correo': peticion.peticionario_correo or '',
            'peticionario_direccion': peticion.peticionario_direccion or ''
        })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})