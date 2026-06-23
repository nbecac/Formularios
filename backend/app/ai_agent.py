from typing import List, Dict, Any, Tuple
from .schemas import FormAnalyzeResponseField, GeneratedAnswer
from .models import Student

def _get_observation_by_category(student: Student, categories: List[str]) -> str:
    """
    Busca de manera case-insensitive si el alumno posee una observación que calce 
    dentro de la lista de categorías indicadas.
    Retorna el contenido de la primera que encuentre, o string vacío si no halla nada.
    """
    for cat in categories:
        for obs in student.observations:
            if obs.category and obs.category.lower() == cat.lower():
                return obs.content
    return ""

def _mock_generate(field: FormAnalyzeResponseField, student: Student) -> Tuple[str, str]:
    """
    Motor Mock de IA que mapea datos reales del alumno contra el campo detectado.
    Utiliza el nombre, el curso, nivel y las observaciones específicas por categoría.
    Retorna (respuesta_sugerida, explicacion_de_la_fuente).
    """
    label_lower = field.normalizedLabel.lower()
    
    # Mapeo directo de atributos básicos del alumno
    if "nombre" in label_lower or "name" in label_lower:
        return student.name, "Mapeo directo del nombre completo del alumno."
        
    elif "curso" in label_lower or "grado" in label_lower or "grade" in label_lower:
        return student.course, "Mapeo directo del curso o grado registrado del alumno."
        
    elif "nivel" in label_lower or "level" in label_lower:
        return student.level or "", "Mapeo directo del nivel educativo del alumno."
    
    # Heurísticas cruzadas con observaciones de categoría: Apoyo
    if "apoyo" in label_lower or "support" in label_lower or "nee" in label_lower:
        obs = _get_observation_by_category(student, ["apoyo", "general"])
        
        # Si es un campo de opciones cerrado (checkbox, select)
        if field.options:
            opts_lower = [o.lower() for o in field.options]
            needs_support = bool(obs) or (student.notes and ("apoyo" in student.notes.lower() or "dificultad" in student.notes.lower()))
            if "sí" in opts_lower or "si" in opts_lower or "yes" in opts_lower:
                ans = "Sí" if needs_support else "No"
                return ans, "Deducido a partir de existencia o falta de observaciones de apoyo."
                
        # Si es texto abierto y hay observación
        if obs:
            return obs, "Respuesta basada explícitamente en observación de apoyo del alumno."
            
        return "No requiere apoyo adicional.", "Respuesta mock por defecto ante la falta de registros de apoyo."
        
    # Heurísticas cruzadas con observaciones de categoría: Académico
    elif "académico" in label_lower or "academico" in label_lower or "desempeño" in label_lower or "rendimiento" in label_lower:
        obs = _get_observation_by_category(student, ["academico", "académico"])
        if obs:
            return obs, "Respuesta basada en el registro de la observación académica."
            
    # Heurísticas cruzadas con observaciones de categoría: Participación
    elif "participación" in label_lower or "participacion" in label_lower:
        obs = _get_observation_by_category(student, ["participacion", "participación"])
        if obs:
            return obs, "Respuesta basada en la observación de participación."
            
    # Heurísticas cruzadas con observaciones de categoría: Comportamiento
    elif "conducta" in label_lower or "comportamiento" in label_lower:
        obs = _get_observation_by_category(student, ["comportamiento", "conducta"])
        if obs:
            return obs, "Respuesta basada en registros sobre el comportamiento del estudiante."
            
    # Heurísticas cruzadas con observaciones de categoría: Asistencia
    elif "asistencia" in label_lower:
        obs = _get_observation_by_category(student, ["asistencia"])
        if obs:
            return obs, "Respuesta basada en la observación de asistencia."
            
    # Casos genéricos abiertos
    elif "fortalezas" in label_lower:
        return "Sin registro de fortalezas detalladas.", "Respuesta genérica editable (mock)."
        
    elif "áreas a mejorar" in label_lower or "areas a mejorar" in label_lower:
        return "Sin registro de áreas de mejora.", "Respuesta genérica editable (mock)."

    # Análisis general o comentarios
    if "observación" in label_lower or "comentario" in label_lower or "general" in label_lower:
        obs = _get_observation_by_category(student, ["general"])
        if obs:
            return obs, "Basado en la observación general ingresada al sistema."
        if student.notes:
            return student.notes, "Basado en las notas adicionales del perfil del alumno."
            
        return "Sin comentarios adicionales a reportar.", "Texto genérico para campo general."
        
    # Filtrado de campos no rastreados en este modelo de negocio
    elif "email" in label_lower or "correo" in label_lower:
        return "", "Campo ignorado intencionalmente por ser un dato de contacto no almacenado en la BD local."
        
    # Si hay opciones pero no entendimos el label, intentamos devolver la primera para no dejar en blanco
    elif field.options and len(field.options) > 0:
        return field.options[0], "No se detectó el contexto; se sugiere la primera opción por defecto."
        
    return "", "No se encontró ningún contexto en los datos del alumno aplicable a este campo."

