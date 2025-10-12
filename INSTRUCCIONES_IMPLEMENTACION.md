# Instrucciones de Implementación - Sistema de Días Hábiles y Dependencias

## Resumen de Cambios Implementados

Se han implementado las siguientes funcionalidades en el sistema de gestión de derechos de petición:

### 1. **Sistema de Días Hábiles**
- ✅ Modelo `DiaNoHabil` para gestionar días no hábiles personalizados
- ✅ Servicio `DiasHabilesService` que calcula días hábiles considerando:
  - Sábados y domingos (NO son días hábiles)
  - Festivos fijos de Colombia (Año Nuevo, Día del Trabajo, etc.)
  - Festivos movibles según Ley Emiliani (trasladados al lunes)
  - Semana Santa (Jueves y Viernes Santo)
  - Días no hábiles personalizados (Día de la Familia, capacitaciones, etc.)

### 2. **Cálculo Automático de Vencimiento**
- ✅ Campo `fecha_vencimiento` en el modelo `Peticion`
- ✅ Cálculo automático de 15 días hábiles desde la fecha de radicación
- ✅ Dashboard actualizado mostrando "Próximas a Vencer" en lugar de "IA Procesamiento"

### 3. **Campo Dependencia en Peticiones**
- ✅ Campo `dependencia` en el modelo `Peticion`
- ✅ Asignación automática de dependencia según el usuario que carga la petición
- ✅ Jefe Jurídica (dependencia 111) puede asignar manualmente cualquier dependencia
- ✅ Jefe Jurídica puede reasignar dependencias de peticiones existentes

### 4. **Segmentación por Dependencias**
- ✅ Los usuarios solo ven peticiones de su propia dependencia
- ✅ Jefe Jurídica (dependencia 111) tiene acceso completo a todas las peticiones
- ✅ Filtros aplicados en:
  - Dashboard (vista principal)
  - Lista de peticiones
  - Estadísticas

### 5. **Calendario Interactivo**
- ✅ Vista de calendario para administradores
- ✅ Visualización de 12 meses con días hábiles/no hábiles
- ✅ Agregar días no hábiles personalizados
- ✅ Eliminar días no hábiles
- ✅ Verificación en tiempo real si una fecha es hábil

## Pasos para Aplicar los Cambios

### Paso 1: Crear las Migraciones
```bash
python manage.py makemigrations
```

Este comando creará las migraciones para:
- Nuevo modelo `DiaNoHabil`
- Campo `dependencia` en `Peticion`
- Campo `fecha_vencimiento` en `Peticion`

### Paso 2: Aplicar las Migraciones
```bash
python manage.py migrate
```

### Paso 3: Crear la Dependencia Jefe Jurídica (si no existe)
```bash
python manage.py shell
```

Luego ejecutar:
```python
from peticiones.models import Dependencia

# Crear dependencia Jefe Jurídica con prefijo 111
Dependencia.objects.get_or_create(
    prefijo='111',
    defaults={
        'nombre_oficina': 'Jefe Jurídica',
        'ciudad': 'Tu Ciudad',
        'activa': True
    }
)
```

### Paso 4: Actualizar Peticiones Existentes (Opcional)
Si ya tienes peticiones en el sistema, necesitas asignarles una dependencia y calcular su vencimiento:

```bash
python manage.py shell
```

```python
from peticiones.models import Peticion, Dependencia
from peticiones.services.dias_habiles_service import DiasHabilesService

# Obtener una dependencia por defecto
dependencia_default = Dependencia.objects.first()

# Actualizar todas las peticiones sin dependencia
for peticion in Peticion.objects.filter(dependencia__isnull=True):
    peticion.dependencia = dependencia_default
    if not peticion.fecha_vencimiento:
        peticion.fecha_vencimiento = DiasHabilesService.calcular_fecha_vencimiento(
            peticion.fecha_radicacion, 
            dias_habiles=15
        )
    peticion.save()
    print(f"Actualizada petición {peticion.radicado}")
```

### Paso 5: Cargar Festivos Nacionales de Colombia (Opcional)
Puedes pre-cargar los festivos nacionales para el año actual:

```bash
python manage.py shell
```

