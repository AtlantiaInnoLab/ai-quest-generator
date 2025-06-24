import openai
import json
import streamlit as st

class AIService:
    """Maneja servicios de IA para extracción de metadatos y embeddings"""
    
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=st.secrets.get("OPENAI_API_KEY", "")
        )
    
    def extract_metadata(self, full_text):
        """Extrae metadatos usando GPT-4"""
        metadata_prompt = f"""Actúa como extractor estructurado de metadata para la base de datos de briefs y KOs de estudios de investigación de mercados.

Voy a proporcionarte el texto completo de un Brief y/o su KO (Kick Off). A veces ambos, a veces solo uno.

Tu tarea es leer este texto y devolver SOLO la siguiente estructura de metadata, en formato JSON válido. No agregues texto adicional ni explicaciones, solo devuelve el JSON.

### Importante:

- El texto del KO puede contener información que no se debe incluir en el embedding (metodología final, muestra acordada, cronograma). NO incluyas esa información en los campos `objetivo_general`, `preguntas_negocio`, `hipotesis`, `texto_preview`.
- `texto_preview` debe contener únicamente fragmentos que describan el contexto del problema, los objetivos de negocio y el reto planteado por el cliente, SIN incluir menciones a "PCT", "U&A", "400 entrevistas", "CAWI", "metodología", "timeline", etc.
- Si el texto incluye preguntas de negocio, extrae la lista textual de esas preguntas. Si no hay, deja `preguntas_negocio` como [].
- Si algún campo no está explícito, déjalo vacío ("") o en [] según corresponda. No inventes nada.

Además, incluye los siguientes dos campos adicionales para control de calidad:

- `"tiene_brief"`: true si en el texto hay evidencia de que se incluye un Brief o contexto original del cliente.
- `"tiene_kickoff"`: true si en el texto hay evidencia de que es un KO, minuta de Kick Off o similar.

ESTRUCTURA:

{{
    "tipo_estudio": "",
    "nombre_proyecto": "",
    "marca": "",
    "industria": "",
    "objetivo_general": "",
    "preguntas_negocio": [],
    "decisiones_a_tomar": "",
    "target": "",
    "muestra_planificada": "",
    "hipotesis": "",
    "texto_preview": "",
    "archivo_link": "",
    "tiene_brief": false,
    "tiene_kickoff": false
}}

Aquí está el texto completo:

{full_text}"""

        try:
            chat_response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Eres un experto en extracción estructurada de metadata."},
                    {"role": "user", "content": metadata_prompt}
                ],
                temperature=0
            )

            metadata_json_str = chat_response.choices[0].message.content
            
            # Limpiar si viene con bloque de código
            if metadata_json_str.startswith("```json"):
                metadata_json_str = metadata_json_str.lstrip("```json").rstrip("```").strip()
            elif metadata_json_str.startswith("```"):
                metadata_json_str = metadata_json_str.lstrip("```").rstrip("```").strip()

            metadata_dict = json.loads(metadata_json_str)
            return metadata_dict
            
        except json.JSONDecodeError as e:
            st.error(f"Error al parsear JSON: {e}")
            return {}
        except Exception as e:
            st.error(f"Error al extraer metadatos: {e}")
            return {}
    
    def generate_embedding(self, text):
        """Genera embedding usando OpenAI"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            st.error(f"Error al generar embedding: {e}")
            return None