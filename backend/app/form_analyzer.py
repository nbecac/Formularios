from typing import List
from .schemas import FormField, FormAnalyzeResponseField

def normalize_fields(fields: List[FormField]) -> List[FormAnalyzeResponseField]:
    normalized = []
    
    for f in fields:
        label = f.label or f.ariaLabel or f.placeholder or f.nearbyText or f.fieldId
        label = label.strip()
        
        type_norm = f.type.lower()
        if type_norm in ['text', 'textarea', 'email', 'number', 'date', 'contenteditable']:
            type_norm = 'text'
        elif type_norm in ['select-one', 'select']:
            type_norm = 'select'
        elif type_norm in ['radio', 'checkbox']:
            type_norm = 'choice'
            
        warnings = []
        if not label or label == f.fieldId:
            warnings.append("Label no detectado correctamente")
            
        normalized.append(
            FormAnalyzeResponseField(
                fieldId=f.fieldId,
                normalizedLabel=label,
                normalizedType=type_norm,
                options=f.options or [],
                required=f.required,
                confidence=0.9 if not warnings else 0.5,
                warnings=warnings
            )
        )
        
    return normalized
