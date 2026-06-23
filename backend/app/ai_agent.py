from typing import List, Dict, Any
from .schemas import FormAnalyzeResponseField, GeneratedAnswer
from .models import Student

def _get_observation_by_category(student: Student, categories: List[str]) -> str:
    for cat in categories:
        for obs in student.observations:
            if obs.category and obs.category.lower() == cat.lower():
                return obs.content
    return ""

def _mock_generate(field: FormAnalyzeResponseField, student: Student) -> tuple[str, str]:
    label_lower = field.normalizedLabel.lower()
    
    if "nombre" in label_lower or "name" in label_lower:
        return student.name, "Mapeo directo del nombre del alumno."
    elif "curso" in label_lower or "grado" in label_lower or "grade" in label_lower:
        return student.course, "Mapeo directo del curso del alumno."
    elif "nivel" in label_lower or "level" in label_lower:
        return student.level or "", "Mapeo directo del nivel del alumno."
    
    # Heuristicas por categoria
    if "apoyo" in label_lower or "support" in label_lower:
        obs = _get_observation_by_category(student, ["apoyo", "general"])
        if field.options:
            opts_lower = [o.lower() for o in field.options]
            needs_support = bool(obs) or (student.notes and ("apoyo" in student.notes.lower() or "dificultad" in student.notes.lower()))
            if "sí" in opts_lower or "si" in opts_lower or "yes" in opts_lower:
                ans = "Sí" if needs_support else "No"
                return ans, "Deducido a partir de observaciones de apoyo o notas."
        if obs:
            return obs, "Basado en observacion de apoyo."
        return "No requiere apoyo adicional.", "Respuesta por defecto ante falta de datos de apoyo."
        
    elif "académico" in label_lower or "academico" in label_lower or "desempeño" in label_lower:
        obs = _get_observation_by_category(student, ["academico", "académico"])
        if obs:
            return obs, "Basado en observacion academica."
            
    elif "participación" in label_lower or "participacion" in label_lower:
        obs = _get_observation_by_category(student, ["participacion", "participación"])
        if obs:
            return obs, "Basado en observacion de participacion."
            
    elif "conducta" in label_lower or "comportamiento" in label_lower:
        obs = _get_observation_by_category(student, ["comportamiento", "conducta"])
        if obs:
            return obs, "Basado en observacion de comportamiento."
            
    elif "asistencia" in label_lower:
        obs = _get_observation_by_category(student, ["asistencia"])
        if obs:
            return obs, "Basado en observacion de asistencia."
            
    elif "fortalezas" in label_lower:
        return "Sin registrar", "Respuesta generica editable."
    elif "áreas a mejorar" in label_lower or "areas a mejorar" in label_lower:
        return "Sin registrar", "Respuesta generica editable."

    # General / Comentarios finales
    if "observación" in label_lower or "comentario" in label_lower or "general" in label_lower:
        obs = _get_observation_by_category(student, ["general"])
        if obs:
            return obs, "Basado en observacion general."
        if student.notes:
            return student.notes, "Basado en las notas del alumno."
        return "Sin comentarios adicionales.", "Respuesta generica editable."
        
    elif "email" in label_lower or "correo" in label_lower:
        return "", "Campo ignorado por ser dato de contacto no almacenado."
        
    elif field.options:
        return field.options[0], "Primera opcion por defecto."
        
    return "", "No se encontro contexto para este campo."

def generate_answers(
    fields: List[FormAnalyzeResponseField], 
    student: Student, 
    page_context: Dict[str, str], 
    settings: Any
) -> List[GeneratedAnswer]:
    answers = []
    provider = settings.AI_PROVIDER.lower()
    
    if provider in ["openai", "gemini"]:
        has_key = False
        if provider == "openai" and settings.OPENAI_API_KEY:
            has_key = True
        elif provider == "gemini" and settings.GEMINI_API_KEY:
            has_key = True
            
        if not has_key:
            # Fallback to mock with clear message
            error_explanation = "No hay API key configurada. Usando modo mock."
            for field in fields:
                ans_text, mock_exp = _mock_generate(field, student)
                if field.options and ans_text not in field.options:
                    ans_text = next((o for o in field.options if ans_text.lower() in o.lower()), ans_text)
                    
                answers.append(
                    GeneratedAnswer(
                        fieldId=field.fieldId,
                        answer=ans_text,
                        confidence=0.5,
                        source="mock_fallback",
                        explanation=f"{error_explanation} {mock_exp}"
                    )
                )
            return answers
        else:
            # Placeholder for future implementation
            pass

    # Default mock implementation
    for field in fields:
        ans_text, explanation = _mock_generate(field, student)
        if field.options and ans_text not in field.options:
            ans_text = next((o for o in field.options if ans_text.lower() in o.lower()), ans_text)

        answers.append(
            GeneratedAnswer(
                fieldId=field.fieldId,
                answer=ans_text,
                confidence=0.8 if ans_text else 0.3,
                source="mock_ai",
                explanation=explanation
            )
        )
            
    return answers
