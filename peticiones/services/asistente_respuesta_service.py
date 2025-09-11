# peticiones/services/asistente_respuesta_service.py
import google.generativeai as genai
import json
import time
from django.conf import settings
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class AsistenteRespuestaService:
    def __init__(self):
        """
        Servicio para generar respuestas inteligentes a derechos de petición
        """
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def analizar_peticion_y_generar_preguntas(self, peticion):
        """
        Analiza el derecho de petición y genera preguntas estratégicas
        para recopilar información necesaria para dar una respuesta precisa
        """
        try:
            if not peticion.transcripcion_completa:
                raise ValidationError("La petición debe estar transcrita primero")
            
            prompt = f"""
            Eres un experto en derecho administrativo y derechos de petición en Colombia.
            
            Tu tarea es analizar el siguiente derecho de petición y generar máximo 3 preguntas estratégicas que permitan al funcionario municipal dar una respuesta precisa, completa y oportuna.

            DERECHO DE PETICIÓN A ANALIZAR:
            {peticion.transcripcion_completa}

            INSTRUCCIONES:
            1. Analiza cuidadosamente el contenido del derecho de petición
            2. Identifica los puntos clave que requieren información adicional para responder adecuadamente
            3. Genera entre 1 y 3 preguntas (solo las necesarias) que ayuden a:
               - Clarificar aspectos técnicos o legales específicos
               - Obtener información adicional necesaria para una respuesta completa
               - Identificar la competencia exacta del municipio
               - Determinar el procedimiento o normativa aplicable

            Las preguntas deben ser:
            - Específicas y relevantes al caso
            - Orientadas a obtener información que mejore la calidad de la respuesta
            - Enfocadas en aspectos legales, técnicos o procedimentales

            RESPONDE EN EL SIGUIENTE FORMATO JSON:
            {{
                "resumen_peticion": "Breve resumen de qué solicita el peticionario",
                "aspectos_clave": ["aspecto 1", "aspecto 2", "aspecto 3"],
                "preguntas": [
                    {{
                        "pregunta": "¿Pregunta específica?",
                        "justificacion": "Por qué es importante esta pregunta",
                        "opciones_sugeridas": ["opción 1", "opción 2", "opción 3"]
                    }}
                ],
                "urgencia": "alta|media|baja",
                "competencia_municipal": "sí|no|parcial"
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                # Limpiar respuesta y extraer JSON
                respuesta_texto = response.text.strip()
                
                # Buscar JSON en la respuesta
                import re
                json_match = re.search(r'\{.*\}', respuesta_texto, re.DOTALL)
                
                if json_match:
                    json_str = json_match.group()
                    analisis = json.loads(json_str)
                    
                    # Validar estructura mínima
                    required_fields = ['resumen_peticion', 'preguntas']
                    for field in required_fields:
                        if field not in analisis:
                            raise ValidationError(f"Respuesta de IA incompleta: falta {field}")
                    
                    return analisis
                else:
                    raise ValidationError("IA no devolvió JSON válido")
            else:
                raise ValidationError("IA no devolvió respuesta")
                
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON de IA: {str(e)}")
            raise ValidationError("Error procesando respuesta de IA")
        except Exception as e:
            logger.error(f"Error en análisis con IA: {str(e)}")
            raise ValidationError(f"Error en análisis: {str(e)}")
    
    def generar_respuesta_sugerida(self, peticion, respuestas_usuario):
        """
        Genera una respuesta sugerida basada en el análisis y las respuestas del usuario
        """
        try:
            # Formatear las respuestas del usuario
            respuestas_formateadas = ""
            for i, respuesta in enumerate(respuestas_usuario, 1):
                respuestas_formateadas += f"\nPregunta {i}: {respuesta.get('pregunta', '')}\nRespuesta: {respuesta.get('respuesta', '')}\n"
            
            prompt = f"""
            Eres un experto en derecho administrativo colombiano especializado en derechos de petición.
            
            Con base en el derecho de petición analizado y las respuestas proporcionadas por el funcionario, genera una respuesta COMPLETA, PRECISA y LEGALMENTE FUNDAMENTADA.

            DERECHO DE PETICIÓN:
            {peticion.transcripcion_completa}

            INFORMACIÓN ADICIONAL PROPORCIONADA:
            {respuestas_formateadas}

            INSTRUCCIONES PARA LA RESPUESTA:
            1. La respuesta debe ser formal y profesional
            2. Debe citar las normas legales aplicables (Constitución, leyes, decretos)
            3. Debe ser clara y comprensible para el ciudadano
            4. Debe responder TODOS los puntos solicitados en la petición
            5. Si algo no es competencia del municipio, explicar claramente y orientar
            6. Incluir términos y procedimientos si aplica
            7. Mantener un tono respetuoso y servicial
            8. No uses negrita, ni subrayado, ni pasos a seguir ni indicaciones dentro del derecho de petición ponlo listo para copiar
            9. No uses **

            ESTRUCTURA SUGERIDA:
            1. Saludo cordial y referencia al radicado
            2. Respuesta punto por punto
            3. Fundamentos legales
            4. Pasos a seguir (si aplica)
            5. Información de contacto para dudas
            6. Despedida formal
            7. No uses **

            GENERA UNA RESPUESTA COMPLETA Y LISTA PARA ENVIAR:
            """
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return {
                    'respuesta_sugerida': response.text.strip(),
                    'fecha_generacion': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'modelo_usado': 'gemini-1.5-flash'
                }
            else:
                raise ValidationError("IA no pudo generar respuesta")
                
        except Exception as e:
            logger.error(f"Error generando respuesta: {str(e)}")
            raise ValidationError(f"Error generando respuesta: {str(e)}")
    
    def evaluar_calidad_respuesta(self, respuesta_generada):
        """
        Evalúa la calidad de la respuesta generada y sugiere mejoras
        """
        try:
            prompt = f"""
            Evalúa la siguiente respuesta a un derecho de petición en una escala de 1-10 y sugiere mejoras:

            RESPUESTA A EVALUAR:
            {respuesta_generada}

            CRITERIOS DE EVALUACIÓN:
            1. Claridad y comprensibilidad (1-10)
            2. Completitud de la respuesta (1-10)
            3. Fundamentación legal adecuada (1-10)
            4. Tono profesional y cordial (1-10)
            5. Utilidad para el ciudadano (1-10)

            RESPONDE EN JSON:
            {{
                "puntuacion_total": 0-10,
                "evaluacion_detallada": {{
                    "claridad": 0-10,
                    "completitud": 0-10,
                    "fundamentacion_legal": 0-10,
                    "profesionalismo": 0-10,
                    "utilidad": 0-10
                }},
                "fortalezas": ["fortaleza 1", "fortaleza 2"],
                "mejoras_sugeridas": ["mejora 1", "mejora 2"],
                "recomendacion": "aceptar|revisar|rehacer"
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                import re
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
            return None
            
        except Exception as e:
            logger.error(f"Error evaluando respuesta: {str(e)}")
            return None