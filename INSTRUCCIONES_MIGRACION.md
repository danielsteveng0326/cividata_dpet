# Instrucciones de Migración - Sistema de Autenticación

## ⚠️ IMPORTANTE - LEER ANTES DE EJECUTAR

Este documento contiene las instrucciones para aplicar los cambios del nuevo sistema de autenticación con usuarios y dependencias.

## Cambios Implementados

### 1. **Modelos Nuevos**
- ✅ **Usuario personalizado**: Modelo de autenticación con cédula como username
- ✅ **Dependencia**: Modelo para gestionar oficinas/dependencias

### 2. **Sistema de Autenticación**
- ✅ Login con cédula y contraseña
- ✅ Registro de usuarios (solo administradores)
- ✅ Recuperación de contraseña por email
- ✅ Cambio de contraseña obligatorio en primer login
- ✅ Contraseñas aleatorias enviadas por correo

### 3. **Eliminación del Modal**
- ✅ Se eliminó el modal que pedía ciudad, nombre del servidor y cargo
- ✅ Ahora estos datos se obtienen automáticamente del usuario autenticado

## Pasos para Aplicar los Cambios

### Paso 1: Configurar Variables de Entorno

Crea o actualiza tu archivo `.env` con la configuración de email:

```env
# Configuración de Email (ejemplo con Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicacion
DEFAULT_FROM_EMAIL=noreply@municipio.gov.co
```

**Nota para Gmail**: Debes generar una "Contraseña de aplicación" en tu cuenta de Google:
1. Ve a https://myaccount.google.com/security
2. Activa la verificación en 2 pasos
3. Genera una contraseña de aplicación

### Paso 2: Respaldar la Base de Datos Actual

**MUY IMPORTANTE**: Antes de hacer las migraciones, respalda tu base de datos:

```bash
# Copiar el archivo de base de datos
copy db.sqlite3 db.sqlite3.backup
```

### Paso 3: Eliminar Migraciones Anteriores (SOLO SI ES NECESARIO)

Si tienes problemas con las migraciones, puedes eliminar las migraciones anteriores:

```bash
# Eliminar archivos de migración (excepto __init__.py)
del peticiones\migrations\0*.py

# O manualmente elimina todos los archivos 0001_initial.py, 0002_*.py, etc.
# PERO DEJA el archivo __init__.py
```

### Paso 4: Crear las Nuevas Migraciones

```bash
python manage.py makemigrations
```

### Paso 5: Aplicar las Migraciones

```bash
python manage.py migrate
```

### Paso 6: Crear un Superusuario

Después de las migraciones, crea el primer usuario administrador:

```bash
python manage.py createsuperuser
```

Te pedirá:
- **Cédula**: Tu número de identificación (será tu usuario)
- **Nombre completo**: Tu nombre completo
- **Email**: Tu correo electrónico
- **Password**: Contraseña segura

### Paso 7: Crear Dependencias Iniciales

Accede al sistema con el superusuario y crea las dependencias:

1. Inicia el servidor: `python manage.py runserver`
2. Ve a http://localhost:8000/login/
3. Inicia sesión con tu cédula y contraseña
4. Ve a "Dependencias" en el menú lateral
5. Crea las dependencias de tu entidad

Ejemplo de dependencia:
- **Prefijo**: 001
- **Nombre Oficina**: Secretaría de Gobierno
- **Ciudad**: Bogotá D.C.

### Paso 8: Registrar Usuarios

Una vez creadas las dependencias, puedes registrar usuarios:

1. Ve a "Usuarios" en el menú lateral
2. Haz clic en "Nuevo Usuario"
3. Completa el formulario
4. El sistema generará una contraseña aleatoria y la enviará al correo del usuario

## Estructura de Usuarios

### Campos del Usuario:
- **Cédula** (ID único y username)
- **Nombre completo**
- **Cargo**
- **Dependencia** (relación con tabla Dependencias)
- **Correo electrónico**
- **Teléfono**

### Campos de la Dependencia:
- **Prefijo** (código numérico único)
- **Nombre oficina**
- **Ciudad**
- **Responsables** (usuarios asignados a la dependencia)

## Flujo de Trabajo del Usuario

1. **Registro**: Un administrador registra al usuario
2. **Email**: El usuario recibe un correo con su cédula y contraseña temporal
3. **Primer Login**: El usuario inicia sesión con su cédula
4. **Cambio de Contraseña**: El sistema obliga a cambiar la contraseña temporal
5. **Uso Normal**: El usuario puede usar el sistema normalmente

## Recuperación de Contraseña

Si un usuario olvida su contraseña:

1. En la pantalla de login, hace clic en "¿Olvidaste tu contraseña?"
2. Ingresa su correo electrónico
3. Recibe un email con un enlace de recuperación
4. Hace clic en el enlace y crea una nueva contraseña

## Generación de Documentos Word

Ahora los documentos Word se generan automáticamente con los datos del usuario:

- **Ciudad**: Se obtiene de la dependencia del usuario
- **Nombre del Funcionario**: Se obtiene del usuario autenticado
- **Cargo**: Se obtiene del usuario autenticado

Ya no es necesario ingresar estos datos manualmente.

## Solución de Problemas

### Error: "No such table: peticiones_usuario"

Esto significa que las migraciones no se aplicaron correctamente. Solución:

```bash
python manage.py migrate --run-syncdb
```

### Error: "UNIQUE constraint failed"

Si ya tienes datos en la base de datos, puede haber conflictos. Opciones:

1. **Opción 1 (Recomendada para desarrollo)**: Eliminar la base de datos y empezar de nuevo
   ```bash
   del db.sqlite3
   python manage.py migrate
   python manage.py createsuperuser
   ```

2. **Opción 2 (Para producción)**: Migración manual de datos existentes

### Error al enviar emails

Si los emails no se envían:

1. Verifica que las credenciales en `.env` sean correctas
2. Para Gmail, asegúrate de usar una "Contraseña de aplicación"
3. Para desarrollo, puedes usar el backend de consola:
   ```env
   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
   ```
   Esto mostrará los emails en la consola en lugar de enviarlos

## Verificación Post-Migración

Después de aplicar los cambios, verifica:

- ✅ Puedes acceder a http://localhost:8000/login/
- ✅ Puedes iniciar sesión con el superusuario
- ✅ Puedes crear dependencias
- ✅ Puedes registrar usuarios
- ✅ Los usuarios reciben emails (o se muestran en consola)
- ✅ Puedes generar documentos Word sin el modal

## Comandos Útiles

```bash
# Ver estado de las migraciones
python manage.py showmigrations

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver

# Ver logs en tiempo real
python manage.py runserver --verbosity 2
```

## Contacto y Soporte

Si encuentras problemas durante la migración, revisa:

1. Los logs del servidor Django
2. El archivo `logs/django.log`
3. La consola donde ejecutas `runserver`

---

**Fecha de creación**: 2025-01-11
**Versión del sistema**: 2.0 - Sistema de Autenticación Integrado
