from typing import List
from .schemas import FormField, FormAnalyzeResponseField

def normalize_fields(fields: List[FormField]) -> List[FormAnalyzeResponseField]:
    normalized_fields = []
    
    for f in fields:
        # Determine normalized label
        labels = [f.label, f.ariaLabel, f.placeholder, f.nearbyText]
        valid_labels = [l for l in labels if l and l.strip()]
        
        normalized_label = valid_labels[0] if valid_labels else "Unknown Field"
        
        # Determine type
        normalized_type = f.type.lower()
        if normalized_type not in ["text", "textarea", "select", "radio", "checkbox", "email", "number", "date", "contenteditable"]:
            normalized_type = "unknown"
            
        normalized_fields.append(
            FormAnalyzeResponseField(
                fieldId=f.fieldId,
                normalizedLabel=normalized_label.strip(),
                normalizedType=normalized_type,
                options=f.options or [],
                required=f.required,
                confidence=0.9 if valid_labels else 0.5,
                warnings=["No clear label found"] if not valid_labels else []
            )
        )
        
    return normalized_fields
