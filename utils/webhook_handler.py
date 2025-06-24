import requests
import streamlit as st
import json

class WebhookHandler:
    """Maneja el envío y recepción de webhooks con Make"""
    
    def __init__(self):
        self.webhook_url = "https://hook.us2.make.com/a18h6yc94x6rp6s1m7do3tij3xontr85"
    
    def send_to_make(self, embedding, metadata, processing_id):
        """Envía datos al webhook de Make y recibe la respuesta JSON"""
        payload = {
            "embedding": embedding,
            "brief_name": f"{processing_id}.docx",
            "metadata": metadata,
            "processing_id": processing_id
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=180)
            response.raise_for_status()
            
            # Intentar extraer JSON de la respuesta
            try:
                json_response = response.json()
                return True, json_response
            except json.JSONDecodeError:
                # Si no es JSON directo, intentar extraer del texto
                response_text = response.text
                return True, response_text
                
        except requests.exceptions.RequestException as e:
            return False, f"Error al enviar datos: {str(e)}"
    
    def receive_from_make(self, processing_id):
        """Recibe respuesta de Make (implementar según tu API)"""
        # Esta función se implementaría para recibir la respuesta JSON
        # desde Make una vez procesado el cuestionario
        pass