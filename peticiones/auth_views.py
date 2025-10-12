# auth_views.py - Vistas de autenticación y gestión de usuarios
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.http import JsonResponse
from datetime import timedelta
from .models import Usuario, Dependencia, DiaNoHabil
from .services.dias_habiles_service import DiasHabilesService
import logging
import json

logger = logging.getLogger(__name__)


def login_view(request):
    """Vista de inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        cedula = request.POST.get('cedula')
        password = request.POST.get('password')
        
        user = authenticate(request, username=cedula, password=password)
        
        if user is not None:
            login(request, user)
            
            # Verificar si debe cambiar contraseña
            if user.debe_cambiar_contrasena:
                messages.warning(
                    request,
                    'Por seguridad, debe cambiar su contraseña temporal.'
                )
                return redirect('cambiar_contrasena')
            
            messages.success(request, f'Bienvenido, {user.nombre_completo}')
            return redirect('index')
        else:
            messages.error(request, 'Cédula o contraseña incorrectos')
    
    return render(request, 'auth/login.html')


@login_required
def logout_view(request):
    """Vista de cierre de sesión"""
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('login')


def is_staff_user(user):
    """Verifica si el usuario es staff (administrador)"""
    return user.is_staff


def is_jefe_juridica(user):
    """Verifica si el usuario pertenece a la dependencia 111 (Jefe Jurídica) o es el superuser"""
    if not user.is_authenticated:
        return False
    # El superuser 1020458606 tiene acceso completo
    if user.cedula == '1020458606' and user.is_superuser:
        return True
    # O si pertenece a la dependencia 111
    return user.dependencia and user.dependencia.prefijo == '111'


def is_superuser_admin(user):
    """Verifica si el usuario es el superuser con cédula 1020458606"""
    if not user.is_authenticated:
        return False
    return user.cedula == '1020458606' and user.is_superuser


@user_passes_test(is_jefe_juridica)
def registro_usuario(request):
    """Vista para registrar nuevos usuarios (solo Jefe Jurídica - dependencia 111)"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            cedula = request.POST.get('cedula')
            nombre_completo = request.POST.get('nombre_completo')
            cargo = request.POST.get('cargo')
            dependencia_id = request.POST.get('dependencia')
            email = request.POST.get('email')
            telefono = request.POST.get('telefono', '')
            
            # Validar que no exista el usuario
            if Usuario.objects.filter(cedula=cedula).exists():
                messages.error(request, f'Ya existe un usuario con la cédula {cedula}')
                return redirect('registro_usuario')
            
            if Usuario.objects.filter(email=email).exists():
                messages.error(request, f'Ya existe un usuario con el correo {email}')
                return redirect('registro_usuario')
            
            # Obtener dependencia
            dependencia = None
            if dependencia_id:
                try:
                    dependencia = Dependencia.objects.get(prefijo=dependencia_id)
                except Dependencia.DoesNotExist:
                    messages.error(request, 'Dependencia no encontrada')
                    return redirect('registro_usuario')
            
            # Generar contraseña aleatoria
            password_temporal = Usuario.objects.generar_contrasena_aleatoria()
            
            # Crear usuario
            usuario = Usuario.objects.create_user(
                cedula=cedula,
                nombre_completo=nombre_completo,
                email=email,
                password=password_temporal,
                cargo=cargo,
                dependencia=dependencia,
                telefono=telefono
            )
            
            # Enviar correo con contraseña temporal
            try:
                asunto = 'Bienvenido al Sistema de Gestión de Peticiones'
                mensaje = f"""
Hola {nombre_completo},

Bienvenido al Sistema de Gestión de Derechos de Petición.

Tus credenciales de acceso son:
- Usuario (Cédula): {cedula}
- Contraseña temporal: {password_temporal}

Por seguridad, deberás cambiar tu contraseña en el primer inicio de sesión.

Puedes acceder al sistema en: {request.build_absolute_uri('/')}

Saludos,
Equipo de Sistemas
"""
                send_mail(
                    asunto,
                    mensaje,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                messages.success(
                    request,
                    f'Usuario {nombre_completo} registrado exitosamente. '
                    f'Se ha enviado un correo con las credenciales a {email}'
                )
            except Exception as e:
                logger.error(f"Error enviando correo de bienvenida: {str(e)}")
                messages.warning(
                    request,
                    f'Usuario registrado, pero no se pudo enviar el correo. '
                    f'Contraseña temporal: {password_temporal}'
                )
            
            return redirect('lista_usuarios')
            
        except Exception as e:
            logger.error(f"Error en registro de usuario: {str(e)}")
            messages.error(request, f'Error al registrar usuario: {str(e)}')
    
    # GET: Mostrar formulario
    dependencias = Dependencia.objects.filter(activa=True).order_by('nombre_oficina')
    context = {
        'dependencias': dependencias
    }
    return render(request, 'auth/registro_usuario.html', context)


@user_passes_test(is_jefe_juridica)
def lista_usuarios(request):
    """Vista para listar todos los usuarios (solo Jefe Jurídica - dependencia 111)"""
    from django.db.models import Q
    
    usuarios = Usuario.objects.select_related('dependencia').order_by('nombre_completo')
    
    # Filtro de búsqueda
    search = request.GET.get('search', '')
    if search:
        usuarios = usuarios.filter(
            Q(cedula__icontains=search) |
            Q(nombre_completo__icontains=search) |
            Q(email__icontains=search)
        )
    
    context = {
        'usuarios': usuarios,
        'search': search
    }
    return render(request, 'auth/lista_usuarios.html', context)


@login_required
def cambiar_contrasena(request):
    """Vista para cambiar contraseña"""
    if request.method == 'POST':
        password_actual = request.POST.get('password_actual')
        password_nueva = request.POST.get('password_nueva')
        password_confirmacion = request.POST.get('password_confirmacion')
        
        # Validar contraseña actual
        if not request.user.check_password(password_actual):
            messages.error(request, 'La contraseña actual es incorrecta')
            return redirect('cambiar_contrasena')
        
        # Validar que las contraseñas nuevas coincidan
        if password_nueva != password_confirmacion:
            messages.error(request, 'Las contraseñas nuevas no coinciden')
            return redirect('cambiar_contrasena')
        
        # Validar longitud mínima
        if len(password_nueva) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres')
            return redirect('cambiar_contrasena')
        
        # Cambiar contraseña
        request.user.set_password(password_nueva)
        request.user.debe_cambiar_contrasena = False
        request.user.save()
        
        # Actualizar sesión
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, request.user)
        
        messages.success(request, 'Contraseña cambiada exitosamente')
        return redirect('index')
    
    return render(request, 'auth/cambiar_contrasena.html')


