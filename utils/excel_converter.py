import json
import pandas as pd
import io
import re
from typing import Dict, List, Optional

class ExcelConverter:
    """Convierte respuestas JSON a archivos Excel"""
    
    def clean_json_content(self, content: str) -> str:
        """Limpia el contenido de texto para extraer JSON válido"""
        content = content.strip()
        
        json_pattern = r'```(?:json)?\s*(.*?)\s*```'
        match = re.search(json_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            content = match.group(1).strip()
        
        return content
    
    def load_json_from_content(self, content: str) -> Optional[Dict]:
        """Carga JSON desde contenido de texto"""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            try:
                cleaned_content = self.clean_json_content(content)
                return json.loads(cleaned_content)
            except json.JSONDecodeError as e:
                raise ValueError(f"Error al parsear JSON: {str(e)}")
    
    def questions_to_dataframe(self, questions: List[Dict]) -> pd.DataFrame:
        """Convierte lista de preguntas a DataFrame"""
        rows = []
        for q in questions:
            # Limpieza básica de saltos de línea en opciones (igual que app.py)
            opts = q.get('Opciones de respuesta', '')
            opts = opts.replace('\r\n', ', ').strip()
            
            rows.append({
                'modulo': q.get('KPI base o Modulo', ''),
                'id': q.get('No. Pregunta', ''),
                'texto': q.get('Pregunta', ''),
                'tipo': q.get('Tipo de respuesta', ''),
                'opciones': opts,
                'indicador': q.get('Indicador', ''),
                'logica': q.get('Lógica de programación', '')
            })
        return pd.DataFrame(rows)
    
    def json_to_excel(self, json_content: str) -> bytes:
        """Convierte JSON a archivo Excel y retorna los bytes"""
        try:
            # Cargar JSON
            data = self.load_json_from_content(json_content)
            
            # Extraer preguntas
            questions = data.get('questions', [])
            if not questions:
                raise ValueError("No se encontraron preguntas en el JSON")
            
            # Convertir a DataFrame
            df = self.questions_to_dataframe(questions)
            
            # Crear Excel en memoria
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Preguntas', index=False)
                
                # Ajustar anchos de columnas
                worksheet = writer.sheets['Preguntas']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            raise ValueError(f"Error al convertir a Excel: {str(e)}")