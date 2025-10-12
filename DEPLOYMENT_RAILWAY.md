# 🚂 Guía de Deployment en Railway

Esta guía te ayudará a desplegar tu aplicación Django de gestión de peticiones en Railway.

---

## 📋 Requisitos Previos

1. ✅ Cuenta en [Railway.app](https://railway.app/)
2. ✅ Cuenta en GitHub (para conectar el repositorio)
3. ✅ API Key de Google Gemini
4. ✅ Código del proyecto subido a GitHub

---

## 🚀 Paso 1: Preparar el Repositorio en GitHub

### 1.1 Crear repositorio en GitHub

```bash
# Inicializar git (si no lo has hecho)
git init

# Agregar todos los archivos
git add .

# Hacer commit
git commit -m "Preparar proyecto para deployment en Railway"

# Conectar con GitHub (reemplaza con tu repositorio)
git remote add origin https://github.com/tu-usuario/cividata_dpet.git

# Subir código
git push -u origin main
```

### 1.2 Verificar archivos importantes

Asegúrate de que estos archivos estén en tu repositorio:
- ✅ `requirements.txt`
- ✅ `runtime.txt`
- ✅ `Procfile`
- ✅ `railway.json`
- ✅ `.env.example`
- ✅ `.gitignore` (para no subir archivos sensibles)

---

## 🎯 Paso 2: Crear Proyecto en Railway

### 2.1 Crear nuevo proyecto

1. Ve a [railway.app](https://railway.app/)
2. Haz clic en **"New Project"**
3. Selecciona **"Deploy from GitHub repo"**
4. Autoriza Railway para acceder a tu GitHub
5. Selecciona el repositorio `cividata_dpet`

### 2.2 Agregar PostgreSQL

1. En tu proyecto de Railway, haz clic en **"+ New"**
2. Selecciona **"Database"**
3. Elige **"PostgreSQL"**
4. Railway creará automáticamente la base de datos y configurará `DATABASE_URL`

---

## ⚙️ Paso 3: Configurar Variables de Entorno

En Railway, ve a tu servicio → **Variables** y agrega:

### Variables Obligatorias:

```bash
# Django
SECRET_KEY=genera-una-clave-secreta-segura-aqui
DEBUG=False
ALLOWED_HOSTS=.railway.app

# Gemini API
GEMINI_API_KEY=tu-api-key-de-gemini

# Railway (automáticas, no las agregues manualmente)
DATABASE_URL=postgresql://... (Railway lo configura automáticamente)
PORT=... (Railway lo configura automáticamente)
RAILWAY_ENVIRONMENT=production (Railway lo configura automáticamente)
```

### Variables Opcionales (Email):

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password-de-aplicacion
DEFAULT_FROM_EMAIL=noreply@municipio.gov.co
```

### 🔑 Generar SECRET_KEY

Puedes generar una SECRET_KEY segura con:

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 🔨 Paso 4: Deploy Inicial

1. Railway detectará automáticamente que es un proyecto Django
2. Instalará las dependencias de `requirements.txt`
3. Ejecutará `collectstatic`
4. Ejecutará las migraciones
5. Iniciará el servidor con Gunicorn

### Monitorear el Deploy

- Ve a la pestaña **"Deployments"** para ver el progreso
- Revisa los **"Logs"** si hay errores

---

## 📊 Paso 5: Verificar Creación Automática del Superuser

El sistema crea automáticamente el superuser durante el deployment. **No necesitas hacer nada manualmente.**

### 5.1 Credenciales del Superuser

El sistema crea automáticamente un superuser con estas credenciales:

```
Usuario (Cédula): 1020458606
Contraseña:       cidoli2025
```

**⚠️ IMPORTANTE:** Cambia la contraseña después del primer login por seguridad.

### 5.2 Verificar en los Logs

En Railway, ve a **"Deployments"** → **"Logs"** y busca:

```
✅ SUPERUSER CREADO EXITOSAMENTE
```

Si ves este mensaje, el superuser fue creado correctamente.

### 5.3 Cargar datos iniciales (opcional)

Si quieres cargar festivos y otras dependencias, conéctate a la terminal de Railway:

```bash
python inicializar_sistema.py
```

O manualmente:

```bash
python manage.py shell
```

```python
from peticiones.models import Dependencia, DiaNoHabil
from datetime import date

# Crear dependencia Jefe Jurídica
Dependencia.objects.create(
    prefijo='111',
    nombre_oficina='Jefe Jurídica',
    activa=True
)

# Crear días festivos 2025 (ejemplo)
festivos = [
    (date(2025, 1, 1), 'Año Nuevo', True),
    (date(2025, 1, 6), 'Día de los Reyes Magos', True),
    # ... agregar más festivos
]

for fecha, descripcion, es_festivo in festivos:
    DiaNoHabil.objects.create(
        fecha=fecha,
        descripcion=descripcion,
        es_festivo_nacional=es_festivo,
        activo=True
    )
```

---

## 🌐 Paso 6: Configurar Dominio (Opcional)

### Usar dominio de Railway

Railway te da un dominio automático como:
```
https://tu-proyecto.railway.app
```

### Usar dominio personalizado

1. Ve a **Settings** → **Domains**
2. Haz clic en **"Custom Domain"**
3. Ingresa tu dominio (ej: `peticiones.municipio.gov.co`)
4. Configura los registros DNS según las instrucciones de Railway
5. Actualiza `ALLOWED_HOSTS` en las variables de entorno:

```bash
ALLOWED_HOSTS=.railway.app,peticiones.municipio.gov.co
```

---

## 📁 Paso 7: Configurar Almacenamiento de Archivos (Media Files)

⚠️ **IMPORTANTE:** Railway no persiste archivos subidos entre deploys.

### Opciones para archivos media:

#### Opción 1: Usar Railway Volumes (Recomendado)

1. En Railway, ve a tu servicio
2. Haz clic en **"+ New"** → **"Volume"**
3. Monta el volumen en `/app/media`

#### Opción 2: Usar AWS S3 o Cloudinary

Instala django-storages:

```bash
pip install django-storages boto3
```

Configura en `settings.py`:

```python
if not DEBUG:
    # Configuración de S3
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
```

---

## 🔍 Paso 8: Verificación Post-Deploy

### Checklist de verificación:

- [ ] La aplicación carga correctamente
- [ ] Puedes hacer login con el superuser
- [ ] Los archivos estáticos se cargan (CSS, JS, imágenes)
- [ ] Puedes crear una petición de prueba
- [ ] El procesamiento de IA funciona (verifica API Key de Gemini)
- [ ] Los días no hábiles están configurados
- [ ] El calendario funciona correctamente
- [ ] Los permisos por dependencia funcionan

### URLs importantes:

```
https://tu-proyecto.railway.app/          # Dashboard
https://tu-proyecto.railway.app/admin/    # Admin Django
https://tu-proyecto.railway.app/login/    # Login
```

---

## 🐛 Solución de Problemas Comunes

### Error: "DisallowedHost"

**Solución:** Agrega tu dominio a `ALLOWED_HOSTS` en las variables de entorno.

```bash
ALLOWED_HOSTS=.railway.app,tu-dominio.com
```

### Error: "Static files not found"

**Solución:** Verifica que WhiteNoise esté instalado y configurado:

```bash
pip install whitenoise
```

Y en `settings.py`:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Debe estar aquí
    ...
]
```

### Error: "Database connection failed"

**Solución:** Verifica que PostgreSQL esté agregado al proyecto y que `DATABASE_URL` esté configurado.

### Error: "Gemini API not working"

**Solución:** Verifica que `GEMINI_API_KEY` esté configurado correctamente en las variables de entorno.

### Los archivos subidos desaparecen

**Solución:** Configura Railway Volumes o usa S3/Cloudinary para almacenamiento persistente.

---

## 📊 Monitoreo y Mantenimiento

### Ver logs en tiempo real

```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Ver logs
railway logs
```

### Escalar recursos

1. Ve a **Settings** → **Resources**
2. Ajusta CPU y RAM según necesidad
3. Railway cobra según uso

### Backups de base de datos

Railway hace backups automáticos de PostgreSQL, pero puedes hacer backups manuales:

```bash
# Exportar base de datos
railway run python manage.py dumpdata > backup.json

# Importar base de datos
railway run python manage.py loaddata backup.json
```

---

## 💰 Costos Estimados

Railway tiene un modelo de pago por uso:

- **Plan Hobby:** $5 USD de crédito gratis mensual
- **Plan Pro:** $20 USD/mes + uso adicional

### Estimación para este proyecto:

- **Aplicación Django:** ~$3-5 USD/mes
- **PostgreSQL:** ~$2-3 USD/mes
- **Total estimado:** ~$5-8 USD/mes

El plan gratuito ($5 USD) puede ser suficiente para desarrollo/pruebas.

---

## 🔐 Seguridad en Producción

### Checklist de seguridad:

- [ ] `DEBUG=False` en producción
- [ ] `SECRET_KEY` única y segura
- [ ] HTTPS habilitado (Railway lo hace automáticamente)
- [ ] `ALLOWED_HOSTS` configurado correctamente
- [ ] Cookies seguras (`SESSION_COOKIE_SECURE=True`)
- [ ] CSRF protection habilitado
- [ ] Variables de entorno para datos sensibles (no en código)
- [ ] Backups regulares de base de datos

---

## 📚 Recursos Adicionales

- [Documentación de Railway](https://docs.railway.app/)
- [Railway Discord](https://discord.gg/railway)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/)

---

## ✅ Resumen de Comandos Rápidos

```bash
# Deploy inicial
git add .
git commit -m "Deploy to Railway"
git push origin main

# Ver logs
railway logs

# Ejecutar comandos en Railway
railway run python manage.py migrate
railway run python manage.py createsuperuser
railway run python manage.py collectstatic

# Abrir shell de Django en Railway
railway run python manage.py shell
```

---

## 🎉 ¡Listo!

Tu aplicación de gestión de peticiones ahora está desplegada en Railway y lista para usar en producción.

**URL de tu aplicación:** https://tu-proyecto.railway.app

**Próximos pasos:**
1. Configura tu dominio personalizado
2. Carga los datos iniciales (dependencias, festivos)
3. Crea usuarios para cada dependencia
4. Prueba el flujo completo de peticiones
5. Monitorea los logs y el rendimiento

---

**¿Necesitas ayuda?** Revisa los logs en Railway o contacta al equipo de soporte.
