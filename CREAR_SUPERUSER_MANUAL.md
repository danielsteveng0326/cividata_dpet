# 🔧 Crear Superuser Manualmente en Railway

Si el script automático no creó el superuser, puedes crearlo manualmente desde Railway.

---

## 🚀 Método 1: Usar el Script Manual (Recomendado)

### Paso 1: Abrir Railway Terminal

1. Ve a Railway → Tu Proyecto → Tu Servicio
2. Haz clic en **"Settings"**
3. Busca la sección **"Service"**
4. Haz clic en **"Open Terminal"** o **"Shell"**

### Paso 2: Ejecutar el Script

```bash
python crear_admin_manual.py
```

El script:
- Verificará si el usuario ya existe
- Creará la dependencia Jefe Jurídica si no existe
- Creará el superuser con las credenciales predefinidas

### Credenciales:
```
Usuario (Cédula): 1020458606
Contraseña:       cidoli2025
```

---

## 🛠️ Método 2: Usar Django Shell

### Paso 1: Abrir Django Shell

Desde Railway Terminal:

```bash
python manage.py shell
```

### Paso 2: Ejecutar el Código

Copia y pega este código completo:

```python
from peticiones.models import Usuario, Dependencia

# Crear dependencia Jefe Jurídica
dependencia, created = Dependencia.objects.get_or_create(
    prefijo='111',
    defaults={
        'nombre_oficina': 'Jefe Jurídica',
        'activa': True
    }
)

if created:
    print("✅ Dependencia creada")
else:
    print("✅ Dependencia ya existe")

# Verificar si el usuario ya existe
cedula = '1020458606'
if Usuario.objects.filter(cedula=cedula).exists():
    print(f"⚠️  Usuario con cédula {cedula} ya existe")
    user = Usuario.objects.get(cedula=cedula)
    print(f"Nombre: {user.nombre_completo}")
    print(f"Es superuser: {user.is_superuser}")
else:
    # Crear superuser
    user = Usuario.objects.create_superuser(
        cedula='1020458606',
        nombre_completo='Administrador del Sistema',
        email='admin@municipio.gov.co',
        cargo='Administrador',
        password='cidoli2025',
        dependencia=dependencia
    )
    
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()
    
    print("✅ Superuser creado exitosamente!")
    print(f"Usuario: {user.cedula}")
    print(f"Contraseña: cidoli2025")
```

### Paso 3: Salir del Shell

```python
exit()
```

---

## 🔍 Método 3: Usar Django createsuperuser

### Paso 1: Ejecutar el Comando

Desde Railway Terminal:

```bash
python manage.py createsuperuser
```

### Paso 2: Ingresar los Datos

El comando te pedirá:

```
Cédula: 1020458606
Nombre completo: Administrador del Sistema
Email: admin@municipio.gov.co
Cargo: Administrador
Password: cidoli2025
Password (again): cidoli2025
```

**Nota:** Necesitas seleccionar una dependencia. Primero crea la dependencia Jefe Jurídica (111) si no existe.

---

## ✅ Verificar que el Superuser fue Creado

### Desde Django Shell:

```bash
python manage.py shell
```

```python
from peticiones.models import Usuario

# Buscar el usuario
user = Usuario.objects.get(cedula='1020458606')

# Verificar datos
print(f"Nombre: {user.nombre_completo}")
print(f"Email: {user.email}")
print(f"Es superuser: {user.is_superuser}")
print(f"Es staff: {user.is_staff}")
print(f"Activo: {user.is_active}")
print(f"Dependencia: {user.dependencia}")

exit()
```

Deberías ver:
```
Nombre: Administrador del Sistema
Email: admin@municipio.gov.co
Es superuser: True
Es staff: True
Activo: True
Dependencia: Jefe Jurídica (111)
```

---

## 🌐 Probar el Login

Una vez creado el superuser:

1. Ve a: `https://tu-proyecto.railway.app/login/`
2. Ingresa:
   - **Usuario:** 1020458606
   - **Contraseña:** cidoli2025
3. Deberías poder acceder al sistema

---

## 🔄 Si el Usuario Ya Existe pero No es Superuser

Si el usuario existe pero no tiene permisos de superuser:

```bash
python manage.py shell
```

```python
from peticiones.models import Usuario

user = Usuario.objects.get(cedula='1020458606')
user.is_superuser = True
user.is_staff = True
user.is_active = True
user.set_password('cidoli2025')  # Restablecer contraseña
user.save()

print("✅ Usuario actualizado a superuser")
exit()
```

---

## 📝 Crear Dependencia Jefe Jurídica (si no existe)

Si necesitas crear la dependencia primero:

```bash
python manage.py shell
```

```python
from peticiones.models import Dependencia

dependencia = Dependencia.objects.create(
    prefijo='111',
    nombre_oficina='Jefe Jurídica',
    activa=True
)

print(f"✅ Dependencia creada: {dependencia}")
exit()
```

---

## 🚨 Solución de Problemas

### Error: "No module named 'peticiones'"

**Solución:** Asegúrate de estar en el directorio correcto:

```bash
cd /app
python manage.py shell
```

### Error: "Dependencia matching query does not exist"

**Solución:** Primero crea la dependencia Jefe Jurídica (ver sección anterior).

### Error: "UNIQUE constraint failed"

**Solución:** El usuario ya existe. Usa el método para actualizar el usuario existente.

---

## 📞 Ayuda Adicional

Si ninguno de estos métodos funciona:

1. Verifica que las migraciones se ejecutaron correctamente
2. Revisa los logs de Railway para errores
3. Asegúrate de que PostgreSQL esté conectado
4. Verifica las variables de entorno

---

## ✅ Resumen de Comandos Rápidos

```bash
# Método más rápido - Script manual
python crear_admin_manual.py

# Alternativa - Django Shell
python manage.py shell
# Luego pega el código de creación

# Verificar usuario
python manage.py shell
from peticiones.models import Usuario
Usuario.objects.get(cedula='1020458606')
```

---

**Una vez creado el superuser, podrás acceder con:**
- Usuario: `1020458606`
- Contraseña: `cidoli2025`

**⚠️ Recuerda cambiar la contraseña después del primer login!**
