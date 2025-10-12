# models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import secrets
import string


# ========================================
# MODELOS DE DEPENDENCIAS
# ========================================

class Dependencia(models.Model):
    """
    Modelo para gestionar las dependencias/oficinas de la entidad
    """
    prefijo = models.CharField(
        max_length=10, 
        unique=True, 
        primary_key=True,
        verbose_name="Prefijo Numérico",
        help_text="Código numérico único de la dependencia (hasta 10 dígitos)"
    )
    nombre_oficina = models.CharField(
        max_length=200,
        verbose_name="Nombre de la Oficina"
    )
    ciudad = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Ciudad",
        help_text="Ciudad donde se ubica la dependencia (opcional)"
    )
    activa = models.BooleanField(
        default=True,
        verbose_name="Dependencia Activa"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Dependencia"
        verbose_name_plural = "Dependencias"
        ordering = ['nombre_oficina']
    
    def __str__(self):
        return f"{self.prefijo} - {self.nombre_oficina}"
    
    def get_responsables(self):
        """Retorna lista de usuarios responsables de esta dependencia"""
        return self.usuarios.filter(is_active=True)


# ========================================
# MODELOS DE USUARIOS PERSONALIZADOS
# ========================================

class UsuarioManager(BaseUserManager):
    """
    Manager personalizado para el modelo Usuario
    """
    def create_user(self, cedula, nombre_completo, email, password=None, **extra_fields):
        """Crea y guarda un usuario normal"""
        if not cedula:
            raise ValueError('El usuario debe tener una cédula')
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico')
        
        email = self.normalize_email(email)
        user = self.model(
            cedula=cedula,
            nombre_completo=nombre_completo,
            email=email,
            **extra_fields
        )
        
        # Si no se proporciona contraseña, generar una aleatoria
        if password is None:
            password = self.generar_contrasena_aleatoria()
        
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, cedula, nombre_completo, email, password=None, **extra_fields):
        """Crea y guarda un superusuario"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
        
        return self.create_user(cedula, nombre_completo, email, password, **extra_fields)
    
    @staticmethod
    def generar_contrasena_aleatoria(longitud=12):
        """Genera una contraseña aleatoria segura"""
        caracteres = string.ascii_letters + string.digits + "!@#$%&*"
        return ''.join(secrets.choice(caracteres) for _ in range(longitud))


class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de Usuario personalizado para el sistema
    """
    cedula = models.CharField(
        max_length=20,
        unique=True,
        primary_key=True,
        verbose_name="Número de Cédula",
        help_text="Número de identificación del servidor público"
    )
    nombre_completo = models.CharField(
        max_length=200,
        verbose_name="Nombre Completo"
    )
    cargo = models.CharField(
        max_length=200,
        verbose_name="Cargo"
    )
    dependencia = models.ForeignKey(
        Dependencia,
        on_delete=models.SET_NULL,
        null=True,
        related_name='usuarios',
        verbose_name="Dependencia"
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Correo Electrónico"
    )
    telefono = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Teléfono"
    )
    
    # Campos de Django para autenticación
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)
    
    # Campo para contraseña temporal (primera vez)
    debe_cambiar_contrasena = models.BooleanField(
        default=True,
        verbose_name="Debe Cambiar Contraseña",
        help_text="Indica si el usuario debe cambiar su contraseña en el próximo login"
    )
    
    objects = UsuarioManager()
    
    USERNAME_FIELD = 'cedula'
    REQUIRED_FIELDS = ['nombre_completo', 'email']
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['nombre_completo']
    
    def __str__(self):
        return f"{self.cedula} - {self.nombre_completo}"
    
    def get_full_name(self):
        return self.nombre_completo
    
    def get_short_name(self):
        return self.nombre_completo.split()[0] if self.nombre_completo else self.cedula


# ========================================
# MODELOS DE DÍAS NO HÁBILES
# ========================================

class DiaNoHabil(models.Model):
    """
    Modelo para gestionar días no hábiles personalizados
    (además de sábados, domingos y festivos nacionales)
    """
    fecha = models.DateField(
        unique=True,
        verbose_name="Fecha",
        help_text="Fecha del día no hábil"
    )
    descripcion = models.CharField(
        max_length=200,
        verbose_name="Descripción",
        help_text="Motivo del día no hábil (ej: Día de la Familia, Capacitación, etc.)"
    )
    es_festivo_nacional = models.BooleanField(
        default=False,
        verbose_name="Festivo Nacional",
        help_text="Marcar si es un festivo nacional de Colombia"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Día No Hábil"
        verbose_name_plural = "Días No Hábiles"
        ordering = ['fecha']
    
    def __str__(self):
        return f"{self.fecha.strftime('%d/%m/%Y')} - {self.descripcion}"


# ========================================
# MODELOS DE PETICIONES
# ========================================

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
    
    # Dependencia responsable
    dependencia = models.ForeignKey(
        Dependencia,
        on_delete=models.SET_NULL,
        null=True,
        related_name='peticiones',
        verbose_name="Dependencia Responsable",
        help_text="Dependencia encargada de responder la petición"
    )
    
    # Fecha de vencimiento (15 días hábiles desde radicación)
    fecha_vencimiento = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha de Vencimiento",
        help_text="Fecha máxima para responder (15 días hábiles)"
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
        
        # Calcular fecha de vencimiento si no existe
        if not self.fecha_vencimiento and self.fecha_radicacion:
            from .services.dias_habiles_service import DiasHabilesService
            self.fecha_vencimiento = DiasHabilesService.calcular_fecha_vencimiento(
                self.fecha_radicacion, 
                dias_habiles=15
            )
        
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