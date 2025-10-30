# 🔒 SEGURIDAD: Control de Permisos por Dependencia

## Regla de Negocio Implementada

**Oficina Jurídica (Prefijo 111):**
- ✅ Puede ver **TODAS** las peticiones del sistema
- ✅ Tiene acceso completo al universo de peticiones
- ✅ Puede gestionar peticiones de cualquier dependencia

**Otras Dependencias:**
- ✅ Solo pueden ver **SUS PROPIAS** peticiones
- ❌ NO pueden acceder a peticiones de otras dependencias
- ✅ Cada oficina trabaja de forma aislada

## Función de Validación Implementada

Se creó la función auxiliar `puede_ver_peticion()` en `views.py`:

```python
def puede_ver_peticion(user, peticion):
    """
    Verifica si un usuario puede ver una petición específica.
    - Oficina Jurídica (prefijo 111) puede ver TODAS las peticiones
    - Superuser puede ver TODAS las peticiones
    - Otras dependencias solo pueden ver sus propias peticiones
    """
    # Oficina Jurídica o superuser pueden ver todo
    if (user.dependencia and user.dependencia.prefijo == '111') or \
       (user.cedula == '1020458606' and user.is_superuser):
        return True
    
    # Otras dependencias solo ven sus propias peticiones
    return peticion.dependencia == user.dependencia
```

## Vistas Protegidas

### ✅ Vistas con Filtrado Automático (QuerySet)

Estas vistas filtran automáticamente las peticiones según la dependencia:

1. **`index()`** - Dashboard principal
   - Filtra estadísticas por dependencia
   - Oficina Jurídica ve todas, otras solo las suyas

2. **`ListaPeticiones`** - Lista de peticiones
   - Filtra el queryset según dependencia
   - Aplica filtros de búsqueda solo sobre peticiones permitidas

### ✅ Vistas con Validación Individual

Estas vistas validan el acceso a cada petición específica usando `puede_ver_peticion()`:

#### Gestión de Peticiones:
1. **`detalle_peticion()`** - Ver detalle de petición
2. **`reprocesar_peticion()`** - Reprocesar con IA
3. **`cambiar_estado_peticion()`** - Marcar como respondida
4. **`editar_peticionario()`** - Editar datos del peticionario
5. **`obtener_datos_peticionario()`** - AJAX para obtener datos

#### Asistente IA:
6. **`iniciar_asistente_respuesta()`** - Iniciar asistente IA
7. **`mostrar_asistente_respuesta()`** - Mostrar interfaz asistente
8. **`procesar_respuestas_asistente()`** - Procesar respuestas
9. **`historial_asistente()`** - Ver historial
10. **`descargar_respuesta_word()`** - Descargar documento Word

## Comportamiento de Seguridad

### Intento de Acceso No Autorizado:

**Vistas HTML (render):**
```python
if not puede_ver_peticion(request.user, peticion):
    messages.error(request, 'No tienes permiso para ver esta petición.')
    return redirect('index')
```
- Muestra mensaje de error
- Redirige al dashboard

**Vistas AJAX (JSON):**
```python
if not puede_ver_peticion(request.user, peticion):
    return JsonResponse({'success': False, 'message': 'No tienes permiso para esta acción'})
```
- Retorna error JSON
- No expone información sensible

## Escenarios de Prueba

### ✅ Escenario 1: Usuario de Oficina Jurídica (111)
```
Usuario: Jefe Jurídica (dependencia 111)
Acción: Ver petición de Secretaría de Salud
Resultado: ✅ PERMITIDO - Puede ver todas las peticiones
```

### ✅ Escenario 2: Usuario de Otra Dependencia
```
Usuario: Secretaría de Salud (dependencia 200)
Acción: Ver petición de Secretaría de Salud
Resultado: ✅ PERMITIDO - Es su propia dependencia
```

### ❌ Escenario 3: Acceso No Autorizado
```
Usuario: Secretaría de Salud (dependencia 200)
Acción: Ver petición de Secretaría de Educación (dependencia 300)
Resultado: ❌ DENEGADO - No puede ver peticiones de otras dependencias
```

### ✅ Escenario 4: Superusuario
```
Usuario: Superusuario (cedula 1020458606)
Acción: Ver cualquier petición
Resultado: ✅ PERMITIDO - Superusuario tiene acceso total
```

## Verificación en Producción

### Checklist de Seguridad:

1. **Login como usuario de Oficina Jurídica (111)**
   - ✅ Debe ver todas las peticiones en el dashboard
   - ✅ Debe ver todas las peticiones en la lista
   - ✅ Debe poder acceder a cualquier detalle de petición

2. **Login como usuario de otra dependencia (ej: 200)**
   - ✅ Debe ver solo peticiones de su dependencia en dashboard
   - ✅ Debe ver solo peticiones de su dependencia en lista
   - ✅ Debe poder acceder a detalles de sus peticiones
   - ❌ NO debe poder acceder a peticiones de otras dependencias

3. **Intento de acceso directo por URL**
   ```
   Usuario: Dependencia 200
   URL: /peticion/dpet2025103000001/  (petición de dependencia 300)
   Resultado esperado: Mensaje de error + redirección
   ```

4. **Intento de acceso AJAX**
   ```
   Usuario: Dependencia 200
   AJAX: POST /peticion/dpet2025103000001/reprocesar/
   Resultado esperado: {"success": false, "message": "No tienes permiso..."}
   ```

## Archivos Modificados

```
peticiones/views.py  ← MODIFICADO
  - Agregada función puede_ver_peticion()
  - Agregado @login_required a todas las vistas
  - Agregada validación de permisos en 10 vistas
```

## Beneficios de Seguridad

✅ **Aislamiento de Datos:**
- Cada dependencia solo ve sus propias peticiones
- Previene fuga de información entre dependencias

✅ **Control Centralizado:**
- Oficina Jurídica puede supervisar todo el sistema
- Facilita auditorías y seguimiento

✅ **Prevención de Acceso No Autorizado:**
- Validación en todas las vistas
- Protección contra acceso directo por URL
- Protección en llamadas AJAX

✅ **Mensajes Claros:**
- Usuario sabe por qué no puede acceder
- No expone información sensible

## Notas Técnicas

### Rendimiento:
- La función `puede_ver_peticion()` es muy eficiente
- Solo hace comparaciones simples (no consultas DB adicionales)
- El objeto `peticion` ya está cargado por `get_object_or_404()`

### Mantenibilidad:
- Lógica centralizada en una función
- Fácil de modificar si cambian las reglas de negocio
- Código DRY (Don't Repeat Yourself)

### Escalabilidad:
- Si se agregan más roles, solo se modifica `puede_ver_peticion()`
- No hay que tocar cada vista individual

## Recomendaciones Futuras

1. **Logging de Intentos de Acceso:**
   ```python
   if not puede_ver_peticion(request.user, peticion):
       logger.warning(f"Intento de acceso no autorizado: {request.user.cedula} -> {radicado}")
   ```

2. **Decorador Personalizado:**
   ```python
   @require_peticion_access
   def detalle_peticion(request, radicado):
       # La validación se hace automáticamente
   ```

3. **Permisos Granulares:**
   - Agregar permisos de solo lectura vs edición
   - Implementar roles adicionales (supervisor, auditor, etc.)

---

**Fecha de implementación:** 30 de octubre de 2025  
**Desarrollador:** Daniel Steven  
**Prioridad:** 🔴 CRÍTICA (Seguridad de datos)  
**Estado:** ✅ IMPLEMENTADO Y PROBADO
