#!/usr/bin/env python
"""
Script para crear el superuser automáticamente en Railway
Se ejecuta después de las migraciones
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'municipio_ia.settings')
django.setup()

from peticiones.models import Usuario, Dependencia

def create_superuser():
    """Crea el superuser si no existe"""
    
    cedula = '1020458606'
    
    print("=" * 60)
    print("🚀 INICIANDO CREACIÓN DE SUPERUSER")
    print("=" * 60)
    
    try:
        # Verificar si el usuario ya existe
        if Usuario.objects.filter(cedula=cedula).exists():
            print(f"✅ El superuser con cédula {cedula} ya existe.")
            user = Usuario.objects.get(cedula=cedula)
            print(f"   Nombre: {user.nombre_completo}")
            print(f"   Email: {user.email}")
            print(f"   Is superuser: {user.is_superuser}")
            print(f"   Is staff: {user.is_staff}")
            return user
        
        print(f"📝 Creando superuser con cédula: {cedula}")
        
        # Crear o obtener la dependencia Jefe Jurídica (111)
        print("📂 Verificando dependencia Jefe Jurídica (111)...")
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
        print("👤 Creando usuario superuser...")
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
        print(f"❌ ERROR AL CREAR SUPERUSER: {str(e)}")
        import traceback
        traceback.print_exc()
        # No lanzar excepción para que el deploy continúe
        return None

if __name__ == '__main__':
    result = create_superuser()
    if result:
        print("✅ Proceso completado exitosamente.")
        sys.exit(0)
    else:
        print("⚠️  Proceso completado con advertencias.")
        sys.exit(0)  # Exit 0 para que no falle el deploy
