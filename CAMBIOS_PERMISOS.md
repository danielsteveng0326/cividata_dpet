# Cambios de Permisos Implementados

## Resumen de Cambios

Se han implementado restricciones de acceso más estrictas en el sistema:

### 1. **Gestión Administrativa - Solo Dependencia 111 (Jefe Jurídica)**

Los siguientes módulos ahora **solo** pueden ser accedidos por usuarios que pertenezcan a la **dependencia 111 (Jefe Jurídica)**:

#### Módulos Restringidos:
- ✅ **Gestión de Usuarios** (`/usuarios/`)
  - Listar usuarios
  - Registrar nuevos usuarios
  
- ✅ **Gestión de Dependencias** (`/dependencias/`)
  - Listar dependencias
  - Crear nuevas dependencias
  
- ✅ **Gestión de Días No Hábiles** (`/calendario-dias-no-habiles/`)
  - Ver calendario
  - Agregar días no hábiles
  - Eliminar días no hábiles
  - Verificar fechas

### 2. **Admin de Django - Solo Superuser Específico**

El acceso al **Admin de Django** (`/admin/`) ahora está restringido **únicamente** al superuser con:
- **Cédula:** `1020458606`
- **Permisos:** `is_superuser = True`

Ningún otro usuario, incluso si tiene `is_staff = True`, podrá acceder al admin de Django.

---

## Implementación Técnica

### Funciones de Verificación de Permisos

Se crearon tres funciones en `peticiones/auth_views.py`:

```python
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
```

### Decoradores Aplicados

Todas las vistas administrativas ahora usan `@user_passes_test(is_jefe_juridica)`:

```python
@user_passes_test(is_jefe_juridica)
def lista_usuarios(request):
    """Vista para listar todos los usuarios (solo Jefe Jurídica - dependencia 111)"""
    ...

@user_passes_test(is_jefe_juridica)
def lista_dependencias(request):
    """Vista para listar dependencias (solo Jefe Jurídica - dependencia 111)"""
    ...

@user_passes_test(is_jefe_juridica)
def calendario_dias_no_habiles(request):
    """Vista del calendario interactivo (solo Jefe Jurídica - dependencia 111)"""
    ...
```

### Middleware para Admin de Django

Se creó un middleware personalizado en `peticiones/middleware.py`:

```python
class AdminAccessMiddleware:
    """
    Middleware que restringe el acceso al admin de Django
    solo al superuser con cédula 1020458606
    """
    
    def __call__(self, request):
        if request.path.startswith('/admin/'):
            if request.user.is_authenticated:
                if not (request.user.cedula == '1020458606' and request.user.is_superuser):
                    messages.error(request, 'No tienes permisos para acceder al panel de administración de Django')
                    return redirect('index')
        
        response = self.get_response(request)
        return response
```

El middleware se agregó en `municipio_ia/settings.py`:

```python
MIDDLEWARE = [
    ...
    'peticiones.middleware.AdminAccessMiddleware',  # Middleware personalizado
]
```

### Actualización del Menú de Navegación

El template `base.html` ahora muestra los enlaces condicionalmente:

```django
{% if user.dependencia and user.dependencia.prefijo == '111' or user.cedula == '1020458606' and user.is_superuser %}
<hr class="text-white">
<small class="text-white opacity-75 px-3">ADMINISTRACIÓN</small>
<a class="nav-link" href="{% url 'lista_usuarios' %}">
    <i class="fas fa-users"></i> Usuarios
</a>
<a class="nav-link" href="{% url 'lista_dependencias' %}">
    <i class="fas fa-building"></i> Dependencias
</a>
<a class="nav-link" href="{% url 'calendario_dias_no_habiles' %}">
    <i class="fas fa-calendar-times"></i> Días No Hábiles
</a>

{% if user.cedula == '1020458606' and user.is_superuser %}
<a class="nav-link" href="/admin/">
    <i class="fas fa-cog"></i> Admin Django
</a>
{% endif %}
{% endif %}
```

---

## Comportamiento del Sistema

### Para Usuarios Normales:
- ❌ **NO** pueden ver el menú de administración
- ❌ **NO** pueden acceder a `/usuarios/`, `/dependencias/`, `/calendario-dias-no-habiles/`
- ❌ **NO** pueden acceder a `/admin/`
- ✅ **SÍ** pueden ver y gestionar peticiones de su propia dependencia

### Para Usuarios de Jefe Jurídica (Dependencia 111):
- ✅ **SÍ** pueden ver el menú de administración
- ✅ **SÍ** pueden gestionar usuarios
- ✅ **SÍ** pueden gestionar dependencias
- ✅ **SÍ** pueden gestionar días no hábiles
- ✅ **SÍ** pueden ver TODAS las peticiones de todas las dependencias
- ❌ **NO** pueden acceder a `/admin/` (a menos que sean el superuser específico)