def recuperar_contrasena(request):
    """Vista para solicitar recuperación de contraseña"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            usuario = Usuario.objects.get(email=email)
            
            # Generar token de recuperación
            token = default_token_generator.make_token(usuario)
            uid = urlsafe_base64_encode(force_bytes(usuario.pk))
            
            # Construir URL de recuperación
            reset_url = request.build_absolute_uri(
                f'/reset-password/{uid}/{token}/'
            )
            
            # Enviar correo
            asunto = 'Recuperación de Contraseña'
            mensaje = f"""
Hola {usuario.nombre_completo},

Has solicitado recuperar tu contraseña.

Para crear una nueva contraseña, haz clic en el siguiente enlace:
{reset_url}

Si no solicitaste este cambio, ignora este correo.

El enlace expirará en 24 horas.

Saludos,
Equipo de Sistemas
"""
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            messages.success(
                request,
                'Se ha enviado un correo con instrucciones para recuperar tu contraseña'
            )
            return redirect('login')
            
        except Usuario.DoesNotExist:
            # Por seguridad, no revelar si el email existe o no
            messages.success(
                request,
                'Si el correo está registrado, recibirás instrucciones para recuperar tu contraseña'
            )
            return redirect('login')
        except Exception as e:
            logger.error(f"Error en recuperación de contraseña: {str(e)}")
            messages.error(request, 'Error al enviar el correo de recuperación')
    
    return render(request, 'auth/recuperar_contrasena.html')


def reset_contrasena(request, uidb64, token):
    """Vista para resetear contraseña con token"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        usuario = None
    
    if usuario is not None and default_token_generator.check_token(usuario, token):
        if request.method == 'POST':
            password_nueva = request.POST.get('password_nueva')
            password_confirmacion = request.POST.get('password_confirmacion')
            
            if password_nueva != password_confirmacion:
                messages.error(request, 'Las contraseñas no coinciden')
                return render(request, 'auth/reset_contrasena.html')
            
            if len(password_nueva) < 8:
                messages.error(request, 'La contraseña debe tener al menos 8 caracteres')
                return render(request, 'auth/reset_contrasena.html')
            
            # Cambiar contraseña
            usuario.set_password(password_nueva)
            usuario.debe_cambiar_contrasena = False
            usuario.save()
            
            messages.success(request, 'Contraseña restablecida exitosamente. Puedes iniciar sesión.')
            return redirect('login')
        
        return render(request, 'auth/reset_contrasena.html')
    else:
        messages.error(request, 'El enlace de recuperación es inválido o ha expirado')
        return redirect('login')


# ========================================
# VISTAS DE GESTIÓN DE DEPENDENCIAS
# ========================================

@user_passes_test(is_jefe_juridica)
def lista_dependencias(request):
    """Vista para listar dependencias (solo Jefe Jurídica - dependencia 111)"""
    dependencias = Dependencia.objects.all().order_by('nombre_oficina')
    
    context = {
        'dependencias': dependencias
    }
    return render(request, 'auth/lista_dependencias.html', context)


