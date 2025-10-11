# views.py - ARCHIVO COMPLETO ACTUALIZADO
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
from .services.asistente_respuesta_service import AsistenteRespuestaService
import threading
import json
import logging

logger = logging.getLogger(__name__)


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
    """Vista para cambiar el estado de una petición con archivos adjuntos"""
    if request.method == 'POST':
        from .forms import MarcarRespondidoForm
        from django.utils import timezone
        
        peticion = get_object_or_404(Peticion, radicado=radicado)
        nuevo_estado = request.POST.get('nuevo_estado')
        
        if nuevo_estado == 'respondido':
            # Usar formulario para validar archivos
            form = MarcarRespondidoForm(request.POST, request.FILES, instance=peticion)
            
            if form.is_valid():
                peticion = form.save(commit=False)
                peticion.estado = 'respondido'
                peticion.fecha_respuesta = timezone.now()
                peticion.save()
                
                messages.success(
                    request, 
                    f'Petición {radicado} marcada como respondida con archivos adjuntos correctamente.'
                )
            else:
                # Mostrar errores del formulario
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{form.fields[field].label}: {error}')
                return redirect('detalle_peticion', radicado=radicado)
        elif nuevo_estado == 'sin_responder':
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


# ========================================
# NUEVAS VISTAS PARA ASISTENTE IA
# ========================================

@csrf_exempt
def iniciar_asistente_respuesta(request, radicado):
    """
    Inicia el proceso de asistente inteligente para generar respuesta
    """
    if request.method == 'POST':
        try:
            peticion = get_object_or_404(Peticion, radicado=radicado)
            
            # Verificar que la petición tenga transcripción
            if not peticion.transcripcion_completa:
                return JsonResponse({
                    'success': False,
                    'error': 'La petición debe estar procesada por IA primero'
                })
            
            # Iniciar análisis con IA
            asistente_service = AsistenteRespuestaService()
            analisis = asistente_service.analizar_peticion_y_generar_preguntas(peticion)
            
            # Guardar análisis en sesión
            request.session[f'analisis_{radicado}'] = analisis
            
            return JsonResponse({
                'success': True,
                'analisis': analisis
            })
            
        except Exception as e:
            logger.error(f"Error en asistente para {radicado}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


def mostrar_asistente_respuesta(request, radicado):
    """
    Muestra la interfaz del asistente con las preguntas generadas
    """
    peticion = get_object_or_404(Peticion, radicado=radicado)
    
    # Obtener análisis de la sesión
    analisis = request.session.get(f'analisis_{radicado}')
    
    if not analisis:
        messages.error(request, 'Debe iniciar el análisis primero')
        return redirect('detalle_peticion', radicado=radicado)
    
    context = {
        'peticion': peticion,
        'analisis': analisis
    }
    
    return render(request, 'peticiones/asistente_respuesta.html', context)


@csrf_exempt
def procesar_respuestas_asistente(request, radicado):
    """
    Procesa las respuestas del usuario y genera la respuesta sugerida
    """
    if request.method == 'POST':
        try:
            peticion = get_object_or_404(Peticion, radicado=radicado)
            
            # Obtener respuestas del formulario
            data = json.loads(request.body)
            respuestas_usuario = data.get('respuestas', [])
            
            if not respuestas_usuario:
                return JsonResponse({
                    'success': False,
                    'error': 'No se proporcionaron respuestas'
                })
            
            # Generar respuesta con IA
            asistente_service = AsistenteRespuestaService()
            resultado = asistente_service.generar_respuesta_sugerida(peticion, respuestas_usuario)
            
            # Evaluar calidad de la respuesta
            evaluacion = asistente_service.evaluar_calidad_respuesta(resultado['respuesta_sugerida'])
            
            return JsonResponse({
                'success': True,
                'respuesta_sugerida': resultado['respuesta_sugerida'],
                'evaluacion': evaluacion,
                'fecha_generacion': resultado['fecha_generacion']
            })
            
        except Exception as e:
            logger.error(f"Error procesando respuestas para {radicado}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


def historial_asistente(request, radicado):
    """
    Muestra el historial de respuestas generadas por el asistente
    """
    peticion = get_object_or_404(Peticion, radicado=radicado)
    
    # Aquí podrías implementar un modelo para guardar el historial
    # Por ahora, mostraremos la última respuesta de la sesión
    
    context = {
        'peticion': peticion
    }
    
    return render(request, 'peticiones/historial_asistente.html', context)


@csrf_exempt
def descargar_respuesta_word(request, radicado):
    """
    Descarga la respuesta generada en formato Word (.docx) con plantilla
    """
    if request.method == 'POST':
        try:
            from docx import Document
            from docx.shared import Pt, Inches
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            from django.http import HttpResponse
            from datetime import datetime
            import io
            
            peticion = get_object_or_404(Peticion, radicado=radicado)
            
            # Obtener el contenido de la respuesta del POST
            data = json.loads(request.body)
            contenido_respuesta = data.get('contenido_respuesta', '')
            
            if not contenido_respuesta:
                return JsonResponse({
                    'success': False,
                    'error': 'No se proporcionó contenido para la respuesta'
                })
            
            # Crear documento Word
            doc = Document()
            
            # Configurar márgenes
            sections = doc.sections
            for section in sections:
                section.top_margin = Inches(1)
                section.bottom_margin = Inches(1)
                section.left_margin = Inches(1)
                section.right_margin = Inches(1)
            
            # Encabezado del documento
            header = doc.add_paragraph()
            header.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = header.add_run('RESPUESTA AL DERECHO DE PETICIÓN')
            run.bold = True
            run.font.size = Pt(14)
            
            # Espacio
            doc.add_paragraph()
            
            # Información del radicado
            info_radicado = doc.add_paragraph()
            info_radicado.add_run(f'Radicado: ').bold = True
            info_radicado.add_run(peticion.radicado)
            
            # Fecha
            info_fecha = doc.add_paragraph()
            info_fecha.add_run(f'Fecha de Respuesta: ').bold = True
            info_fecha.add_run(datetime.now().strftime('%d de %B de %Y'))
            
            # Peticionario
            if peticion.peticionario_nombre:
                info_peticionario = doc.add_paragraph()
                info_peticionario.add_run(f'Peticionario: ').bold = True
                info_peticionario.add_run(peticion.peticionario_nombre)
            
            # Línea separadora
            doc.add_paragraph('_' * 80)
            
            # Espacio
            doc.add_paragraph()
            
            # Contenido de la respuesta
            # Dividir por párrafos y agregar al documento
            parrafos = contenido_respuesta.split('\n')
            for parrafo in parrafos:
                if parrafo.strip():
                    p = doc.add_paragraph(parrafo.strip())
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    p_format = p.paragraph_format
                    p_format.line_spacing = 1.5
                    p_format.space_after = Pt(6)
                    
                    # Aplicar formato a todo el texto del párrafo
                    for run in p.runs:
                        run.font.name = 'Times New Roman'
                        run.font.size = Pt(12)
                else:
                    doc.add_paragraph()  # Línea en blanco
            
            # Guardar documento en memoria
            file_stream = io.BytesIO()
            doc.save(file_stream)
            file_stream.seek(0)
            
            # Preparar respuesta HTTP
            response = HttpResponse(
                file_stream.read(),
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            
            filename = f'Respuesta_{peticion.radicado}_{datetime.now().strftime("%Y%m%d")}.docx'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            logger.error(f"Error generando documento Word para {radicado}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})