```python
from peticiones.models import DiaNoHabil
from datetime import date

# Festivos fijos 2025 (ejemplo)
festivos_2025 = [
    (date(2025, 1, 1), "Año Nuevo"),
    (date(2025, 1, 6), "Día de los Reyes Magos"),
    (date(2025, 3, 24), "Día de San José"),
    (date(2025, 4, 17), "Jueves Santo"),
    (date(2025, 4, 18), "Viernes Santo"),
    (date(2025, 5, 1), "Día del Trabajo"),
    (date(2025, 6, 23), "Sagrado Corazón"),
    (date(2025, 6, 30), "San Pedro y San Pablo"),
    (date(2025, 7, 20), "Día de la Independencia"),
    (date(2025, 8, 7), "Batalla de Boyacá"),
    (date(2025, 8, 18), "Asunción de la Virgen"),
    (date(2025, 10, 13), "Día de la Raza"),
    (date(2025, 11, 3), "Día de Todos los Santos"),
    (date(2025, 11, 17), "Independencia de Cartagena"),
    (date(2025, 12, 8), "Día de la Inmaculada Concepción"),
    (date(2025, 12, 25), "Navidad"),
]

for fecha, descripcion in festivos_2025:
    DiaNoHabil.objects.get_or_create(
        fecha=fecha,
        defaults={
            'descripcion': descripcion,
            'es_festivo_nacional': True
        }
    )
    print(f"Agregado: {descripcion}")
```

## Uso del Sistema

### Para Usuarios Normales:
1. Al crear una petición, se asigna automáticamente a su dependencia
2. Solo pueden ver peticiones de su propia dependencia
3. El sistema calcula automáticamente la fecha de vencimiento (15 días hábiles)

### Para Jefe Jurídica (Dependencia 111):
1. Al crear una petición, puede seleccionar manualmente la dependencia responsable
2. Puede ver TODAS las peticiones de todas las dependencias
3. Puede reasignar dependencias (funcionalidad a implementar en el detalle)

### Para Administradores:
1. Acceder a "Días No Hábiles" en el menú de administración
2. Ver el calendario interactivo del año
3. Agregar días no hábiles personalizados (Día de la Familia, capacitaciones, etc.)
4. Los días se marcan automáticamente como no hábiles en el cálculo de vencimientos

## Archivos Modificados/Creados

### Modelos:
- ✅ `peticiones/models.py` - Agregado modelo `DiaNoHabil` y campos en `Peticion`

### Servicios:
- ✅ `peticiones/services/dias_habiles_service.py` - Nuevo servicio para cálculo de días hábiles

### Vistas:
- ✅ `peticiones/views.py` - Actualizado con filtros por dependencia
- ✅ `peticiones/auth_views.py` - Agregadas vistas para calendario

### Formularios:
- ✅ `peticiones/forms.py` - Actualizado con lógica condicional para dependencias

### Templates:
- ✅ `templates/peticiones/index.html` - Card de vencimiento
- ✅ `templates/auth/calendario_dias_no_habiles.html` - Nuevo calendario interactivo
- ✅ `templates/base.html` - Agregado enlace al calendario

### URLs:
- ✅ `peticiones/urls.py` - Agregadas rutas para gestión de días no hábiles

### Admin:
- ✅ `peticiones/admin.py` - Registrado modelo `DiaNoHabil`

## Verificación del Sistema

### 1. Verificar Cálculo de Días Hábiles:
```python
from peticiones.services.dias_habiles_service import DiasHabilesService
from datetime import date

# Verificar si una fecha es hábil
fecha = date(2025, 1, 1)  # Año Nuevo
print(DiasHabilesService.es_dia_habil(fecha))  # Debe ser False

# Calcular vencimiento
fecha_inicio = date(2025, 10, 11)
fecha_vencimiento = DiasHabilesService.calcular_fecha_vencimiento(fecha_inicio, 15)
print(f"Vencimiento: {fecha_vencimiento}")
```

### 2. Verificar Permisos por Dependencia:
- Iniciar sesión con un usuario normal → Solo debe ver peticiones de su dependencia
- Iniciar sesión con Jefe Jurídica (dep. 111) → Debe ver todas las peticiones

### 3. Verificar Calendario:
- Acceder a `/calendario-dias-no-habiles/`
- Verificar que muestra los 12 meses
- Agregar un día no hábil personalizado
- Verificar que se refleja en el calendario

## Notas Importantes

1. **Dependencia 111**: Es crucial que exista la dependencia con prefijo "111" para el Jefe Jurídica
2. **Días Hábiles**: El sistema ya incluye sábados, domingos y festivos nacionales automáticamente
3. **Vencimientos**: Se calculan automáticamente al crear una petición
4. **Seguridad**: Los filtros por dependencia están implementados a nivel de backend

## Soporte

Si encuentras algún problema:
1. Verificar que las migraciones se aplicaron correctamente
2. Verificar que existe la dependencia 111
3. Revisar los logs de Django para errores
4. Verificar permisos de usuario (is_staff para acceder al calendario)