@user_passes_test(is_jefe_juridica)
def crear_dependencia(request):
    """Vista para crear nueva dependencia (solo Jefe Jurídica - dependencia 111)"""
    if request.method == 'POST':
        try:
            prefijo = request.POST.get('prefijo')
            nombre_oficina = request.POST.get('nombre_oficina')
            ciudad = request.POST.get('ciudad', '').strip() or None  # Convertir string vacío a None
            
            # Validar que no exista el prefijo
            if Dependencia.objects.filter(prefijo=prefijo).exists():
                messages.error(request, f'Ya existe una dependencia con el prefijo {prefijo}')
                return redirect('crear_dependencia')
            
            # Crear dependencia
            dependencia = Dependencia.objects.create(
                prefijo=prefijo,
                nombre_oficina=nombre_oficina,
                ciudad=ciudad
            )
            
            messages.success(
                request,
                f'Dependencia {nombre_oficina} creada exitosamente'
            )
            return redirect('lista_dependencias')
            
        except Exception as e:
            logger.error(f"Error creando dependencia: {str(e)}")
            messages.error(request, f'Error al crear dependencia: {str(e)}')
    
    return render(request, 'auth/crear_dependencia.html')


# ========================================
# VISTAS DE GESTIÓN DE DÍAS NO HÁBILES
# ========================================

@user_passes_test(is_jefe_juridica)
def calendario_dias_no_habiles(request):
    """Vista del calendario interactivo para gestionar días no hábiles (solo Jefe Jurídica - dependencia 111)"""
    from datetime import date
    
    # Obtener año actual o el especificado
    año_actual = int(request.GET.get('año', date.today().year))
    
    # Obtener todos los días no hábiles del año
    dias_no_habiles = DiaNoHabil.objects.filter(
        fecha__year=año_actual,
        activo=True
    ).order_by('fecha')
    
    context = {
        'año_actual': año_actual,
        'dias_no_habiles': dias_no_habiles,
    }
    return render(request, 'auth/calendario_dias_no_habiles.html', context)


@user_passes_test(is_jefe_juridica)
def agregar_dia_no_habil(request):
    """Vista AJAX para agregar un día no hábil (solo Jefe Jurídica - dependencia 111)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            fecha_str = data.get('fecha')
            descripcion = data.get('descripcion')
            es_festivo = data.get('es_festivo_nacional', False)
            
            # Convertir string a fecha
            from datetime import datetime
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            
            # Verificar si ya existe
            if DiaNoHabil.objects.filter(fecha=fecha).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Ya existe un día no hábil registrado para esta fecha'
                })
            
            # Crear día no hábil
            dia_no_habil = DiaNoHabil.objects.create(
                fecha=fecha,
                descripcion=descripcion,
                es_festivo_nacional=es_festivo
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Día no hábil agregado correctamente',
                'dia': {
                    'id': dia_no_habil.id,
                    'fecha': dia_no_habil.fecha.strftime('%Y-%m-%d'),
                    'descripcion': dia_no_habil.descripcion,
                    'es_festivo_nacional': dia_no_habil.es_festivo_nacional
                }
            })
            
        except Exception as e:
            logger.error(f"Error agregando día no hábil: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@user_passes_test(is_jefe_juridica)
def eliminar_dia_no_habil(request, dia_id):
    """Vista AJAX para eliminar un día no hábil (solo Jefe Jurídica - dependencia 111)"""
    if request.method == 'POST':
        try:
            dia_no_habil = DiaNoHabil.objects.get(id=dia_id)
            dia_no_habil.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Día no hábil eliminado correctamente'
            })
            
        except DiaNoHabil.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Día no hábil no encontrado'
            })
        except Exception as e:
            logger.error(f"Error eliminando día no hábil: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@user_passes_test(is_jefe_juridica)
def verificar_dia_habil(request):
    """Vista AJAX para verificar si una fecha es día hábil (solo Jefe Jurídica - dependencia 111)"""
    if request.method == 'GET':
        try:
            fecha_str = request.GET.get('fecha')
            from datetime import datetime
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            
            es_habil = DiasHabilesService.es_dia_habil(fecha)
            descripcion = DiasHabilesService.obtener_descripcion_dia_no_habil(fecha)
            
            return JsonResponse({
                'success': True,
                'es_habil': es_habil,
                'descripcion': descripcion
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@user_passes_test(is_jefe_juridica)
def obtener_dias_no_habiles_mes(request):
    """Vista AJAX para obtener días no hábiles de un mes específico (solo Jefe Jurídica - dependencia 111)"""
    if request.method == 'GET':
        try:
            año = int(request.GET.get('año'))
            mes = int(request.GET.get('mes'))
            
            from datetime import date
            import calendar
            
            # Obtener primer y último día del mes
            primer_dia = date(año, mes, 1)
            ultimo_dia = date(año, mes, calendar.monthrange(año, mes)[1])
            
            # Obtener todos los días del mes
            dias_info = []
            fecha_actual = primer_dia
            
            while fecha_actual <= ultimo_dia:
                es_habil = DiasHabilesService.es_dia_habil(fecha_actual)
                descripcion = DiasHabilesService.obtener_descripcion_dia_no_habil(fecha_actual)
                
                dias_info.append({
                    'fecha': fecha_actual.strftime('%Y-%m-%d'),
                    'dia': fecha_actual.day,
                    'es_habil': es_habil,
                    'descripcion': descripcion if not es_habil else None
                })
                
                fecha_actual += timedelta(days=1)
            
            return JsonResponse({
                'success': True,
                'dias': dias_info
            })
            
        except Exception as e:
            logger.error(f"Error obteniendo días del mes: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})
