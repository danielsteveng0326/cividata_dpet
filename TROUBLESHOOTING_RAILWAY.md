# 🔧 Troubleshooting Railway - Healthcheck Failures

## ❌ Error: "Service Unavailable" en Healthcheck

### Síntomas:
```
Attempt #1 failed with service unavailable
Attempt #2 failed with service unavailable
...
```

---

## 🔍 Causas Comunes y Soluciones

### 1. ⚠️ Variables de Entorno Faltantes

**Causa:** Faltan variables de entorno obligatorias.

**Solución:**

Ve a Railway → Tu Servicio → Variables y agrega:

```bash
SECRET_KEY=tu-secret-key-generada
DEBUG=False
RAILWAY_ENVIRONMENT=production
GEMINI_API_KEY=tu-api-key
```

**Generar SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

### 2. 🗄️ PostgreSQL No Agregado

**Causa:** La aplicación necesita PostgreSQL pero no está configurado.

**Solución:**

1. En Railway, haz clic en **"+ New"**
2. Selecciona **"Database"** → **"PostgreSQL"**
3. Railway configurará automáticamente `DATABASE_URL`
4. Espera a que el servicio se reinicie

---

### 3. 🔐 ALLOWED_HOSTS Incorrecto

**Causa:** Django rechaza las peticiones porque el host no está permitido.

**Solución:** Ya está corregido en el código actualizado.

El `settings.py` ahora usa:
```python
if RAILWAY_ENVIRONMENT:
    ALLOWED_HOSTS = ['*']  # Railway maneja el routing
```

---

### 4. ⏱️ Timeout Durante Migraciones

**Causa:** Las migraciones tardan mucho y el healthcheck falla antes de que termine.

**Solución:** Ya está corregido con:
- `--timeout 120` en Gunicorn
- `healthcheckTimeout: 300` en railway.json

---

### 5. 🐛 Error en create_superuser.py

**Causa:** El script de creación de superuser falla.

**Solución:**

Revisa los logs en Railway:
```
Railway → Deployments → View Logs
```

Busca errores relacionados con `create_superuser.py`.

Si falla, puedes comentar temporalmente esa línea en `Procfile`:

```bash
# Temporal: sin create_superuser
web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn municipio_ia.wsgi:application --bind 0.0.0.0:$PORT --timeout 120 --workers 2
```

Luego crea el superuser manualmente desde la terminal de Railway.

---

### 6. 📦 Dependencias Faltantes

**Causa:** Alguna dependencia no se instaló correctamente.

**Solución:**

Revisa los logs de build:
```
Railway → Deployments → Build Logs
```

Verifica que todas las dependencias de `requirements.txt` se instalaron.

---

## 🚀 Pasos para Resolver el Error Actual

### Paso 1: Verificar Variables de Entorno

```bash
# En Railway → Variables, asegúrate de tener:
SECRET_KEY=...
DEBUG=False
RAILWAY_ENVIRONMENT=production
GEMINI_API_KEY=...
DATABASE_URL=postgresql://... (automático)
```

### Paso 2: Verificar PostgreSQL

```bash
# En Railway, verifica que PostgreSQL esté:
- Creado
- Conectado al servicio
- Con DATABASE_URL configurado
```

### Paso 3: Hacer Push de los Cambios

```bash
git add .
git commit -m "Fix: Configuración de Railway y healthcheck"
git push origin main
```

Railway detectará el push y redesplegará automáticamente.

### Paso 4: Monitorear el Deploy

```bash
# En Railway → Deployments:
1. Ve a "View Logs"
2. Busca estos mensajes:
   - "Running migrations..."
   - "✅ SUPERUSER CREADO EXITOSAMENTE"
   - "Booting worker with pid..."
   - "Listening at: http://0.0.0.0:XXXX"
```

### Paso 5: Verificar Healthcheck

```bash
# El healthcheck debería pasar ahora:
✅ Healthcheck passed on /login/
```

---

## 📊 Logs Importantes

### Logs de Migraciones:
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

### Logs de Superuser:
```
╔═══════════════════════════════════════╗
║  ✅ SUPERUSER CREADO EXITOSAMENTE    ║
╚═══════════════════════════════════════╝
```

### Logs de Gunicorn:
```
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:8080
[INFO] Using worker: sync
[INFO] Booting worker with pid: 123
```

---

## 🔄 Si el Problema Persiste

### Opción 1: Deploy Simplificado

Edita `Procfile` temporalmente:

```bash
# Versión simplificada sin create_superuser
web: python manage.py migrate && gunicorn municipio_ia.wsgi:application --bind 0.0.0.0:$PORT
```

Luego crea el superuser manualmente:

```bash
# En Railway Terminal:
python manage.py shell
```

```python
from peticiones.models import Usuario, Dependencia
dep = Dependencia.objects.create(prefijo='111', nombre_oficina='Jefe Jurídica', activa=True)
Usuario.objects.create_superuser(
    cedula='1020458606',
    nombre_completo='Admin',
    email='admin@example.com',
    cargo='Admin',
    password='cidoli2025',
    dependencia=dep
)
```

### Opción 2: Revisar Logs Completos

```bash
# En Railway Terminal:
railway logs --follow
```

Busca el error específico y compártelo para ayuda adicional.

### Opción 3: Verificar Configuración de Red

En Railway → Settings → Networking:
- Verifica que el puerto esté configurado correctamente
- Asegúrate de que el servicio esté público

---

## ✅ Checklist de Verificación

Antes de desplegar, verifica:

- [ ] PostgreSQL agregado y conectado
- [ ] Variables de entorno configuradas
- [ ] `SECRET_KEY` generada y configurada
- [ ] `GEMINI_API_KEY` configurada
- [ ] `DEBUG=False`
- [ ] `RAILWAY_ENVIRONMENT=production`
- [ ] Código pusheado a GitHub
- [ ] Railway detectó el push

---

## 🎯 Solución Rápida (Recomendada)

1. **Asegúrate de tener PostgreSQL:**
   ```
   Railway → + New → Database → PostgreSQL
   ```

2. **Configura las variables:**
   ```bash
   SECRET_KEY=tu-secret-key
   DEBUG=False
   RAILWAY_ENVIRONMENT=production
   GEMINI_API_KEY=tu-api-key
   ```

3. **Haz push de los cambios:**
   ```bash
   git add .
   git commit -m "Fix Railway configuration"
   git push origin main
   ```

4. **Espera el redeploy:**
   - Railway redesplegará automáticamente
   - Monitorea los logs
   - El healthcheck debería pasar

---

## 📞 Ayuda Adicional

Si el problema persiste:

1. **Copia los logs completos** de Railway
2. **Verifica las variables de entorno** (sin mostrar valores sensibles)
3. **Comparte el error específico** que aparece en los logs

---

## 🔗 Enlaces Útiles

- [Railway Docs - Healthchecks](https://docs.railway.com/guides/healthchecks)
- [Railway Docs - Environment Variables](https://docs.railway.com/guides/variables)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/)
