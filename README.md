# Formularios AI Assistant

MVP local para autocompletado inteligente de formularios autorizados.

## Qué hace el proyecto
* Detecta campos en formularios visibles.
* Genera sugerencias de relleno mediante inteligencia artificial (actualmente en modo mock, en preparacion para IA real).
* Rellena borradores localmente en el navegador.

## Qué no hace (Seguridad)
* NUNCA hace click en botones de envío ("Enviar", "Submit", "Finalizar").
* No ejecuta `form.submit()`.
* No evade detección ni oculta automatización.
* Deja el envío final siempre a cargo de revisión humana.

## Instalación Local

1. Clona el repositorio.
2. Ejecuta `scripts/setup.bat` (solo Windows).
3. Asegurate de tener `python-multipart` instalado si necesitas probar la subida de archivos CSV.

## Cómo correr el backend

Ejecuta el script de inicialización general:
`scripts/run_all.bat`

O si ya tienes el entorno configurado, levanta el backend con:
`backend/run_backend.bat`

## Cómo cargar la extensión

1. Abre Google Chrome y ve a `chrome://extensions`.
2. Activa el "Modo desarrollador".
3. Haz click en "Cargar descomprimida" y selecciona la carpeta `extension/`.
4. Habilita "Permitir acceso a URLs de archivo" en los detalles de la extension.

## Cómo probar el formulario local

1. Abre el archivo `docs/formulario_prueba.html` en tu navegador.
2. Abre el popup de la extension.
3. Conecta y selecciona un alumno.
4. Genera respuestas y clickea "Rellenar borrador".

## Cómo revisar GitHub Actions

El repositorio cuenta con un pipeline de Integración Continua (CI) que corre automáticamente en cada push o pull request.
* **Qué valida el CI:** Clona el repo, instala Python 3.11, instala `backend/requirements.txt`, ejecuta la compilación de todos los archivos fuente de Python, y corre pruebas automatizadas (LFs, JSON, endpoints y seguridad no-submit).
* **Cómo revisar si está en verde:** Ve a la pestaña "Actions" del repositorio en GitHub para confirmar si el workflow pasó (status success).

## Estado actual del proyecto

MVP funcional local (Fase 1 completada, transicionando a Fase 2).
* Base de datos local: SQLite
* Backend: FastAPI
* Extensión Chrome: Manifest V3
* CI/CD: Pipeline estable en GitHub Actions

## Próxima Fase (Fase 2: administración de datos reales)

Administración real de datos mediante CRUD local de alumnos, observaciones y soporte de importación vía CSV. Uso de base de datos para simular mejor a los agentes y arquitectura lista para conectar IA real (OpenAI/Gemini).
