# 🔐 Credenciales de Administrador

## Superuser del Sistema

El sistema crea automáticamente un superuser durante el deployment con las siguientes credenciales:

---

### 📋 Credenciales de Acceso

```
Usuario (Cédula): 1020458606
Contraseña:       cidoli2025
```

---

### 👤 Información del Usuario

- **Nombre Completo:** Administrador del Sistema
- **Email:** admin@municipio.gov.co
- **Cargo:** Administrador
- **Dependencia:** Jefe Jurídica (111)
- **Permisos:** Superuser (acceso total)

---

### 🔑 Permisos del Superuser

Este usuario tiene **acceso completo** a:

✅ **Panel de Administración Django** (`/admin/`)
✅ **Gestión de Usuarios** - Crear, editar, eliminar usuarios
✅ **Gestión de Dependencias** - Crear y administrar dependencias
✅ **Gestión de Días No Hábiles** - Configurar calendario
✅ **Ver TODAS las Peticiones** - De todas las dependencias
✅ **Crear y Responder Peticiones** - Sin restricciones
✅ **Acceso al Asistente IA** - Generar respuestas automáticas

---

### 🌐 URLs de Acceso

#### Desarrollo Local:
```
Login:     http://127.0.0.1:8000/login/
Dashboard: http://127.0.0.1:8000/
Admin:     http://127.0.0.1:8000/admin/
```

#### Producción (Railway):
```
Login:     https://tu-proyecto.railway.app/login/
Dashboard: https://tu-proyecto.railway.app/
Admin:     https://tu-proyecto.railway.app/admin/
```

---

### 🚀 Primer Acceso

1. **Accede al sistema:**
   - Ve a la URL de login
   - Ingresa cédula: `1020458606`
   - Ingresa contraseña: `cidoli2025`

2. **Cambia la contraseña:**
   - Una vez dentro, ve a tu perfil
   - Haz clic en "Cambiar Contraseña"
   - Ingresa una contraseña segura nueva

3. **Configura el sistema:**
   - Ve a "Dependencias" y crea las dependencias necesarias
   - Ve a "Usuarios" y crea usuarios para cada dependencia
   - Ve a "Días No Hábiles" y configura días personalizados

---

### ⚠️ IMPORTANTE - Seguridad

#### En Desarrollo Local:
- ✅ Puedes usar la contraseña por defecto
- ✅ No hay problema de seguridad

#### En Producción (Railway):
- 🔴 **CAMBIA LA CONTRASEÑA INMEDIATAMENTE** después del primer login
- 🔴 Usa una contraseña fuerte (mínimo 12 caracteres)
- 🔴 No compartas estas credenciales
- 🔴 Considera usar autenticación de dos factores

---

### 🔄 Creación Automática

El superuser se crea automáticamente en los siguientes casos:

1. **Deployment en Railway:**
   - Se ejecuta `create_superuser.py` después de las migraciones
   - Si el usuario ya existe, no lo vuelve a crear

2. **Inicialización Local:**
   - Ejecuta: `python inicializar_sistema.py`
   - Crea el superuser junto con datos iniciales

3. **Manual:**
   - Ejecuta: `python create_superuser.py`
   - Solo crea el superuser

---

### 🛠️ Recuperación de Acceso

Si olvidas la contraseña, puedes restablecerla:

#### Opción 1: Desde Railway Terminal
```bash
python manage.py shell
```

```python
from peticiones.models import Usuario
user = Usuario.objects.get(cedula='1020458606')
user.set_password('nueva_contraseña_segura')
user.save()
print("Contraseña actualizada")
```

#### Opción 2: Crear nuevo superuser
```bash
python manage.py createsuperuser
```

---

### 📝 Notas Adicionales

- El superuser pertenece a la dependencia "Jefe Jurídica (111)"
- Tiene acceso a TODAS las funcionalidades del sistema
- Es el único usuario que puede acceder al Admin de Django
- Puede ver y gestionar peticiones de todas las dependencias
- Puede crear y gestionar otros usuarios

---

### 🔒 Recomendaciones de Seguridad

1. **Contraseña Fuerte:**
   - Mínimo 12 caracteres
   - Incluye mayúsculas, minúsculas, números y símbolos
   - No uses información personal

2. **Acceso Restringido:**
   - No compartas las credenciales
   - Crea usuarios individuales para cada persona
   - Usa el superuser solo para administración

3. **Auditoría:**
   - Revisa regularmente los logs de acceso
   - Monitorea cambios en usuarios y permisos
   - Mantén un registro de acciones administrativas

4. **Backup:**
   - Guarda estas credenciales en un lugar seguro
   - Considera usar un gestor de contraseñas
   - Mantén un backup de la base de datos

---

## ✅ Verificación

Para verificar que el superuser fue creado correctamente:

```bash
python manage.py shell
```

```python
from peticiones.models import Usuario

# Verificar que existe
user = Usuario.objects.get(cedula='1020458606')
print(f"Usuario: {user.nombre_completo}")
print(f"Email: {user.email}")
print(f"Es superuser: {user.is_superuser}")
print(f"Es staff: {user.is_staff}")
print(f"Dependencia: {user.dependencia}")
```

Deberías ver:
```
Usuario: Administrador del Sistema
Email: admin@municipio.gov.co
Es superuser: True
Es staff: True
Dependencia: Jefe Jurídica (111)
```

---

**¡El sistema está listo para usar!** 🎉
