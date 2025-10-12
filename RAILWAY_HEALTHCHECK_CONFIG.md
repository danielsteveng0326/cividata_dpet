# 🏥 Configuración de Healthcheck en Railway

## ✅ Endpoint de Healthcheck Implementado

Tu aplicación ahora tiene un endpoint `/health/` que Railway usa para verificar que el servicio está funcionando correctamente.

---

## 🔍 Endpoint de Healthcheck

### URL:
```
https://elcarmen.cividata.co/health/
https://tu-proyecto.railway.app/health/
```

### Respuesta:
```json
{
  "status": "healthy",
  "service": "cividata_dpet",
  "version": "1.0.0"
}
```

### Código HTTP: `200 OK`

---

## ⚙️ Configuración en Railway

### Archivo `railway.json`:

```json
{
  "deploy": {
    "healthcheckPath": "/health/",
    "healthcheckTimeout": 300
  }
}
```

### Configuración Manual (Alternativa):

Si prefieres configurarlo desde la UI de Railway:

1. **Ve a:** Railway → Tu Servicio → Settings → Deploy
2. **Healthcheck Path:** `/health/`
3. **Healthcheck Timeout:** `300` segundos (5 minutos)

---

## 🚀 Cómo Funciona el Healthcheck

### Durante el Deploy:

1. **Railway construye** tu aplicación
2. **Ejecuta migraciones** y crea el superuser
3. **Inicia Gunicorn** en el puerto asignado
4. **Espera hasta 300 segundos** para que `/health/` responda con 200
5. **Si responde 200:** ✅ Deploy exitoso, enruta tráfico
6. **Si no responde:** ❌ Deploy fallido, mantiene versión anterior

### Hostname del Healthcheck:

Railway hace las peticiones desde:
```
healthcheck.railway.app
```

Tu aplicación ya está configurada para aceptar peticiones desde este hostname con `ALLOWED_HOSTS = ['*']`.

---

## 📊 Ventajas del Healthcheck

✅ **Zero-downtime deployments** - No hay caída del servicio durante deploys
✅ **Validación automática** - Railway verifica que la app funciona antes de enrutar tráfico
✅ **Rollback automático** - Si el healthcheck falla, mantiene la versión anterior
✅ **Confiabilidad** - Solo recibe tráfico cuando está lista

---

## 🔧 Características del Endpoint `/health/`

### Sin Autenticación:
- No requiere login
- No requiere CSRF token (`@csrf_exempt`)
- Accesible públicamente

### Respuesta Rápida:
- No hace queries a la base de datos
- No ejecuta lógica compleja
- Responde instantáneamente

### Información Útil:
```json
{
  "status": "healthy",      // Estado del servicio
  "service": "cividata_dpet", // Nombre del servicio
  "version": "1.0.0"         // Versión de la aplicación
}
```

---

## 🧪 Probar el Healthcheck

### Desde el navegador:
```
https://elcarmen.cividata.co/health/
```

### Desde curl:
```bash
curl https://elcarmen.cividata.co/health/
```

### Desde Python:
```python
import requests
response = requests.get('https://elcarmen.cividata.co/health/')
print(response.status_code)  # Debe ser 200
print(response.json())       # {'status': 'healthy', ...}
```

---

## 📝 Configuración Completa en Railway

### Variables de Entorno Necesarias:

```bash
# Django
SECRET_KEY=tu-secret-key
DEBUG=False
RAILWAY_ENVIRONMENT=production

# Dominios
CUSTOM_DOMAINS=elcarmen.cividata.co

# Gemini
GEMINI_API_KEY=tu-api-key

# Database (automático)
DATABASE_URL=postgresql://...

# Port (automático)
PORT=8080
```

### Configuración de Deploy:

```json
{
  "deploy": {
    "startCommand": "python manage.py migrate && python create_superuser.py && gunicorn municipio_ia.wsgi:application --bind 0.0.0.0:$PORT --timeout 120 --workers 2",
    "healthcheckPath": "/health/",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

## 🔍 Monitorear Healthchecks

### En los Logs de Railway:

Busca estos mensajes durante el deploy:

```
====================
Starting Healthcheck
====================

Path: /health/
Retry window: 5m0s

Attempt #1 succeeded with status 200
✅ Healthcheck passed
```

### Si el Healthcheck Falla:

```
Attempt #1 failed with service unavailable
Attempt #2 failed with service unavailable
...
❌ Healthcheck failed after 5m0s
```

**Causas comunes:**
- La aplicación no está escuchando en `$PORT`
- El endpoint `/health/` no existe
- La aplicación no inició correctamente
- Timeout muy corto

---

## 🚨 Solución de Problemas

### Error: "service unavailable"

**Causa:** La aplicación no está escuchando en el puerto correcto.

**Solución:** Verifica que Gunicorn use `$PORT`:
```bash
gunicorn municipio_ia.wsgi:application --bind 0.0.0.0:$PORT
```

### Error: "failed with status 400"

**Causa:** El hostname `healthcheck.railway.app` no está permitido.

**Solución:** Ya está configurado con `ALLOWED_HOSTS = ['*']`.

### Error: "timeout exceeded"

**Causa:** La aplicación tarda más de 300 segundos en iniciar.

**Solución:** 
- Optimiza las migraciones
- Aumenta el timeout en `railway.json`
- Verifica que no haya procesos bloqueantes en el startup

---

## 📈 Healthcheck Avanzado (Opcional)

Si quieres un healthcheck más completo que verifique la base de datos:

```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

@csrf_exempt
def health_check(request):
    """Healthcheck con verificación de base de datos"""
    try:
        # Verificar conexión a la base de datos
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'service': 'cividata_dpet',
            'version': '1.0.0',
            'database': 'connected'
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=503)
```

**Nota:** Esto puede hacer el healthcheck más lento.

---

## 🔄 Monitoreo Continuo

Railway solo usa el healthcheck durante el deploy. Para monitoreo continuo:

### Opción 1: Uptime Kuma (Recomendado)

1. Instala Uptime Kuma desde Railway Templates
2. Configura un monitor para `https://elcarmen.cividata.co/health/`
3. Recibe alertas si el servicio cae

### Opción 2: Servicios Externos

- [UptimeRobot](https://uptimerobot.com/) (Gratis)
- [Pingdom](https://www.pingdom.com/)
- [StatusCake](https://www.statuscake.com/)

---

## ✅ Checklist de Configuración

- [x] Endpoint `/health/` creado
- [x] Retorna status 200
- [x] Sin autenticación requerida
- [x] CSRF exempt
- [x] `railway.json` configurado
- [x] `ALLOWED_HOSTS` permite `healthcheck.railway.app`
- [x] Gunicorn escucha en `$PORT`
- [x] Timeout configurado (300s)

---

## 🎯 Resumen

**Endpoint:** `/health/`  
**Método:** GET  
**Autenticación:** No requerida  
**Respuesta:** JSON con status 200  
**Timeout:** 300 segundos  
**Hostname:** `healthcheck.railway.app`  

**Estado:** ✅ Configurado y funcionando

---

## 📚 Referencias

- [Railway Healthchecks Docs](https://docs.railway.com/guides/healthchecks)
- [Django Health Check Best Practices](https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/settings.html)
