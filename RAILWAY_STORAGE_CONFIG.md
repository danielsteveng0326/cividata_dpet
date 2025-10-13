# 🗄️ Configuración de Almacenamiento en Railway

## 📁 Problema

Railway usa **contenedores efímeros**, lo que significa que cualquier archivo guardado en el sistema de archivos se pierde cuando:
- Haces un redeploy
- El servicio se reinicia
- Railway mueve tu contenedor a otro servidor

**Archivos afectados:**
- PDFs subidos por usuarios (`archivo_pdf`)
- Respuestas firmadas (`archivo_respuesta_firmada`)
- Constancias de envío (`archivo_constancia_envio`)

---

## ✅ Solución: Railway Volumes

Railway Volumes proporciona **almacenamiento persistente** que sobrevive a redeploys y reinicios.

---

## 🚀 Configuración Paso a Paso

### **Paso 1: Crear Volume en Railway**

1. **Ve a Railway → Tu Servicio → Settings**

2. **Busca la sección "Volumes"**

3. **Click en "+ New Volume"**

4. **Configura el Volume:**
   ```
   Mount Path: /app/media
   Size: 1 GB (o más según necesites)
   ```

5. **Guarda los cambios**

Railway creará el volume y reiniciará el servicio automáticamente.

---

### **Paso 2: Verificar Configuración en Django**

El código ya está configurado correctamente:

#### **`settings.py`:**
```python
# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'  # En Railway será /app/media
```

#### **`urls.py`:**
```python
# Servir archivos media (desarrollo y producción)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

### **Paso 3: Verificar Modelos**

Los modelos ya usan `upload_to` correctamente:

```python
class Peticion(models.Model):
    archivo_pdf = models.FileField(
        upload_to='peticiones/',  # Se guardará en /app/media/peticiones/
        null=True,
        blank=True
    )
    
    archivo_respuesta_firmada = models.FileField(
        upload_to='respuestas/',  # Se guardará en /app/media/respuestas/
        null=True,
        blank=True
    )
    
    archivo_constancia_envio = models.FileField(
        upload_to='constancias/',  # Se guardará en /app/media/constancias/
        null=True,
        blank=True
    )
```

---

## 📊 Estructura de Archivos en Railway

Con el Volume configurado, los archivos se guardarán así:

```
/app/media/
├── peticiones/
│   ├── archivo1.pdf
│   ├── archivo2.pdf
│   └── ...
├── respuestas/
│   ├── respuesta1.pdf
│   ├── respuesta2.docx
│   └── ...
└── constancias/
    ├── constancia1.pdf
    ├── constancia2.jpg
    └── ...
```

---

## 🔍 Verificar que Funciona

### **1. Después de Configurar el Volume:**

1. **Sube un PDF** en una petición
2. **Verifica que se guardó:**
   - Ve a Railway → Tu Servicio → **Volumes**
   - Click en el volume
   - Deberías ver los archivos guardados

### **2. Hacer un Redeploy:**

1. **Haz un cambio** en el código y push
2. **Espera el redeploy**
3. **Verifica que los archivos siguen ahí:**
   - Accede a una petición anterior
   - El PDF debería seguir disponible

---

## 💰 Costos de Railway Volumes

| Tamaño | Costo Mensual |
|--------|---------------|
| 1 GB   | ~$0.25/mes    |
| 5 GB   | ~$1.25/mes    |
| 10 GB  | ~$2.50/mes    |

**Nota:** Los precios son aproximados. Verifica en Railway para precios exactos.

---

## 📈 Monitorear Uso del Volume

### **Ver Espacio Usado:**

1. **Railway → Tu Servicio → Volumes**
2. Verás el espacio usado vs. total

### **Limpiar Archivos Antiguos (Opcional):**

Puedes crear un comando de Django para limpiar archivos antiguos:

```python
# management/commands/limpiar_archivos_antiguos.py
from django.core.management.base import BaseCommand
from peticiones.models import Peticion
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Elimina archivos de peticiones antiguas'
    
    def handle(self, *args, **options):
        # Eliminar archivos de peticiones de más de 1 año
        fecha_limite = datetime.now() - timedelta(days=365)
        peticiones_antiguas = Peticion.objects.filter(
            fecha_radicacion__lt=fecha_limite
        )
        
        for peticion in peticiones_antiguas:
            if peticion.archivo_pdf:
                peticion.archivo_pdf.delete()
            if peticion.archivo_respuesta_firmada:
                peticion.archivo_respuesta_firmada.delete()
            if peticion.archivo_constancia_envio:
                peticion.archivo_constancia_envio.delete()
        
        self.stdout.write(f'Limpiados {peticiones_antiguas.count()} archivos')
```

---

## 🔐 Seguridad de Archivos

### **Acceso a Archivos Media:**

Los archivos en `/media/` son accesibles públicamente si conoces la URL.

**Para mayor seguridad:**

1. **Usar vistas protegidas:**

```python
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
import os

@login_required
def descargar_pdf(request, radicado):
    peticion = get_object_or_404(Peticion, radicado=radicado)
    
    # Verificar permisos (solo su dependencia)
    if peticion.dependencia != request.user.dependencia:
        return HttpResponseForbidden()
    
    # Servir archivo
    file_path = peticion.archivo_pdf.path
    return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
```

2. **Configurar URLs protegidas:**

```python
# urls.py
path('peticiones/<str:radicado>/pdf/', views.descargar_pdf, name='descargar_pdf'),
```

---

## 🔄 Alternativa: Almacenamiento en la Nube

Si necesitas más espacio o mejor rendimiento, considera:

### **Opción 1: AWS S3**

```bash
pip install django-storages boto3
```

```python
# settings.py
if RAILWAY_ENVIRONMENT:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = 'us-east-1'
```

### **Opción 2: Cloudinary**

```bash
pip install django-cloudinary-storage
```

```python
# settings.py
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': config('CLOUDINARY_API_KEY'),
    'API_SECRET': config('CLOUDINARY_API_SECRET')
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

---

## ✅ Checklist de Configuración

- [ ] Volume creado en Railway (`/app/media`)
- [ ] Tamaño del volume configurado (1GB+)
- [ ] `MEDIA_ROOT` configurado en settings
- [ ] `MEDIA_URL` configurado en settings
- [ ] URLs de media agregadas en `urls.py`
- [ ] Probado subir archivo
- [ ] Probado descargar archivo
- [ ] Verificado que archivos persisten después de redeploy

---

## 🎯 Resumen

**Para Railway Volumes:**

1. ✅ **Crear Volume** en Railway → Settings → Volumes
2. ✅ **Mount Path:** `/app/media`
3. ✅ **Size:** 1GB (o más)
4. ✅ **Código ya configurado** (no requiere cambios)
5. ✅ **Archivos persistirán** entre redeploys

**Ventajas:**
- ✅ Fácil de configurar
- ✅ Integrado con Railway
- ✅ Económico para volúmenes pequeños
- ✅ Backup automático

**Desventajas:**
- ⚠️ Limitado a un servidor (no distribuido)
- ⚠️ Puede ser más caro para grandes volúmenes

---

## 📞 Soporte

Si tienes problemas:

1. **Verifica los logs:** Railway → Deployments → View Logs
2. **Verifica el volume:** Railway → Volumes
3. **Verifica permisos:** El directorio debe ser escribible

**Error común:**
```
PermissionError: [Errno 13] Permission denied: '/app/media/peticiones/archivo.pdf'
```

**Solución:** Asegúrate de que el volume esté montado correctamente en `/app/media`.

---

**¡Con Railway Volumes configurado, tus archivos estarán seguros y persistentes!** 🎉
