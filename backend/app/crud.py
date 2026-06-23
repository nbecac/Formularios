import csv
import io
from sqlalchemy.orm import Session
from . import models, schemas

def get_students(db: Session):
    """
    Retorna todos los estudiantes registrados.
    """
    return db.query(models.Student).all()

def get_student(db: Session, student_id: int):
    """
    Retorna un estudiante filtrado por ID.
    """
    return db.query(models.Student).filter(models.Student.id == student_id).first()

def create_student(db: Session, student: schemas.StudentCreate):
    """
    Inserta un nuevo estudiante en la base de datos.
    """
    db_student = models.Student(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def update_student(db: Session, student_id: int, student: schemas.StudentUpdate):
    """
    Actualiza datos básicos de un estudiante existente de forma parcial.
    """
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        return None
        
    update_data = student.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_student, key, value)
        
    db.commit()
    db.refresh(db_student)
    return db_student

def delete_student(db: Session, student_id: int):
    """
    Borra un estudiante y todas sus observaciones asociadas (cascada definida en modelo).
    """
    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        return None
        
    db.delete(db_student)
    db.commit()
    return db_student

def get_student_observations(db: Session, student_id: int):
    """
    Recupera todas las observaciones para un estudiante dado.
    """
    return db.query(models.Observation).filter(models.Observation.student_id == student_id).all()

def create_observation(db: Session, student_id: int, observation: schemas.ObservationCreate):
    """
    Agrega una nueva observación a un estudiante en específico.
    """
    db_obs = models.Observation(**observation.model_dump(), student_id=student_id)
    db.add(db_obs)
    db.commit()
    db.refresh(db_obs)
    return db_obs

def update_observation(db: Session, observation_id: int, observation: schemas.ObservationUpdate):
    """
    Actualiza la categoría o contenido de una observación existente.
    """
    db_obs = db.query(models.Observation).filter(models.Observation.id == observation_id).first()
    if not db_obs:
        return None
        
    update_data = observation.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obs, key, value)
        
    db.commit()
    db.refresh(db_obs)
    return db_obs

def delete_observation(db: Session, observation_id: int):
    """
    Borra directamente una observación puntual.
    """
    db_obs = db.query(models.Observation).filter(models.Observation.id == observation_id).first()
    if not db_obs:
        return None
        
    db.delete(db_obs)
    db.commit()
    return db_obs

def import_students_csv(db: Session, csv_text: str) -> dict:
    """
    Importa masivamente estudiantes usando formato CSV delimitado por comas o punto y coma.
    Soporta encoding utf-8-sig para evadir BOM characters.
    Hace Upsert basado en la llave natural (name, course).
    """
    # Intentamos detectar delimitador si viene con ;
    delimiter = ';' if ';' in csv_text.split('\n')[0] else ','
    
    # Preparamos el lector
    reader = csv.DictReader(io.StringIO(csv_text), delimiter=delimiter)
    
    creados = 0
    actualizados = 0
    obs_creadas = 0
    errores = []
    
    for idx, row in enumerate(reader, start=1):
        try:
            name = row.get('name', '').strip()
            course = row.get('course', '').strip()
            
            # Name y course son obligatorios para el upsert
            if not name or not course:
                errores.append({"row_index": idx, "error": "name y course son obligatorios en cada fila"})
                continue
                
            level = row.get('level', '').strip()
            notes = row.get('notes', '').strip()
            
            # Buscar el estudiante por llave natural
            student = db.query(models.Student).filter(
                models.Student.name == name, 
                models.Student.course == course
            ).first()
            
            if student:
                # Update
                if level:
                    student.level = level
                if notes:
                    student.notes = notes
                actualizados += 1
            else:
                # Create
                student = models.Student(
                    name=name, 
                    course=course, 
                    level=level, 
                    notes=notes
                )
                db.add(student)
                db.flush() # Importante para poder asignar observaciones en el mismo paso
                creados += 1
                
            obs_cat = row.get('observation_category', '').strip()
            obs_content = row.get('observation_content', '').strip()
            
            if obs_cat and obs_content:
                obs = models.Observation(
                    student_id=student.id, 
                    category=obs_cat, 
                    content=obs_content
                )
                db.add(obs)
                obs_creadas += 1
                
        except Exception as e:
            errores.append({"row_index": idx, "error": f"Excepcion importando fila: {str(e)}"})
            
    db.commit()
    
    return {
        "alumnos_creados": creados,
        "alumnos_actualizados": actualizados,
        "observaciones_creadas": obs_creadas,
        "errores": errores
    }

def get_settings(db: Session):
    return db.query(models.Setting).all()

