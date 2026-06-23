from typing import List, Dict, Any
from .schemas import FormAnalyzeResponseField, GeneratedAnswer
from .models import Student

def _mock_generate(field: FormAnalyzeResponseField, student: Student) -> str:
    label_lower = field.normalizedLabel.lower()
    
    if "nombre" in label_lower or "name" in label_lower:
        return student.name
    elif "curso" in label_lower or "grado" in label_lower or "grade" in label_lower:
        return student.course
    elif "nivel" in label_lower or "level" in label_lower:
        return student.level
    elif "apoyo" in label_lower or "support" in label_lower:
        # Check options
        opts_lower = [o.lower() for o in field.options]
        if "sí" in opts_lower or "si" in opts_lower or "yes" in opts_lower:
            return "Sí" if "apoyo" in student.notes.lower() or "dificultad" in student.notes.lower() else "No"
        return "No"
    elif "observación" in label_lower or "comentario" in label_lower or "desempeño" in label_lower or "comments" in label_lower:
        # Get some observation or notes
        obs = [o.content for o in student.observations if "desempeño" in label_lower and o.category == "académico"]
        if obs:
            return obs[0]
        return student.notes or "Sin observaciones particulares."
    elif "email" in label_lower or "correo" in label_lower:
        return "" # Do not invent sensitive emails
    elif field.options:
        # Pick the first one as fallback if not matching anything else
        return field.options[0]
        
    return ""

def generate_answers(
    fields: List[FormAnalyzeResponseField], 
    student: Student, 
    page_context: Dict[str, str], 
    settings: Any
) -> List[GeneratedAnswer]:
    answers = []
    
    provider = settings.AI_PROVIDER
    
    for field in fields:
        if provider == "mock":
            ans_text = _mock_generate(field, student)
            
            # Match options if needed
            if field.options and ans_text not in field.options:
                # Basic mapping
                ans_text = next((o for o in field.options if ans_text.lower() in o.lower()), ans_text)

            answers.append(
                GeneratedAnswer(
                    fieldId=field.fieldId,
                    answer=ans_text,
                    confidence=0.8,
                    source="mock_ai",
                    explanation="Respuesta generada mediante mock basado en reglas simples."
                )
            )
        else:
            # Here we would call OpenAI, Claude, etc.
            # Using prompt with student data and form context
            answers.append(
                GeneratedAnswer(
                    fieldId=field.fieldId,
                    answer="",
                    confidence=0.0,
                    source="real_ai",
                    explanation="AI real no implementada aún."
                )
            )
            
    return answers