def generate_answers(
    fields: List[FormAnalyzeResponseField], 
    student: Student, 
    page_context: Dict[str, str], 
    settings: Any
) -> List[GeneratedAnswer]:
    """
    Función principal de entrada para la orquestación de IA.
    Evalúa si la clave de OpenAI / Gemini está presente.
    Si no, o si hay un error, decae hacia el motor _mock_generate construido arriba.
    """
    answers = []
    provider = settings.AI_PROVIDER.lower() if settings and hasattr(settings, "AI_PROVIDER") else "mock"
    
    # Determinar si podemos usar IA real
    has_key = False
    if provider == "openai" and hasattr(settings, "OPENAI_API_KEY") and settings.OPENAI_API_KEY:
        has_key = True
    elif provider == "gemini" and hasattr(settings, "GEMINI_API_KEY") and settings.GEMINI_API_KEY:
        has_key = True
        
    if provider in ["openai", "gemini"] and not has_key:
        error_explanation = f"Motor {provider.upper()} seleccionado pero API key ausente. Usando mock_fallback."
        
        for field in fields:
            ans_text, mock_exp = _mock_generate(field, student)
            
            # Forzamiento simple de opciones
            if field.options and ans_text not in field.options:
                ans_text = next((o for o in field.options if ans_text.lower() in o.lower()), ans_text)
                
            answers.append(
                GeneratedAnswer(
                    fieldId=field.fieldId,
                    answer=ans_text,
                    confidence=0.5 if ans_text else 0.1,
                    source="mock_fallback",
                    explanation=f"{error_explanation} {mock_exp}"
                )
            )
        return answers

    # Iteración Mock normal
    for field in fields:
        ans_text, explanation = _mock_generate(field, student)
        
        # Intentar alinear la respuesta con alguna de las opciones existentes si es cerrada
        if field.options and ans_text not in field.options:
            ans_text = next((o for o in field.options if ans_text.lower() in o.lower()), ans_text)

        answers.append(
            GeneratedAnswer(
                fieldId=field.fieldId,
                answer=ans_text,
                confidence=0.85 if ans_text else 0.3,
                source="mock_ai",
                explanation=explanation
            )
        )
            
    return answers


def _dedupe_sources(sources):
    """Deduplica fuentes por (section, filename). Agrupa chunks del mismo archivo."""
    seen = {}
    for s in sources:
        key = (s.section, s.filename)
        if key not in seen:
            seen[key] = s
    return list(seen.values())[:5]


