# models.py
from django.db import models
from django.utils import timezone


class Peticion(models.Model):
    ESTADO_CHOICES = [
        ('sin_responder', 'Sin Responder'),
        ('respondido', 'Respondido'),
    ]
    
    FUENTE_CHOICES = [
        ('gestion_documental', 'Gestión Documental'),
        ('correo_electronico', 'Correo Electrónico'),
        ('presencial', 'Presencial'),
    ]
    
    # Radicado único con formato dpetaaaammddxxxxx
    radicado = models.CharField(max_length=20, unique=True, editable=False)
    
    # FECHA MANUAL Y OBLIGATORIA
    fecha_radicacion = models.DateTimeField(
        help_text="Fecha y hora de radicación del derecho de petición",
        verbose_name="Fecha de Radicación"
    )
    
    # Datos del peticionario (todos opcionales)
    peticionario_nombre = models.CharField(max_length=200, blank=True, null=True)
    peticionario_id = models.CharField(max_length=20, blank=True, null=True)
    peticionario_telefono = models.CharField(max_length=15, blank=True, null=True)
    peticionario_correo = models.EmailField(blank=True, null=True)
    peticionario_direccion = models.TextField(blank=True, null=True)
    
    # Archivo PDF cargado
    archivo_pdf = models.FileField(upload_to='peticiones/', help_text="Archivo PDF del derecho de petición")
    
    # Transcripción completa extraída por Gemini
    transcripcion_completa = models.TextField(blank=True, help_text="Transcripción completa del documento extraída por IA")
    
    # Estado y fuente
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='sin_responder')
    fuente = models.CharField(max_length=20, choices=FUENTE_CHOICES)
    
    # Archivos adjuntos al marcar como respondido
    archivo_respuesta_firmada = models.FileField(upload_to='respuestas_firmadas/', blank=True, null=True, help_text="Respuesta firmada")
    archivo_constancia_envio = models.FileField(upload_to='constancias_envio/', blank=True, null=True, help_text="Constancia de envío")
    fecha_respuesta = models.DateTimeField(blank=True, null=True, help_text="Fecha en que se marcó como respondido")
    
    # Fecha de actualización automática
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Derecho de Petición"
        verbose_name_plural = "Derechos de Petición"
        ordering = ['-fecha_radicacion']
    
    def save(self, *args, **kwargs):
        if not self.radicado:
            self.radicado = self.generar_radicado()
        super().save(*args, **kwargs)
    
    def generar_radicado(self):
        """
        Genera radicado único con formato: dpetaaaammddxxxxx
        Ejemplo: depet2025091000001
        """
        # Usar la fecha de radicación manual para generar el radicado
        fecha_rad = self.fecha_radicacion.date()
        año = fecha_rad.strftime('%Y')
        mes = fecha_rad.strftime('%m')
        dia = fecha_rad.strftime('%d')
        
        # Buscar el último radicado del día para generar el consecutivo
        prefijo = f"dpet{año}{mes}{dia}"
        ultima_peticion = Peticion.objects.filter(
            radicado__startswith=prefijo
        ).order_by('radicado').last()
        
        if ultima_peticion:
            # Extraer el número consecutivo del último radicado
            ultimo_consecutivo = int(ultima_peticion.radicado[-5:])
            nuevo_consecutivo = ultimo_consecutivo + 1
        else:
            nuevo_consecutivo = 1
        
        # Formatear el consecutivo a 5 dígitos
        consecutivo_formateado = str(nuevo_consecutivo).zfill(5)
        
        return f"{prefijo}{consecutivo_formateado}"
    
    def __str__(self):
        return f"{self.radicado} - {self.peticionario_nombre or 'Anónimo'}"


class ProcesamientoIA(models.Model):
    """
    Modelo para almacenar metadatos del procesamiento con IA
    """
    peticion = models.OneToOneField(Peticion, on_delete=models.CASCADE, related_name='procesamiento_ia')
    fecha_procesamiento = models.DateTimeField(auto_now_add=True)
    tiempo_procesamiento = models.FloatField(help_text="Tiempo en segundos")
    modelo_ia_usado = models.CharField(max_length=50, default="gemini-1.5-flash")
    estado_procesamiento = models.CharField(max_length=20, choices=[
        ('exitoso', 'Exitoso'),
        ('error', 'Error'),
        ('pendiente', 'Pendiente')
    ], default='pendiente')
    mensaje_error = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Procesamiento IA - {self.peticion.radicado}"


class RespuestaPeticion(models.Model):
    """
    Modelo para almacenar las respuestas a las peticiones
    """
    peticion = models.ForeignKey(Peticion, on_delete=models.CASCADE, related_name='respuestas')
    contenido_respuesta = models.TextField()
    fecha_respuesta = models.DateTimeField(auto_now_add=True)
    funcionario_responsable = models.CharField(max_length=200)
    archivo_respuesta = models.FileField(upload_to='respuestas/', blank=True, null=True)
    
    class Meta:
        ordering = ['-fecha_respuesta']
    
    def __str__(self):
        return f"Respuesta a {self.peticion.radicado}"