# Reporte de Implementación del MVP "Formularios"

## Archivos Creados
Se implementó un ecosistema full-stack compuesto por:
- **Backend FastAPI**: `app/main.py`, `app/models.py`, `app/schemas.py`, `app/crud.py`, `app/ai_agent.py`, `app/form_analyzer.py`, `app/database.py`, `app/seed_data.py`.
- **Extensión Chrome**: `manifest.json`, `background.js`, `contentScript.js`, `popup.html`, `popup.js`, `popup.css`.
- **Scripts de entorno**: `scripts/setup.bat`, `scripts/run_all.bat`, `backend/run_backend.bat`.
- **Documentación y tests**: `docs/formulario_prueba.html`, `README.md`.

## Decisiones Técnicas
- **SQLite + SQLAlchemy**: Utilizado para mantener el proyecto 100% local, ligero y fácil de portar.
- **FastAPI**: Elegido por su velocidad y soporte para tipado (Pydantic), lo cual facilita crear endpoints robustos y auto-documentados.
- **Modo Mock (IA)**: Se incorporó una lógica heurística basada en sub-strings en `ai_agent.py` para devolver valores realistas según los datos del `seed_data.py` sin usar API Keys.
- **Seguridad**: Se agregó validación explícita en el `contentScript.js` para nunca ejecutar `.submit()` y se ignoran botones de tipo submit en la detección.

## Estado de Funcionalidad
- [x] Inicialización del entorno con `setup.bat`.
- [x] Ejecución del servidor FastAPI con CORS habilitado en `127.0.0.1:8000`.
- [x] Poblado de base de datos exitoso (3 alumnos de prueba, configuraciones).
- [x] La extensión se conecta al backend local sin bloqueos de CORS.
- [x] Detección de inputs y mapeo en `docs/formulario_prueba.html`.
- [x] Generación de respuestas basadas en el alumno (ej: Juan Pérez -> problemas en matemáticas).
- [x] Rellenado en el DOM con disparos de eventos de `input`, `change` y `blur`.
- [x] Registro del historial de uso en `/api/history`.

## Limitaciones y Tareas Pendientes (Google Forms)
- La implementación en Google Forms es heurística. Algunos radios o selects complejos de Google usan spans y divs anidados (`role="listbox"`, `role="radio"`) en lugar de `input type="radio"` nativo, por lo que el `contentScript.js` requerirá futuras optimizaciones de MutationObservers y simulación de Clicks para funcionar perfectamente en Forms complejos. Por ahora, funciona en inputs de texto estándar.

## Resultado de Pruebas Manuales
*Todo probado y corriendo de forma estable en entorno Windows local.*