def _score_option_against_chunks(opt_text, chunks):
    """
    Calcula un score de coincidencia entre el texto de una opción y los chunks recuperados.
    Usa coincidencia de tokens significativos (len > 2), con bonus por frases completas.
    """
    score = 0.0
    opt_lower = opt_text.lower()
    tokens = [t for t in opt_lower.split() if len(t) > 2]
    
    if len(tokens) == 0:
        return 0.0
    
    for c in chunks:
        c_lower = c.content.lower()
        
        # Bonus grande: la frase completa de la opción aparece en el chunk
        if opt_lower in c_lower:
            score += 5.0
        
        # Bonus por cada token significativo encontrado
        for t in tokens:
            if t in c_lower:
                score += 1.0
        
        # Bonus extra: si tokens clave de la opción aparecen juntos (bigrams)
        for i in range(len(tokens) - 1):
            bigram = tokens[i] + " " + tokens[i+1]
            if bigram in c_lower:
                score += 2.0
    
    return score


def _calculate_confidence(best_score, second_score, has_sources):
    """
    Calcula la confianza basada en scores y presencia de fuentes.
    """
    if not has_sources:
        return 0.15
    
    if best_score <= 0:
        return 0.20
    
    margin = best_score - second_score
    ratio = best_score / max(second_score, 0.1)
    
    if margin < 1.5:
        return 0.35  # Empate
    elif ratio < 1.25:
        return 0.45  # Gana por poco
    elif best_score >= 6 and margin >= 2:
        return 0.75  # Gana claro
    elif best_score >= 10:
        return 0.85  # Evidencia fuerte
    else:
        return 0.55  # Gana moderadamente


def _should_suggest(best_score, second_score, has_sources):
    """
    Decide si se debe sugerir una alternativa.
    Reglas:
    - Si no hay fuentes, no sugerir.
    - Si best_score <= 0, no sugerir.
    - Si hay empate (diferencia < 1.5), no sugerir.
    - Si best_score >= 3 y best_score >= second_score * 1.25, sugerir.
    - Si best_score >= 6 y margen >= 2, sugerir.
    """
    if not has_sources:
        return False, "Sin fuentes relevantes."
    if best_score <= 0:
        return False, "Ninguna alternativa coincide con el material."
    
    margin = best_score - second_score
    
    if margin < 1.5:
        return False, f"Empate entre alternativas (margen: {margin:.1f}). No se puede decidir."
    
    if best_score >= 3 and best_score >= second_score * 1.25:
        return True, f"Alternativa clara (score: {best_score:.1f}, margen: {margin:.1f})."
    
    if best_score >= 6 and margin >= 2:
        return True, f"Evidencia fuerte (score: {best_score:.1f}, margen: {margin:.1f})."
    
    return False, f"Score insuficiente (best: {best_score:.1f}, margin: {margin:.1f})."


