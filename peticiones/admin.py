# peticiones/admin.py
from django.contrib import admin
from .models import Peticion, ProcesamientoIA, RespuestaPeticion


@admin.register(Peticion)
class PeticionAdmin(admin.ModelAdmin):
    list_display = [
        'radicado', 
        'peticionario_nombre', 
        'fuente', 
        'estado', 
        'fecha_radicacion'
    ]
    list_filter = ['estado', 'fuente', 'fecha_radicacion']
    search_fields = [
        'radicado', 
        'peticionario_nombre', 
        'peticionario_id', 
        'peticionario_correo'
    ]
    readonly_fields = ['radicado', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información del Radicado', {
            'fields': ('radicado', 'fecha_radicacion', 'fecha_actualizacion')
        }),
        ('Datos del Peticionario', {
            'fields': (
                'peticionario_nombre', 
                'peticionario_id', 
                'peticionario_telefono',
                'peticionario_correo', 
                'peticionario_direccion'
            )
        }),
        ('Documento y Procesamiento', {
            'fields': ('archivo_pdf', 'transcripcion_completa')
        }),
        ('Estado y Fuente', {
            'fields': ('estado', 'fuente')
        }),
    )


@admin.register(ProcesamientoIA)
class ProcesamientoIAAdmin(admin.ModelAdmin):
    list_display = [
        'peticion__radicado', 
        'estado_procesamiento', 
        'fecha_procesamiento',
        'tiempo_procesamiento'
    ]
    list_filter = ['estado_procesamiento', 'fecha_procesamiento']
    readonly_fields = ['fecha_procesamiento']


@admin.register(RespuestaPeticion)
class RespuestaPeticionAdmin(admin.ModelAdmin):
    list_display = [
        'peticion__radicado', 
        'funcionario_responsable', 
        'fecha_respuesta'
    ]
    list_filter = ['fecha_respuesta']