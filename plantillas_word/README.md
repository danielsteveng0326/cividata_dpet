# Plantillas Word para Respuestas a Derechos de Petición

## 📄 Descripción

Esta carpeta contiene las plantillas de Word utilizadas para generar las respuestas oficiales a los derechos de petición.

## 🎯 Plantilla Actual

**Archivo:** `plantilla_respuesta_peticion.docx`

Esta plantilla se utiliza para generar documentos Word con el formato institucional de la entidad.

## 🔧 Marcadores de Posición

La plantilla utiliza los siguientes marcadores que son reemplazados automáticamente por el sistema:

| Marcador | Descripción | Ejemplo |
|----------|-------------|---------|
| `{{CIUDAD}}` | Ciudad desde donde se emite la respuesta | Bogotá D.C. |
| `{{FECHA}}` | Fecha actual en formato largo | 11 de octubre de 2025 |
| `{{NOMBRE_PETICIONARIO}}` | Nombre completo del peticionario | Juan Pérez García |
| `{{DIRECCION_PETICIONARIO}}` | Dirección del peticionario | Calle 123 #45-67 |
| `{{RADICADO}}` | Número de radicado de la petición | dpet2025101100001 |
| `{{CUERPO_RESPUESTA}}` | Contenido de la respuesta generada por IA | [Texto completo de la respuesta] |
| `{{NOMBRE_FUNCIONARIO}}` | Nombre del funcionario que firma | María López Rodríguez |
| `{{CARGO_FUNCIONARIO}}` | Cargo del funcionario | Secretario de Gobierno |

## 📝 Cómo Personalizar la Plantilla

### Opción 1: Editar la plantilla existente

1. Abra el archivo `plantilla_respuesta_peticion.docx` con Microsoft Word
2. Modifique el diseño, colores, logos, encabezados según los lineamientos de su entidad
3. **IMPORTANTE:** Mantenga los marcadores `{{NOMBRE_MARCADOR}}` en el documento
4. Guarde el archivo con el mismo nombre

### Opción 2: Crear una nueva plantilla desde cero

1. Cree un nuevo documento Word con el diseño institucional
2. Incluya todos los marcadores necesarios (ver tabla arriba)
3. Guarde el archivo como `plantilla_respuesta_peticion.docx` en esta carpeta
4. Reemplace el archivo existente

### Opción 3: Regenerar la plantilla base

Si desea regenerar la plantilla base desde código:

```bash
# Activar entorno virtual
venv\Scripts\activate

# Ejecutar script de creación
python crear_plantilla_base.py
```

## 🎨 Recomendaciones de Diseño

- **Encabezado:** Incluya el logo y nombre de la entidad
- **Fuente:** Use fuentes profesionales como Times New Roman, Arial o Calibri
- **Tamaño:** 11pt o 12pt para el cuerpo del texto
- **Márgenes:** 1 pulgada (2.54 cm) en todos los lados
- **Interlineado:** 1.5 para mejor legibilidad
- **Pie de página:** Incluya información de contacto de la entidad

## ⚠️ Notas Importantes

1. **No elimine los marcadores:** El sistema busca estos marcadores para reemplazarlos. Si los elimina, esos datos no aparecerán en el documento final.

2. **Formato de marcadores:** Los marcadores deben estar exactamente como se muestran: `{{NOMBRE}}` (con dobles llaves y en mayúsculas).

3. **Ubicación del archivo:** La plantilla debe estar en esta carpeta (`plantillas_word/`) para que el sistema la encuentre.

4. **Respaldo:** Antes de modificar la plantilla, haga una copia de seguridad.

## 🔄 Actualización Automática

Cuando modifique la plantilla, los cambios se aplicarán inmediatamente en todas las nuevas descargas de documentos. No es necesario reiniciar el servidor.

## 📞 Soporte

Si tiene problemas con la plantilla o necesita ayuda para personalizarla, contacte al administrador del sistema.