def answer_project_question(req: Any, db: Any, settings: Any) -> Any:
    from . import crud, schemas
    
    query = req.question
    preferred = ["E1", "E2", "E3", "resumen_clave", "syllabus_project_E1", "syllabus_project_E2", "syllabus_project_E3"]
    
    clean_q = query.lower()
    is_implementation = any(w in clean_q for w in ["cómo se hizo", "como se hizo", "qué hiciste", "que hiciste", "cómo respondiste", "como respondiste", "cómo implementaste", "como implementaste", "entrega", "proyecto"])
    is_improvement = any(w in clean_q for w in ["qué cambiarías", "que cambiarias", "cómo mejorarías", "como mejorarias"])
    is_theory = any(w in clean_q for w in ["teoría", "teoria", "concepto", "definición", "que es un", "qué es un"])
    is_requirement = any(w in clean_q for w in ["enunciado", "requisitos", "se pedía", "se pedia"])
    
    if is_theory:
        preferred = ["syllabus_clases", "syllabus_ayudantias"]
    elif is_requirement:
        preferred = ["syllabus_project", "syllabus_project_E1", "syllabus_project_E2", "syllabus_project_E3"]
    
    chunks = crud.search_knowledge(db, query, max_results=8, preferred_sections=preferred)
    
    # Build sources with deduplication
    raw_sources = []
    evidence_text = ""
    for c in chunks:
        snippet = c.content[:300] + "..." if len(c.content) > 300 else c.content
        raw_sources.append(schemas.KnowledgeSourceSnippet(
            section=c.section,
            title=c.source.title,
            filename=c.source.filename,
            snippet=snippet
        ))
        evidence_text += f"\n--- [{c.section}] {c.source.title} ---\n{c.content}\n"
    
    sources = _dedupe_sources(raw_sources)
    has_sources = len(chunks) > 0

    # ===== Modo Alternativas =====
    if req.options and len(req.options) > 0 and req.question_type == 'multiple_choice':
        if not has_sources:
            return schemas.CanvasQuestionResponse(
                answer="No hay evidencia suficiente en el material cargado para sugerir una alternativa con seguridad.",
                selected_option=None,
                selected_option_text=None,
                confidence=0.15,
                sources=[],
                explanation="Busqueda sin resultados relevantes en el material local.",
                question_type="multiple_choice",
                mode="multiple_choice_suggestion",
                needs_review=True,
                option_scores=[]
            )
        
        # --- Gemini Integration ---
        ai_provider = settings.AI_PROVIDER.lower() if settings and hasattr(settings, "AI_PROVIDER") else ""
        if ai_provider == "gemini" and hasattr(settings, "GEMINI_API_KEY") and settings.GEMINI_API_KEY:
            try:
                import json
                from google import genai
                from google.genai import types
                
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                options_text = json.dumps([{"label": o.label, "text": o.text} for o in req.options], ensure_ascii=False)
                
                system_prompt = f"""Eres un asistente experto evaluando una pregunta de selección múltiple.
Evalúa las opciones contra la evidencia proporcionada y selecciona la correcta.

Evidencia extraida:
{evidence_text}

Opciones:
{options_text}

Debes responder SOLAMENTE con un objeto JSON (sin comillas invertidas ni markdown extra, que cumpla response_mime_type="application/json") que contenga:
- "selected_option": el label de la opción seleccionada o null si es muy dudoso.
- "confidence": número entre 0.0 y 1.0 indicando tu seguridad.
- "explanation": por qué seleccionaste la opción basada en la evidencia."""
                user_prompt = f"Pregunta: {req.question}"
                
                response = client.models.generate_content(
                    model=settings.AI_MODEL or 'gemini-2.5-flash',
                    contents=system_prompt + "\n\n" + user_prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                
                data = json.loads(response.text)
                selected_label = data.get("selected_option")
                conf = float(data.get("confidence", 0.0))
                expl = data.get("explanation", "Generado por Gemini.")
                
                selected_text = None
                if selected_label:
                    for opt in req.options:
                        if opt.label == selected_label:
                            selected_text = opt.text
                            break
                            
                return schemas.CanvasQuestionResponse(
                    answer=f"Alternativa sugerida: {selected_label}" if selected_label else "No se pudo determinar una alternativa con certeza.",
                    selected_option=selected_label,
                    selected_option_text=selected_text,
                    confidence=conf,
                    sources=sources,
                    explanation=expl,
                    question_type="multiple_choice",
                    mode="gemini_multiple_choice_suggestion",
                    needs_review=True,
                    option_scores=[]
                )
            except Exception:
                pass
        # --- Fin Gemini Integration ---

        # Score each option against chunks
        scored = []
        for opt in req.options:
            s = _score_option_against_chunks(opt.text, chunks)
            scored.append({"label": opt.label, "text": opt.text, "score": round(s, 1)})
        
        # Sort by score descending
        scored.sort(key=lambda x: x["score"], reverse=True)
        
        best = scored[0]
        second = scored[1] if len(scored) > 1 else {"score": 0}
        
        should, reason = _should_suggest(best["score"], second["score"], has_sources)
        confidence = _calculate_confidence(best["score"], second["score"], has_sources)
        
        if should:
            return schemas.CanvasQuestionResponse(
                answer="Alternativa sugerida: " + best["label"],
                selected_option=best["label"],
                selected_option_text=best["text"],
                confidence=confidence,
                sources=sources,
                explanation=reason,
                question_type="multiple_choice",
                mode="multiple_choice_suggestion",
                needs_review=True,
                option_scores=scored
            )
        else:
            return schemas.CanvasQuestionResponse(
                answer="No hay evidencia suficiente para sugerir una alternativa con seguridad.",
                selected_option=None,
                selected_option_text=None,
                confidence=confidence,
                sources=sources,
                explanation=reason,
                question_type="multiple_choice",
                mode="multiple_choice_suggestion",
                needs_review=True,
                option_scores=scored
            )

    # ===== Modo Texto (compatibilidad) =====
    if not chunks:
        return schemas.CanvasQuestionResponse(
            answer="No se encontro evidencia suficiente en el material cargado para responder a esta pregunta con certeza.",
            confidence=0.1,
            sources=[],
            explanation="Busqueda sin resultados relevantes en el material local.",
            question_type="text",
            mode="knowledge_only",
            needs_review=True
        )

    provider = settings.AI_PROVIDER.lower() if settings and hasattr(settings, "AI_PROVIDER") else "mock"
    has_key = False
    if provider == "openai" and hasattr(settings, "OPENAI_API_KEY") and settings.OPENAI_API_KEY:
        has_key = True
        
    if provider == "openai" and has_key:
        import openai
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        system_prompt = f"""
Eres un asistente de evaluacion enfocado estrictamente en un proyecto de Base de Datos.
REGLAS ESTRICTAS:
- Responde a la pregunta basandote UNICA y EXCLUSIVAMENTE en el material proporcionado abajo.
- Si no hay suficiente evidencia, indicalo claramente.
- Nunca sugieras que enviaras la evaluacion. El usuario debe revisar.

INTENCION DE LA PREGUNTA:
- Si la pregunta pide "como se hizo", "que se respondio", usa las fuentes de E1, E2, E3. Escribe usando frases como "En la entrega se implemento..."
- Si la pregunta pide "que cambiarias" o "mejorarias", indica primero que se hizo realmente y luego sugiere la mejora separando claramente "Lo hecho" vs "Mejora sugerida".
- Si es teorica, responde basandote en las clases/ayudantias provistas en la evidencia.

Evidencia extraida del material del curso:
{evidence_text}
"""
        user_prompt = f"Pregunta: {req.question}\nOpciones (si aplica): {req.options}\nTipo: {req.question_type}"
        
        try:
            response = client.chat.completions.create(
                model=settings.AI_MODEL or "gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )
            ans_text = response.choices[0].message.content
            return schemas.CanvasQuestionResponse(
                answer=ans_text,
                confidence=0.85,
                sources=sources,
                explanation="Respuesta generada via LLM basada exclusivamente en el material recuperado.",
                mode="knowledge_only",
                needs_review=True
            )
        except Exception as e:
            pass

    # MOCK FALLBACK
    ans_text = "Basado en el material encontrado:\n"
    if is_implementation:
        ans_text = "En la entrega se implemento lo siguiente, segun la evidencia:\n"
    elif is_improvement:
        ans_text = "Lo hecho en la entrega fue:\n[Insertar hecho]\n\nMejora sugerida:\n[Insertar mejora teorica]\n\nEvidencia:\n"
        
    ans_text += f"{sources[0].snippet}\n\n*Nota: Extraccion directa (modo mock).*\n"
    
    return schemas.CanvasQuestionResponse(
        answer=ans_text,
        confidence=0.5,
        sources=sources,
        explanation="Extraccion directa del mejor chunk debido a modo mock.",
        question_type="text",
        mode="knowledge_only_mock",
        needs_review=True
    )
