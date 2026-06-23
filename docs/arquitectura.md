# Arquitectura del MVP

```text
[ Navegador Web / Chrome ]
       |
       | (DOM Scraping & Event Injection)
       v
[ Chrome Extension (Manifest V3) ]
   - popup.html (UI)
   - contentScript.js (Lector de campos y escritor)
   - background.js (Opcional, enrutador de mensajes)
       |
       | (REST API via fetch)
       v
[ Backend Local (FastAPI) ]
   - main.py (Endpoints)
   - form_analyzer.py (Normalización)
   - ai_agent.py (Motor Mock/IA para sugerencias)
       |
       | (SQLAlchemy / ORM)
       v
[ Base de Datos (SQLite) ]
   - data/formularios_agent.db
```

El flujo principal es:
1. El usuario abre el formulario.
2. La extensión extrae los `inputs` y sus `labels`.
3. Se envía el JSON al Backend.
4. El Backend y el `ai_agent` asocian las preguntas con los datos del alumno en SQLite.
5. Se devuelven las sugerencias generadas.
6. La extensión inyecta los valores en el DOM sin hacer click en Enviar.
