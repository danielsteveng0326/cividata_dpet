#!/usr/bin/env python
"""
Script para inicializar el sistema con datos básicos:
- Crear dependencia Jefe Jurídica (111)
- Cargar festivos nacionales de Colombia para 2025
- Actualizar peticiones existentes con dependencia y vencimiento
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'municipio_ia.settings')
django.setup()

from peticiones.models import Dependencia, DiaNoHabil, Peticion
from peticiones.services.dias_habiles_service import DiasHabilesService
from datetime import date

def crear_dependencia_jefe_juridica():
    """Crear la dependencia Jefe Jurídica con prefijo 111"""
    print("\n=== Creando Dependencia Jefe Jurídica ===")
    
    dependencia, created = Dependencia.objects.get_or_create(
        prefijo='111',
        defaults={
            'nombre_oficina': 'Jefe Jurídica',
            'ciudad': 'El Carmen de Bolívar',
            'activa': True
        }
    )
    
    if created:
        print(f"✓ Dependencia creada: {dependencia}")
    else:
        print(f"✓ Dependencia ya existe: {dependencia}")
    
    return dependencia


def cargar_festivos_2025():
    """Cargar festivos nacionales de Colombia para 2025"""
    print("\n=== Cargando Festivos Nacionales 2025 ===")
    
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
    
    contador = 0
    for fecha, descripcion in festivos_2025:
        dia, created = DiaNoHabil.objects.get_or_create(
            fecha=fecha,
            defaults={
                'descripcion': descripcion,
                'es_festivo_nacional': True
            }
        )
        
        if created:
            print(f"✓ Agregado: {descripcion} - {fecha.strftime('%d/%m/%Y')}")
            contador += 1
        else:
            print(f"  Ya existe: {descripcion} - {fecha.strftime('%d/%m/%Y')}")
    
    print(f"\n✓ Total festivos agregados: {contador}")


def actualizar_peticiones_existentes():
    """Actualizar peticiones existentes con dependencia y vencimiento"""
    print("\n=== Actualizando Peticiones Existentes ===")
    
    # Obtener dependencia por defecto
    dependencia_default = Dependencia.objects.first()
    
    if not dependencia_default:
        print("⚠ No hay dependencias en el sistema. Crea al menos una dependencia primero.")
        return
    
    # Contar peticiones sin dependencia
    peticiones_sin_dep = Peticion.objects.filter(dependencia__isnull=True).count()
    peticiones_sin_venc = Peticion.objects.filter(fecha_vencimiento__isnull=True).count()
    
    print(f"Peticiones sin dependencia: {peticiones_sin_dep}")
    print(f"Peticiones sin vencimiento: {peticiones_sin_venc}")
    
    if peticiones_sin_dep == 0 and peticiones_sin_venc == 0:
        print("✓ Todas las peticiones ya tienen dependencia y vencimiento")
        return
    
    # Actualizar peticiones
    contador = 0
    for peticion in Peticion.objects.all():
        actualizado = False
        
        if not peticion.dependencia:
            peticion.dependencia = dependencia_default
            actualizado = True
        
        if not peticion.fecha_vencimiento and peticion.fecha_radicacion:
            peticion.fecha_vencimiento = DiasHabilesService.calcular_fecha_vencimiento(
                peticion.fecha_radicacion, 
                dias_habiles=15
            )
            actualizado = True
        
        if actualizado:
            peticion.save()
            print(f"✓ Actualizada: {peticion.radicado} - Vence: {peticion.fecha_vencimiento}")
            contador += 1
    
    print(f"\n✓ Total peticiones actualizadas: {contador}")


def mostrar_estadisticas():
    """Mostrar estadísticas del sistema"""
    print("\n=== Estadísticas del Sistema ===")
    
    total_dependencias = Dependencia.objects.count()
    total_peticiones = Peticion.objects.count()
    total_dias_no_habiles = DiaNoHabil.objects.filter(activo=True).count()
    
    print(f"Dependencias: {total_dependencias}")
    print(f"Peticiones: {total_peticiones}")
    print(f"Días no hábiles registrados: {total_dias_no_habiles}")
    
    # Verificar Jefe Jurídica
    jefe_juridica = Dependencia.objects.filter(prefijo='111').first()
    if jefe_juridica:
        usuarios_juridica = jefe_juridica.usuarios.count()
        peticiones_juridica = jefe_juridica.peticiones.count()
        print(f"\nJefe Jurídica (111):")
        print(f"  - Usuarios: {usuarios_juridica}")
        print(f"  - Peticiones: {peticiones_juridica}")


def main():
    """Función principal"""
    print("=" * 60)
    print("INICIALIZACIÓN DEL SISTEMA DE DÍAS HÁBILES Y DEPENDENCIAS")
    print("=" * 60)
    
    try:
        # 1. Crear dependencia Jefe Jurídica
        crear_dependencia_jefe_juridica()
        
        # 2. Cargar festivos nacionales
        cargar_festivos_2025()
        
        # 3. Actualizar peticiones existentes
        actualizar_peticiones_existentes()
        
        # 4. Mostrar estadísticas
        mostrar_estadisticas()
        
        print("\n" + "=" * 60)
        print("✓ INICIALIZACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print("\nPróximos pasos:")
        print("1. Accede al sistema como administrador")
        print("2. Ve a 'Días No Hábiles' para agregar días personalizados")
        print("3. Asigna usuarios a la dependencia Jefe Jurídica (111)")
        print("4. Crea nuevas peticiones para probar el sistema")
        
    except Exception as e:
        print(f"\n❌ Error durante la inicialización: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
