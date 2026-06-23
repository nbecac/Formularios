from typing import List
from .schemas import FormField, FormAnalyzeResponseField

def normalize_fields(fields: List[FormField]) -> List[FormAnalyzeResponseField]:
    """
    Recibe la lista de campos crudos extraídos por contentScript.js desde el DOM del navegador.
    Limpia, normaliza e identifica el propósito probable de cada campo (label vs name).
    Devuelve la estructura final que consumirá la IA para generar las respuestas.
    """
    normalized = []
    
    for f in fields:
        # Extraer el mejor label disponible
        raw_label = f.label or f.ariaLabel or f.placeholder or f.nearbyText or f.fieldId
        
        # Limpieza básica
        clean_label = str(raw_label).strip()
        
        # Opciones si es un select o radio
        opts = f.options if f.options else []
        
        # Calcular confianza básica del parseo
        confidence = 0.9 if f.label else (0.7 if f.ariaLabel else 0.5)
        
        # Advertencias
        warnings = []
        if not clean_label:
            warnings.append("No se encontró un label descriptivo claro.")
            
        normalized.append(FormAnalyzeResponseField(
            fieldId=f.fieldId,
            normalizedLabel=clean_label,
            normalizedType=f.type,
            options=opts,
            required=f.required,
            confidence=confidence,
            warnings=warnings
        ))
        
    return normalized
