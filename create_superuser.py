#!/usr/bin/env python
"""
Script para crear el superuser automáticamente en Railway
Se ejecuta después de las migraciones
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'municipio_ia.settings')
django.setup()

from peticiones.models import Usuario, Dependencia

def create_superuser():
    """Crea el superuser si no existe"""
    
    cedula = '1020458606'
    
    # Verificar si el usuario ya existe
    if Usuario.objects.filter(cedula=cedula).exists():
        print(f"✅ El superuser con cédula {cedula} ya existe.")
        return
    
    # Crear o obtener la dependencia Jefe Jurídica (111)
    dependencia_jefe, created = Dependencia.objects.get_or_create(
        prefijo='111',
        defaults={
            'nombre_oficina': 'Jefe Jurídica',
            'activa': True
        }
    )
    
    if created:
        print(f"✅ Dependencia 'Jefe Jurídica' (111) creada.")
    else:
        print(f"✅ Dependencia 'Jefe Jurídica' (111) ya existe.")
    
    # Crear el superuser
    try:
        superuser = Usuario.objects.create_superuser(
            cedula=cedula,
            nombre_completo='Administrador del Sistema',
            email='admin@municipio.gov.co',
            cargo='Administrador',
            password='cidoli2025',
            dependencia=dependencia_jefe
        )
        
        # Asegurar que tenga todos los permisos
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.is_active = True
        superuser.save()
        
        print(f"""
╔═══════════════════════════════════════════════════════════╗
║          ✅ SUPERUSER CREADO EXITOSAMENTE                ║
╠═══════════════════════════════════════════════════════════╣
║  Cédula:    {cedula}                              ║
║  Nombre:    Administrador del Sistema                     ║
║  Email:     admin@municipio.gov.co                        ║
║  Password:  cidoli2025                                    ║
║  Cargo:     Administrador                                 ║
║  Dependencia: Jefe Jurídica (111)                         ║
╠═══════════════════════════════════════════════════════════╣
║  ⚠️  IMPORTANTE: Cambia la contraseña después del        ║
║     primer login por seguridad                            ║
╚═══════════════════════════════════════════════════════════╝
        """)
        
        return superuser
        
    except Exception as e:
        print(f"❌ Error al crear superuser: {str(e)}")
        raise

if __name__ == '__main__':
    print("🚀 Iniciando creación de superuser...")
    create_superuser()
    print("✅ Proceso completado.")
