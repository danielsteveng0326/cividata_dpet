#!/usr/bin/env python
"""
Script manual para crear el superuser desde Railway Terminal
Ejecuta: python crear_admin_manual.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'municipio_ia.settings')
django.setup()

from peticiones.models import Usuario, Dependencia

print("=" * 70)
print("CREACIÓN MANUAL DE SUPERUSER")
print("=" * 70)

# Datos del superuser
CEDULA = '1020458606'
PASSWORD = 'cidoli2025'
NOMBRE = 'Administrador del Sistema'
EMAIL = 'admin@municipio.gov.co'
CARGO = 'Administrador'

# Verificar si ya existe
if Usuario.objects.filter(cedula=CEDULA).exists():
    print(f"\n⚠️  Ya existe un usuario con cédula {CEDULA}")
    user = Usuario.objects.get(cedula=CEDULA)
    print(f"\nDatos actuales:")
    print(f"  - Nombre: {user.nombre_completo}")
    print(f"  - Email: {user.email}")
    print(f"  - Cargo: {user.cargo}")
    print(f"  - Es superuser: {user.is_superuser}")
    print(f"  - Es staff: {user.is_staff}")
    print(f"  - Activo: {user.is_active}")
    
    respuesta = input("\n¿Deseas actualizar este usuario a superuser? (s/n): ")
    if respuesta.lower() == 's':
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.set_password(PASSWORD)
        user.save()
        print("\n✅ Usuario actualizado a superuser exitosamente!")
    else:
        print("\n❌ Operación cancelada.")
else:
    # Crear dependencia si no existe
    print(f"\n1. Verificando dependencia Jefe Jurídica (111)...")
    dependencia, created = Dependencia.objects.get_or_create(
        prefijo='111',
        defaults={
            'nombre_oficina': 'Jefe Jurídica',
            'activa': True
        }
    )
    if created:
        print("   ✅ Dependencia creada")
    else:
        print("   ✅ Dependencia ya existe")
    
    # Crear superuser
    print(f"\n2. Creando superuser...")
    try:
        user = Usuario.objects.create_superuser(
            cedula=CEDULA,
            nombre_completo=NOMBRE,
            email=EMAIL,
            cargo=CARGO,
            password=PASSWORD,
            dependencia=dependencia
        )
        
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        
        print("\n" + "=" * 70)
        print("✅ SUPERUSER CREADO EXITOSAMENTE")
        print("=" * 70)
        print(f"\nCredenciales:")
        print(f"  Usuario (Cédula): {CEDULA}")
        print(f"  Contraseña:       {PASSWORD}")
        print(f"  Nombre:           {NOMBRE}")
        print(f"  Email:            {EMAIL}")
        print(f"  Cargo:            {CARGO}")
        print(f"  Dependencia:      {dependencia.nombre_oficina} ({dependencia.prefijo})")
        print("\n⚠️  IMPORTANTE: Cambia la contraseña después del primer login")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error al crear superuser: {str(e)}")
        import traceback
        traceback.print_exc()