def update_setting(db: Session, key: str, value: str):
    setting = db.query(models.Setting).filter(models.Setting.key == key).first()
    if setting:
        setting.value = value
    else:
        setting = models.Setting(key=key, value=value)
        db.add(setting)
    db.commit()
    return setting

def create_history(db: Session, history: schemas.HistoryCreate):
    db_hist = models.History(
        url=history.url,
        page_title=history.page_title,
        student_id=history.student_id,
        detected_fields_json=history.detected_fields_json,
        generated_answers_json=history.generated_answers_json
    )
    db.add(db_hist)
    db.commit()
    db.refresh(db_hist)
    return db_hist

import os
from pathlib import Path

import os
import zipfile
import tempfile
import shutil
import json
import re
from pathlib import Path
import csv

def _extract_zip_safely(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            # Security: Prevent directory traversal
            if member.startswith('/') or '..' in member:
                continue
            # Security: Skip known bad folders
            if any(bad in member for bad in ['.git/', '__MACOSX/', 'node_modules/', '.venv/']):
                continue
            zip_ref.extract(member, extract_to)

def _get_section_and_priority(rel_path_str):
    section = "syllabus"
    source_kind = "course_content"
    priority = 40
    
    parts = Path(rel_path_str).parts
    
    if parts[0] in ["E1", "E2", "E3"]:
        section = parts[0]
        source_kind = "student_submission"
        priority = 100
    elif "Syllabus" in parts[0] or "syllabus" in parts[0].lower():
        if "Proyecto" in parts:
            if "E1" in parts:
                section = "syllabus_project_E1"
                priority = 80
            elif "E2" in parts:
                section = "syllabus_project_E2"
                priority = 80
            elif "E3" in parts:
                section = "syllabus_project_E3"
                priority = 80
            else:
                section = "syllabus_project"
                priority = 75
        elif "Clases" in parts:
            section = "syllabus_clases"
            priority = 40
        elif "Ayudantías" in parts or "Ayudantias" in parts:
            section = "syllabus_ayudantias"
            priority = 40
            
    filename = Path(rel_path_str).name
    if filename == "memoria_maestra_proyecto.md":
        section = "memoria_maestra"
        source_kind = "user_verified_master_memory"
        priority = 1000
    elif filename == "resumen_clave_proyecto.md":
        section = "resumen_clave"
        source_kind = "user_verified_summary"
        priority = 700
    elif filename.startswith("ficha_"):
        section = "ficha_" + parts[0] if parts[0] in ["E1", "E2", "E3"] else "ficha_general"
        source_kind = "user_verified_summary"
        priority = 800

    return section, source_kind, priority

def _chunk_text(content, max_len=1500, overlap=200, is_master_memory=False):
    if not content: return []
    
    if is_master_memory:
        # Custom chunking preserving headers
        # Split by any heading (e.g. \n# )
        parts = re.split(r'\n(?=#+ )', "\n" + content)
        chunks = []
        for part in parts:
            part = part.strip()
            if not part: continue
            
            # Extract the header (the first line)
            lines = part.split("\n", 1)
            header = lines[0] if len(lines) > 0 else ""
            
            if len(part) <= max_len:
                chunks.append(part)
            else:
                # If a section is too big, split it but prepend the header
                # Ensure we don't break QA pairs (they usually start with ### QA-)
                # We'll split by sub-blocks like ### or blank lines
                sub_parts = re.split(r'\n\n', part)
                current = ""
                for sp in sub_parts:
                    # If this subpart alone is too big, we just have to chunk it roughly
                    if len(current) + len(sp) > max_len and current:
                        # Append current and start new
                        chunks.append(current.strip())
                        current = header + "\n\n" + sp
                    else:
                        if not current:
                            current = sp
                        else:
                            current += "\n\n" + sp
                if current:
                    chunks.append(current.strip())
        return chunks
        
    # Default behavior for other files
    if "# " in content or "## " in content:
        parts = re.split(r'(?=\n#)', content)
    else:
        parts = content.split("\n\n")
        
    chunks = []
    current = ""
    for p in parts:
        if len(current) + len(p) > max_len and current:
            chunks.append(current.strip())
            current = current[-overlap:] + "\n" + p
        else:
            current += "\n" + p
    if current:
        chunks.append(current.strip())
    
    return chunks

def _chunk_code(content, ext):
    if not content: return []
    if ext == 'sql':
        # Split by SQL statements roughly
        parts = re.split(r'(?i)(?=\b(CREATE|INSERT|SELECT|FUNCTION|TRIGGER)\b)', content)
        return [p.strip() for p in parts if len(p.strip()) > 10][:50]
    else:
        # Default code chunking (PHP, CSS) - simple block split
        parts = content.split("\n\n")
        return [p.strip() for p in parts if len(p.strip()) > 10][:50]

def import_knowledge_folder(db: Session, base_folder_path: str) -> dict:
    fuentes_importadas = 0
    chunks_creados = 0
    archivos_omitidos = 0
    errores = []

    # Path resolution relative to this file
    app_dir = Path(__file__).parent
    project_root = app_dir.parent.parent
    base_path = project_root / base_folder_path

    if not base_path.exists() or not base_path.is_dir():
        return {
            "fuentes_importadas": 0, "chunks_creados": 0, "archivos_omitidos": 0, 
            "errores": [f"La carpeta '{base_path}' no existe o no es un directorio."],
            "ruta_absoluta": str(base_path),
            "existe": base_path.exists(),
            "es_dir": base_path.is_dir() if base_path.exists() else False,
            "contenido_raiz": os.listdir(project_root) if project_root.exists() else []
        }

    # Clean existing
    db.query(models.KnowledgeSource).delete()
    db.commit()

    temp_dir = tempfile.mkdtemp()
    try:
        # 1. Process base_path. Copy or extract to temp_dir
        for item in base_path.iterdir():
            if item.name.startswith('.') or item.name in ['__MACOSX']:
                continue
            if item.is_dir():
                shutil.copytree(item, Path(temp_dir) / item.name)
            elif item.suffix.lower() == '.zip':
                _extract_zip_safely(item, Path(temp_dir) / item.stem)
            elif item.is_file():
                shutil.copy2(item, Path(temp_dir) / item.name)

        allowed_text_exts = {".txt", ".md", ".sql", ".php", ".css", ".json", ".ipynb"}
        allowed_img_exts = {".png", ".jpg", ".jpeg", ".svg"}
        
        # We will use pypdf if available
        try:
            from pypdf import PdfReader
            has_pypdf = True
        except ImportError:
            has_pypdf = False

        for root, dirs, files in os.walk(temp_dir):
            if '.git' in dirs: dirs.remove('.git')
            if 'node_modules' in dirs: dirs.remove('node_modules')
            if '.venv' in dirs: dirs.remove('.venv')
            
            for file in files:
                if file.startswith('.'): continue
                file_path = Path(root) / file
                rel_path = file_path.relative_to(temp_dir)
                ext = file_path.suffix.lower()
                
                # Ignorar videos y binarios no deseados
                if ext in [".mp4", ".ppsx", ".pack", ".idx", ".rev", ".exe", ".dll"]:
                    archivos_omitidos += 1
                    continue

                section, source_kind, priority = _get_section_and_priority(str(rel_path))

                # CREATE SOURCE
                source = models.KnowledgeSource(
                    title=file_path.stem,
                    source_type=ext.strip('.'),
                    source_kind=source_kind,
                    folder=rel_path.parts[0] if len(rel_path.parts)>0 else "",
                    filename=file_path.name,
                    relative_path=str(rel_path),
                    priority=priority
                )
                
                if ext in allowed_text_exts:
                    try:
                        content = file_path.read_text(encoding="utf-8-sig", errors="ignore")
                        db.add(source)
                        db.flush()
                        fuentes_importadas += 1
                        
                        if ext in ['.sql', '.php', '.css']:
                            chunks = _chunk_code(content, ext.strip('.'))
                        else:
                            is_mm = (file_path.name == "memoria_maestra_proyecto.md")
                            chunks = _chunk_text(content, is_master_memory=is_mm)
                            
                        for i, c in enumerate(chunks):
                            db.add(models.KnowledgeChunk(source_id=source.id, section=section, content=c, chunk_index=i))
                            chunks_creados += 1
                    except Exception as e:
                        errores.append(f"Error TXT {file_path.name}: {e}")
                        
                elif ext == '.csv':
                    try:
                        content = file_path.read_text(encoding="utf-8-sig", errors="ignore")
                        lines = content.splitlines()
                        if lines:
                            summary = f"Archivo CSV: {file_path.name}\nTotal filas aprox: {len(lines)}\nPrimeras filas:\n"
                            summary += "\n".join(lines[:6])
                            db.add(source)
                            db.flush()
                            db.add(models.KnowledgeChunk(source_id=source.id, section=section, content=summary, chunk_index=0))
                            fuentes_importadas += 1
                            chunks_creados += 1
                    except Exception as e:
                        errores.append(f"Error CSV {file_path.name}: {e}")
                        
                elif ext == '.pdf' and has_pypdf:
                    try:
                        reader = PdfReader(file_path)
                        db.add(source)
                        db.flush()
                        fuentes_importadas += 1
                        for i, page in enumerate(reader.pages):
                            text = page.extract_text()
                            if text and text.strip():
                                db.add(models.KnowledgeChunk(source_id=source.id, section=section, content=text.strip(), page_number=i+1, chunk_index=i))
                                chunks_creados += 1
                    except Exception as e:
                        errores.append(f"Error PDF {file_path.name}: {e}")
                
                elif ext in allowed_img_exts:
                    db.add(source)
                    db.flush()
                    fuentes_importadas += 1
                    summary = f"Fuente visual: {file_path.name}, asociada a {section}."
                    db.add(models.KnowledgeChunk(source_id=source.id, section=section, content=summary, chunk_index=0))
                    chunks_creados += 1
                else:
                    archivos_omitidos += 1

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    db.commit()
    return {
        "fuentes_importadas": fuentes_importadas,
        "chunks_creados": chunks_creados,
        "archivos_omitidos": archivos_omitidos,
        "errores": errores,
        "ruta_absoluta": str(base_path)
    }

def search_knowledge(db: Session, query: str, max_results: int = 5, preferred_sections: list = None):
    stopwords = {"el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "a", "ante", "con", "en", "para", "por", "y", "o", "que", "se", "es", "son", "como", "sobre"}
    clean_q = query.lower().replace('?', '').replace('¿', '')
    query_words = [w for w in clean_q.split() if w not in stopwords and len(w) > 2]
    if not query_words:
        return []

    chunks = db.query(models.KnowledgeChunk).join(models.KnowledgeSource).all()
    
    layer_mm = []
    layer_fichas = []
    layer_ex = []
    layer_syll = []
    
    # Determine dynamic preferred sections based on query
    q_mentions_e1 = "e1" in clean_q or "entrega 1" in clean_q
    q_mentions_e2 = "e2" in clean_q or "entrega 2" in clean_q or "pago" in clean_q or "membres" in clean_q or "cuota" in clean_q or "csv" in clean_q
    q_mentions_e3 = "e3" in clean_q or "entrega 3" in clean_q or "php" in clean_q or "login" in clean_q
    
    for c in chunks:
        score = 0
        content_lower = c.content.lower()
        title_lower = c.source.title.lower() if c.source.title else ""
        
        for w in query_words:
            if w in content_lower:
                score += content_lower.count(w) * 1.0
            if w in title_lower:
                score += 5.0
                
        if score > 0:
            section = c.section
            # Contextual boosting for Master Memory based on question topics
            if section == "memoria_maestra":
                if q_mentions_e2 and ("e2" in content_lower or "pago" in content_lower or "csv" in content_lower):
                    score += 50.0
                if q_mentions_e1 and ("e1" in content_lower or "modelo" in content_lower or "relacion" in content_lower):
                    score += 50.0
                if q_mentions_e3 and ("e3" in content_lower or "php" in content_lower or "vista" in content_lower):
                    score += 50.0
                    
            if preferred_sections and c.source.folder in preferred_sections:
                score += 20.0
                
            kind = c.source.source_kind
            if section == "memoria_maestra":
                layer_mm.append((score, c))
            elif "ficha" in section or "resumen" in section:
                layer_fichas.append((score, c))
            elif kind == "student_submission":
                # contextual boosting for E1/E2/E3
                if q_mentions_e2 and c.source.folder == "E2":
                    score += 30.0
                elif q_mentions_e1 and c.source.folder == "E1":
                    score += 30.0
                elif q_mentions_e3 and c.source.folder == "E3":
                    score += 30.0
                layer_ex.append((score, c))
            else:
                layer_syll.append((score, c))

    layer_mm.sort(key=lambda x: x[0], reverse=True)
    layer_fichas.sort(key=lambda x: x[0], reverse=True)
    layer_ex.sort(key=lambda x: x[0], reverse=True)
    layer_syll.sort(key=lambda x: x[0], reverse=True)
    
    # Hierarchical resolution
    final_chunks = []
    
    if len(layer_mm) >= 2:
        final_chunks.extend(layer_mm)
        final_chunks.extend(layer_fichas)
        final_chunks.extend(layer_ex)
    elif len(layer_mm) == 1:
        final_chunks.extend(layer_mm)
        final_chunks.extend(layer_fichas)
        final_chunks.extend(layer_ex)
    else:
        final_chunks.extend(layer_fichas)
        final_chunks.extend(layer_ex)
        final_chunks.extend(layer_syll)
        
    # Deduplicate and limit
    seen = set()
    result = []
    for s, c in final_chunks:
        if c.id not in seen:
            seen.add(c.id)
            result.append(c)
            if len(result) >= max_results:
                break
                
    # If still not enough, add syllabus
    if len(result) < max_results:
        for s, c in layer_syll:
            if c.id not in seen:
                seen.add(c.id)
                result.append(c)
                if len(result) >= max_results:
                    break
                    
    return result