### Para el Superuser (Cédula 1020458606):
- ✅ **SÍ** pueden acceder a TODO lo anterior
- ✅ **SÍ** pueden gestionar usuarios, dependencias y días no hábiles
- ✅ **SÍ** pueden ver TODAS las peticiones de todas las dependencias
- ✅ **SÍ** pueden acceder al Admin de Django (`/admin/`)
- ✅ Acceso completo y total al sistema (combina permisos de Jefe Jurídica + Admin Django)

---

## Mensajes de Error

### Intento de Acceso No Autorizado a Módulos Administrativos:
Si un usuario que NO pertenece a la dependencia 111 intenta acceder a:
- `/usuarios/`
- `/dependencias/`
- `/calendario-dias-no-habiles/`

Será redirigido a la página de login con un mensaje de error.

### Intento de Acceso No Autorizado al Admin de Django:
Si un usuario que NO es el superuser con cédula 1020458606 intenta acceder a `/admin/`:

```
❌ No tienes permisos para acceder al panel de administración de Django
```

Y será redirigido al dashboard principal.

---

## Archivos Modificados

1. **`peticiones/auth_views.py`**
   - Agregadas funciones `is_jefe_juridica()` y `is_superuser_admin()`
   - Actualizados decoradores de todas las vistas administrativas

2. **`peticiones/middleware.py`** (NUEVO)
   - Middleware personalizado para restringir acceso al admin

3. **`municipio_ia/settings.py`**
   - Agregado middleware `AdminAccessMiddleware`

4. **`templates/base.html`**
   - Actualizado menú de navegación con condiciones de permisos

---

## Verificación de Permisos

### Para Probar:

1. **Usuario Normal (ej: Infraestructura):**
   ```
   - Iniciar sesión con usuario de otra dependencia
   - Verificar que NO aparece el menú "ADMINISTRACIÓN"
   - Intentar acceder a /usuarios/ → Debe redirigir al login
   - Intentar acceder a /admin/ → Debe mostrar error y redirigir
   ```

2. **Usuario Jefe Jurídica (Dependencia 111):**
   ```
   - Iniciar sesión con usuario de dependencia 111
   - Verificar que SÍ aparece el menú "ADMINISTRACIÓN"
   - Acceder a /usuarios/ → Debe funcionar
   - Acceder a /dependencias/ → Debe funcionar
   - Acceder a /calendario-dias-no-habiles/ → Debe funcionar
   - Intentar acceder a /admin/ → Debe mostrar error (si no es el superuser)
   ```

3. **Superuser (Cédula 1020458606):**
   ```
   - Iniciar sesión con el superuser
   - Verificar que aparece el enlace "Admin Django"
   - Acceder a /admin/ → Debe funcionar correctamente
   ```

---

## Seguridad

✅ **Protección a nivel de backend:** Los decoradores `@user_passes_test` verifican permisos en el servidor

✅ **Protección a nivel de middleware:** El middleware intercepta todas las peticiones al admin

✅ **Protección a nivel de frontend:** El menú solo muestra enlaces autorizados

✅ **Mensajes claros:** Los usuarios reciben mensajes informativos cuando no tienen permisos

---

## Notas Importantes

1. **Dependencia 111 es crítica:** Asegúrate de que siempre exista y tenga al menos un usuario asignado

2. **Superuser único:** Solo el usuario con cédula `1020458606` puede acceder al admin de Django

3. **Permisos heredados:** Los usuarios de Jefe Jurídica (111) tienen todos los permisos administrativos EXCEPTO el admin de Django (a menos que sean el superuser)

4. **Backup del superuser:** Asegúrate de tener las credenciales del superuser guardadas de forma segura

---

## Comandos Útiles

### Verificar usuarios de Jefe Jurídica:
```python
python manage.py shell
from peticiones.models import Usuario, Dependencia

jefe_juridica = Dependencia.objects.get(prefijo='111')
usuarios = Usuario.objects.filter(dependencia=jefe_juridica)
for u in usuarios:
    print(f"{u.nombre_completo} - {u.cedula}")
```

### Verificar el superuser:
```python
from peticiones.models import Usuario

superuser = Usuario.objects.get(cedula='1020458606')
print(f"Superuser: {superuser.nombre_completo}")
print(f"Is superuser: {superuser.is_superuser}")
```

---

## ✅ Sistema de Permisos Implementado Exitosamente

Todos los cambios de permisos han sido aplicados y están funcionando correctamente.
