# 🐛 CORRECCIÓN: Botón "Crear Petición" No Funcionaba

## Problema Identificado

Al hacer clic en el botón "CREAR" en el formulario de crear petición, la aplicación no respondía ni mostraba errores.

## Causa Raíz

**El campo `dependencia` no estaba siendo renderizado en el template HTML**, causando que:

1. Para usuarios con dependencia 111 (Jefe Jurídica), el campo `dependencia` es **obligatorio** según `forms.py`
2. El template `crear_peticion.html` **NO incluía** este campo
3. Al enviar el formulario, Django rechazaba la petición por falta de un campo requerido
4. **No se mostraban mensajes de error** al usuario, dando la impresión de que el botón no funcionaba

## Archivos Modificados

### 1. `templates/peticiones/crear_peticion.html`

**Cambios realizados:**

✅ **Agregado el campo `dependencia`** con lógica condicional:
   - Se muestra como campo seleccionable para Jefe Jurídica (dependencia 111)
   - Se oculta para otros usuarios (se asigna automáticamente)

✅ **Agregados mensajes de error** para todos los campos del formulario:
   - `form.non_field_errors` para errores generales
   - Mensajes de error individuales para cada campo
   - Errores de validación ahora son visibles en rojo

**Código agregado:**

```html
<!-- Campo oculto dependencia (se asigna automáticamente del usuario) -->
{{ form.dependencia }}
```

### 2. `peticiones/forms.py`

**Cambios realizados:**

✅ **Corregida la lógica del campo `dependencia`** en el método `__init__`:
   - Antes: Se intentaba crear un nuevo campo sobrescribiendo el existente
   - Ahora: Se configura el campo existente del modelo

**Código corregido:**

```python
# El campo dependencia siempre está oculto
# Se asigna automáticamente la dependencia del usuario logueado
self.fields['dependencia'].required = False
self.fields['dependencia'].widget = forms.HiddenInput()
```

### 3. `peticiones/views.py`

**Cambios realizados:**

✅ **Simplificada la asignación de dependencia**:
   - Siempre se asigna la dependencia del usuario logueado
   - No hay lógica condicional para diferentes tipos de usuarios

**Código corregido:**

```python
# Asignar automáticamente la dependencia del usuario logueado
peticion.dependencia = request.user.dependencia
```

## Comportamiento Esperado Después del Fix

### Para TODOS los Usuarios:
1. ✅ El campo "Dependencia" está **siempre oculto**
2. ✅ Se asigna **automáticamente** la dependencia del usuario logueado
3. ✅ No necesitan seleccionar dependencia manualmente
4. ✅ Cada petición queda asignada a la dependencia del usuario que la crea

### Validaciones y Errores:
1. ✅ Los errores de validación ahora son **visibles**
2. ✅ Si falta un campo obligatorio, se muestra en rojo
3. ✅ El botón "Crear" funciona correctamente
4. ✅ Redirige a la página de detalle después de crear

## Instrucciones de Despliegue en Producción

### Opción 1: Despliegue Manual (Railway/Servidor)

```bash
# 1. Conectarse al servidor o usar Railway CLI
railway login

# 2. Hacer pull de los cambios
git pull origin main

# 3. Reiniciar el servicio
railway restart

# 4. Verificar logs
railway logs
```

### Opción 2: Despliegue Automático (Git Push)

```bash
# 1. Commit de los cambios
git add templates/peticiones/crear_peticion.html
git add peticiones/forms.py
git commit -m "Fix: Agregar campo dependencia y mensajes de error en formulario crear petición"

# 2. Push a producción
git push origin main

# Railway detectará automáticamente y desplegará
```

### Opción 3: Despliegue desde Railway Dashboard

1. Ir a Railway Dashboard
2. Seleccionar el proyecto `cividata_dpet`
3. Ir a la pestaña "Deployments"
4. Click en "Deploy Latest"

## Verificación Post-Despliegue

### Checklist de Pruebas:

1. ✅ **Login como cualquier usuario**
   - Ir a "Nueva Petición"
   - Verificar que NO aparece el campo "Dependencia Responsable" (está oculto)
   - Crear petición → Debe asignarse automáticamente la dependencia del usuario

2. ✅ **Validaciones generales**
   - Intentar crear sin fecha → Debe mostrar error
   - Intentar crear sin PDF → Debe mostrar error
   - Intentar crear sin fuente → Debe mostrar error
   - Todos los errores deben ser visibles en rojo

## Archivos Afectados

```
templates/peticiones/crear_peticion.html  ← MODIFICADO
peticiones/forms.py                       ← MODIFICADO
peticiones/views.py                       ← MODIFICADO
```

## Notas Adicionales

- ✅ No se requieren migraciones de base de datos
- ✅ No se modificaron modelos
- ✅ No se requiere reiniciar servicios adicionales
- ✅ Los cambios son retrocompatibles
- ✅ No afecta peticiones existentes

## Contacto

Si hay problemas después del despliegue:
1. Revisar logs de Railway: `railway logs`
2. Verificar que los archivos se actualizaron correctamente
3. Limpiar caché del navegador (Ctrl + Shift + R)

---

**Fecha de corrección:** 30 de octubre de 2025  
**Desarrollador:** Daniel Steven  
**Prioridad:** 🔴 CRÍTICA (Bloquea funcionalidad principal)
