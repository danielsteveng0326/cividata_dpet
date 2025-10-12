# peticiones/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Peticion, ProcesamientoIA, RespuestaPeticion, Usuario, Dependencia, DiaNoHabil

@admin.register(Peticion)
class PeticionAdmin(admin.ModelAdmin):
    list_display = [
        'radicado', 
        'peticionario_nombre',
        'dependencia',
        'fuente', 
        'estado', 
        'fecha_radicacion',
        'fecha_vencimiento'
    ]
    list_filter = ['estado', 'fuente', 'dependencia', 'fecha_radicacion']
    search_fields = [
        'radicado', 
        'peticionario_nombre', 
        'peticionario_id', 
        'peticionario_correo'
    ]
    readonly_fields = ['radicado', 'fecha_vencimiento', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información del Radicado', {
            'fields': ('radicado', 'fecha_radicacion', 'dependencia', 'fecha_vencimiento', 'fecha_actualizacion')
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


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = [
        'cedula',
        'nombre_completo',
        'email',
        'cargo',
        'dependencia',
        'is_active',
        'is_staff'
    ]
    list_filter = ['is_staff', 'is_active', 'dependencia']
    search_fields = ['cedula', 'nombre_completo', 'email']
    ordering = ['nombre_completo']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('cedula', 'nombre_completo', 'email', 'telefono')
        }),
        ('Información Laboral', {
            'fields': ('cargo', 'dependencia')
        }),
        ('Contraseña', {
            'fields': ('password', 'debe_cambiar_contrasena')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        ('Crear Usuario', {
            'classes': ('wide',),
            'fields': ('cedula', 'nombre_completo', 'email', 'password1', 'password2', 'cargo', 'dependencia')
        }),
    )
    
    readonly_fields = ['last_login', 'date_joined']


@admin.register(Dependencia)
class DependenciaAdmin(admin.ModelAdmin):
    list_display = [
        'prefijo',
        'nombre_oficina',
        'ciudad',
        'activa',
        'fecha_creacion'
    ]
    list_filter = ['activa', 'ciudad']
    search_fields = ['prefijo', 'nombre_oficina', 'ciudad']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('prefijo', 'nombre_oficina', 'ciudad')
        }),
        ('Estado', {
            'fields': ('activa',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion')
        }),
    )


@admin.register(DiaNoHabil)
class DiaNoHabilAdmin(admin.ModelAdmin):
    list_display = [
        'fecha',
        'descripcion',
        'es_festivo_nacional',
        'activo',
        'fecha_creacion'
    ]
    list_filter = ['es_festivo_nacional', 'activo', 'fecha']
    search_fields = ['descripcion', 'fecha']
    readonly_fields = ['fecha_creacion']
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('Información del Día', {
            'fields': ('fecha', 'descripcion', 'es_festivo_nacional')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Fecha de Registro', {
            'fields': ('fecha_creacion',)
        }),
    )