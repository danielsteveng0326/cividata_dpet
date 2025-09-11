# services/gemini_service.py
import google.generativeai as genai
import PyPDF2
import time
import json
import re
from django.conf import settings
from django.core.files.base import ContentFile
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


class GeminiTranscriptionService:
    def __init__(self):
        """
        Inicializa el servicio de Gemini para transcripción de PDFs
        """
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def extraer_texto_pdf(self, archivo_pdf):
        """
        Extrae el texto completo de un archivo PDF
        """
        try:
            # Leer el archivo PDF
            pdf_content = archivo_pdf.read()
            pdf_file = BytesIO(pdf_content)
            
            # Usar PyPDF2 para extraer texto
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            texto_completo = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                texto_pagina = page.extract_text()
                texto_completo += f"\n--- PÁGINA {page_num + 1} ---\n"
                texto_completo += texto_pagina
            
            # Resetear el puntero del archivo
            archivo_pdf.seek(0)
            
            return texto_completo
            
        except Exception as e:
            logger.error(f"Error extrayendo texto del PDF: {str(e)}")
            return None
    
    def transcribir_con_gemini(self, texto_extraido):
        """
        Usa Gemini para limpiar y estructurar la transcripción completa
        """
        try:
            prompt = f"""
            Eres un asistente especializado en transcripción de derechos de petición ciudadanos para un municipio.

            Tu tarea es:
            1. Limpiar y estructurar el siguiente texto extraído de un PDF
            2. Corregir errores de OCR si los hay
            3. Mantener TODO el contenido original, no resumir ni omitir información
            4. Organizar el texto de manera clara y legible
            5. Conservar la estructura original del documento

            IMPORTANTE: 
            - NO hagas resúmenes, transcribe completamente
            - Mantén todos los detalles, fechas, números y referencias
            - Si hay información personal, consérvala tal como está
            - Organiza el texto en párrafos claros

            TEXTO A TRANSCRIBIR:
            {texto_extraido}

            TRANSCRIPCIÓN COMPLETA Y LIMPIA:
            """
            
            # Enviar a Gemini
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                logger.warning("Gemini no devolvió respuesta válida")
                return texto_extraido  # Devolver texto original si falla IA
                
        except Exception as e:
            logger.error(f"Error en transcripción con Gemini: {str(e)}")
            return texto_extraido  # Devolver texto original si falla IA
    
    def extraer_datos_peticionario(self, texto_extraido):
        """
        Extrae información del peticionario del texto usando Gemini
        """
        try:
            prompt = f"""
            Eres un especialista en extracción de datos de documentos legales. Analiza el siguiente texto de un derecho de petición y extrae ÚNICAMENTE la información personal del peticionario.

            Busca y extrae:
            - Nombre completo del peticionario
            - Número de documento de identidad (cédula, pasaporte, etc.)
            - Teléfono o celular
            - Correo electrónico
            - Dirección completa

            IMPORTANTE:
            - Si no encuentras algún dato, devuelve "NO_ENCONTRADO" para ese campo
            - No inventes ni asumas información que no esté en el texto
            - Extrae solo información que sea claramente del peticionario
            - Responde ÚNICAMENTE en el formato JSON especificado

            TEXTO DEL DOCUMENTO:
            {texto_extraido}

            RESPUESTA (solo JSON, sin explicaciones):
            {{
                "nombre": "nombre completo o NO_ENCONTRADO",
                "documento": "número de documento o NO_ENCONTRADO", 
                "telefono": "número de teléfono o NO_ENCONTRADO",
                "correo": "correo electrónico o NO_ENCONTRADO",
                "direccion": "dirección completa o NO_ENCONTRADO"
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                # Limpiar respuesta y extraer JSON
                respuesta_limpia = response.text.strip()
                
                # Buscar JSON entre llaves
                json_match = re.search(r'\{.*\}', respuesta_limpia, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    datos = json.loads(json_str)
                    
                    # Convertir "NO_ENCONTRADO" a None
                    for key, value in datos.items():
                        if value == "NO_ENCONTRADO":
                            datos[key] = None
                    
                    return datos
                else:
                    logger.warning("No se encontró JSON válido en respuesta de Gemini")
                    return {}
                    
            else:
                logger.warning("Gemini no devolvió respuesta para extracción de datos")
                return {}
                
        except Exception as e:
            logger.error(f"Error extrayendo datos del peticionario: {str(e)}")
            return {}
    
    def procesar_peticion_completa(self, peticion):
        """
        Procesa una petición completa: extrae texto, transcribe con IA y extrae datos del peticionario
        """
        tiempo_inicio = time.time()
        
        try:
            # 1. Extraer texto del PDF
            logger.info(f"Iniciando procesamiento de {peticion.radicado}")
            texto_extraido = self.extraer_texto_pdf(peticion.archivo_pdf)
            
            if not texto_extraido:
                raise Exception("No se pudo extraer texto del PDF")
            
            # 2. Transcribir con Gemini
            logger.info(f"Enviando a Gemini para transcripción: {peticion.radicado}")
            transcripcion_limpia = self.transcribir_con_gemini(texto_extraido)
            
            # 3. Extraer datos del peticionario si no fueron llenados manualmente
            logger.info(f"Extrayendo datos del peticionario: {peticion.radicado}")
            datos_peticionario = self.extraer_datos_peticionario(texto_extraido)
            
            # 4. Actualizar petición con datos extraídos (solo si no existen)
            datos_actualizados = False
            
            if not peticion.peticionario_nombre and datos_peticionario.get('nombre'):
                peticion.peticionario_nombre = datos_peticionario['nombre']
                datos_actualizados = True
                
            if not peticion.peticionario_id and datos_peticionario.get('documento'):
                peticion.peticionario_id = datos_peticionario['documento']
                datos_actualizados = True
                
            if not peticion.peticionario_telefono and datos_peticionario.get('telefono'):
                peticion.peticionario_telefono = datos_peticionario['telefono']
                datos_actualizados = True
                
            if not peticion.peticionario_correo and datos_peticionario.get('correo'):
                peticion.peticionario_correo = datos_peticionario['correo']
                datos_actualizados = True
                
            if not peticion.peticionario_direccion and datos_peticionario.get('direccion'):
                peticion.peticionario_direccion = datos_peticionario['direccion']
                datos_actualizados = True
            
            # 5. Guardar transcripción y datos del peticionario
            peticion.transcripcion_completa = transcripcion_limpia
            peticion.save()
            
            if datos_actualizados:
                logger.info(f"Datos del peticionario actualizados automáticamente: {peticion.radicado}")
            
            # 6. Crear registro de procesamiento IA
            tiempo_total = time.time() - tiempo_inicio
            
            from peticiones.models import ProcesamientoIA
            ProcesamientoIA.objects.create(
                peticion=peticion,
                tiempo_procesamiento=tiempo_total,
                estado_procesamiento='exitoso'
            )
            
            logger.info(f"Procesamiento exitoso de {peticion.radicado} en {tiempo_total:.2f}s")
            return True
            
        except Exception as e:
            # Registrar error en el modelo
            tiempo_total = time.time() - tiempo_inicio
            
            from peticiones.models import ProcesamientoIA
            ProcesamientoIA.objects.create(
                peticion=peticion,
                tiempo_procesamiento=tiempo_total,
                estado_procesamiento='error',
                mensaje_error=str(e)
            )
            
            logger.error(f"Error procesando {peticion.radicado}: {str(e)}")
            return False
    
    def reanalizar_peticion(self, peticion):
        """
        Re-analiza una petición que ya fue procesada anteriormente
        """
        logger.info(f"Re-analizando petición {peticion.radicado}")
        return self.procesar_peticion_completa(peticion)