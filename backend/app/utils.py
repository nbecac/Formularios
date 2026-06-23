def format_student_name(name: str) -> str:
    """
    Función de utilidad genérica para asegurar que el nombre del alumno 
    esté capitalizado correctamente.
    """
    if not name:
        return ""
    return " ".join([word.capitalize() for word in name.strip().split()])

def clean_course_name(course: str) -> str:
    """
    Función de utilidad para limpiar caracteres extraños en el curso.
    """
    if not course:
        return ""
    return course.strip().upper()
