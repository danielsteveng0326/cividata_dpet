# 📋 Instrucciones: Sistema de Plantillas Word

## ✅ Implementación Completada

Se ha implementado exitosamente un sistema de plantillas Word para las respuestas a derechos de petición.

## 🎯 Características

### 1. **Plantilla Institucional**
- Ubicación: `plantillas_word/plantilla_respuesta_peticion.docx`
- Formato profesional con encabezado institucional
- Incluye todos los elementos requeridos por gestión de calidad

### 2. **Datos Dinámicos**
El sistema reemplaza automáticamente los siguientes datos:
- ✓ Fecha actual (formato: "11 de octubre de 2025")
- ✓ Ciudad
- ✓ Nombre del peticionario
- ✓ Dirección del peticionario
- ✓ Radicado de la petición
- ✓ Cuerpo completo de la respuesta
- ✓ Nombre del funcionario que firma
- ✓ Cargo del funcionario

### 3. **Flujo de Uso**

1. El usuario genera una respuesta con el **Asistente IA**
2. Hace clic en **"Descargar Word"**
3. Se abre un modal solicitando:
   - Ciudad
   - Nombre del funcionario
   - Cargo del funcionario
4. El sistema genera el documento Word con la plantilla institucional
5. Se descarga automáticamente

## 🔧 Personalización de la Plantilla

### Para personalizar según los lineamientos de su entidad:

1. **Abrir la plantilla:**
   ```
   plantillas_word/plantilla_respuesta_peticion.docx
   ```

2. **Modificar elementos visuales:**
   - Logo de la entidad
   - Colores institucionales
   - Encabezados y pie de página
   - Fuentes y estilos

3. **IMPORTANTE - Mantener los marcadores:**
   ```
   {{CIUDAD}}
   {{FECHA}}
   {{NOMBRE_PETICIONARIO}}
   {{DIRECCION_PETICIONARIO}}
   {{RADICADO}}
   {{CUERPO_RESPUESTA}}
   {{NOMBRE_FUNCIONARIO}}
   {{CARGO_FUNCIONARIO}}
   ```

4. **Guardar el archivo** con el mismo nombre

## 📁 Estructura de Archivos

```
cividata_dpet/
├── plantillas_word/
│   ├── plantilla_respuesta_peticion.docx  ← Plantilla principal
│   ├── README.md                          ← Documentación detallada
│   └── .gitignore
├── crear_plantilla_base.py                ← Script para regenerar plantilla
└── INSTRUCCIONES_PLANTILLA_WORD.md        ← Este archivo
```

## 🚀 Próximos Pasos (Pendientes)

- [ ] Implementar sistema de autenticación de usuarios
- [ ] Asociar automáticamente el nombre y cargo del usuario logueado
- [ ] Permitir múltiples plantillas según tipo de respuesta
- [ ] Agregar firma digital

## 📝 Notas Técnicas

### Archivos Modificados:
- `peticiones/views.py` - Vista `descargar_respuesta_word()`
- `peticiones/urls.py` - Ruta para descarga
- `templates/peticiones/asistente_respuesta.html` - Modal y JavaScript
- `requirements.txt` - Dependencia `python-docx`

### Dependencias:
```
python-docx==1.1.0
```

### Instalación:
```bash
pip install python-docx==1.1.0
```

## 🧪 Pruebas

Para probar el sistema:

1. Crear una nueva petición
2. Procesar con IA
3. Usar el Asistente IA para generar respuesta
4. Hacer clic en "Descargar Word"
5. Completar los datos solicitados
6. Verificar que el documento descargado tenga el formato correcto

## ⚠️ Solución de Problemas

### Error: "No se encontró la plantilla de Word"
**Solución:** Ejecutar `python crear_plantilla_base.py` para regenerar la plantilla

### Los marcadores no se reemplazan
**Solución:** Verificar que los marcadores en la plantilla estén exactamente como: `{{NOMBRE}}`

### El formato se pierde
**Solución:** Asegurarse de que el marcador `{{CUERPO_RESPUESTA}}` esté en un párrafo con el formato deseado

## 📞 Contacto

Para soporte técnico o personalizaciones adicionales, contactar al equipo de desarrollo.

---

**Fecha de implementación:** Octubre 11, 2025  
**Versión:** 1.0
