# Variables de Entorno para Railway

## ⚙️ Variables Obligatorias

Configura estas variables en Railway → Settings → Variables:

### 1. Django Settings

```bash
SECRET_KEY=genera-una-clave-secreta-aqui
DEBUG=False
RAILWAY_ENVIRONMENT=production
```

**Generar SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Gemini API

```bash
GEMINI_API_KEY=tu-api-key-de-gemini
```

**Obtener API Key:**
- Ve a: https://makersuite.google.com/app/apikey
- Crea una nueva API Key
- Cópiala y pégala aquí

---

## 🔄 Variables Automáticas (Railway las configura)

Estas variables son configuradas automáticamente por Railway, **NO las agregues manualmente**:

```bash
DATABASE_URL=postgresql://...  # Automático cuando agregas PostgreSQL
PORT=...                        # Automático
RAILWAY_STATIC_URL=...         # Automático
RAILWAY_PUBLIC_DOMAIN=...      # Automático
```

---

## 📧 Variables Opcionales (Email)

Si quieres enviar emails desde la aplicación:

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password-de-aplicacion
DEFAULT_FROM_EMAIL=noreply@municipio.gov.co
```

**Para Gmail:**
1. Habilita verificación en 2 pasos
2. Genera una "Contraseña de aplicación"
3. Usa esa contraseña en `EMAIL_HOST_PASSWORD`

---

## ✅ Checklist de Variables

Antes de desplegar, verifica que tengas configuradas:

- [ ] `SECRET_KEY` (generada, única y segura)
- [ ] `DEBUG=False`
- [ ] `RAILWAY_ENVIRONMENT=production`
- [ ] `GEMINI_API_KEY` (tu API key de Google)
- [ ] PostgreSQL agregado al proyecto (Railway configura `DATABASE_URL`)

---

## 🔍 Verificar Variables

En Railway:
1. Ve a tu servicio
2. Click en "Variables"
3. Verifica que todas las variables obligatorias estén configuradas

---

## ⚠️ Importante

- **NO** subas el archivo `.env` a GitHub
- **NO** compartas tu `SECRET_KEY` o `GEMINI_API_KEY`
- Usa variables de entorno para todos los datos sensibles
- Railway encripta las variables de entorno automáticamente

---

## 🚀 Ejemplo de Configuración Completa

```bash
# Django
SECRET_KEY=django-insecure-abc123xyz789...
DEBUG=False
RAILWAY_ENVIRONMENT=production

# Gemini
GEMINI_API_KEY=AIzaSy...

# Database (automático)
DATABASE_URL=postgresql://postgres:...@...railway.app:5432/railway

# Port (automático)
PORT=8080
```

---

## 📝 Notas

- Railway reinicia el servicio automáticamente cuando cambias variables
- Los cambios en variables de entorno no requieren redeploy
- Puedes ver los valores de las variables en Railway (excepto las marcadas como secretas)
