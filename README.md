# Formularios AI Assistant

## ¿Qué hace el proyecto?
Es un asistente local diseñado para ayudar en la cumplimentación de borradores de formularios web utilizando contexto real de alumnos e Inteligencia Artificial (mock o real). Detecta campos de texto y los rellena basándose en el perfil de cada estudiante (por ejemplo, curso, observaciones previas de comportamiento o académicas).

## ¿Qué NO hace por seguridad?
* Nunca ejecuta `form.submit()`.
* No hace click en botones de "Enviar", "Submit", "Send" o "Finalizar".
* No automatiza plataformas de evaluaciones restringidas como Canvas, ni intenta evadir detecciones.
* No resuelve captchas de forma automatizada.
* La herramienta está diseñada como un rellenador de "borrador" que requiere revisión manual y envío explícito por el usuario.

## Instalación Local

1. Clona este repositorio y entra en la carpeta local:
   ```bash
   git clone https://github.com/nbecac/Formularios.git
   cd Formularios
   ```
2. Crea el entorno virtual e instala dependencias:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```
3. Inicializa la base de datos de SQLite con los datos de prueba:
   ```bash
   python -m backend.app.seed_data
   ```

## Cómo Correr el Backend

El backend está construido con FastAPI y Uvicorn. Para iniciarlo, asegúrate de estar dentro del entorno virtual y ejecuta:
```bash
uvicorn backend.app.main:app --reload
```
La API estará disponible localmente en: `http://127.0.0.1:8000`.

## Cómo Cargar la Extensión en Chrome

1. Abre Google Chrome y ve a la dirección `chrome://extensions/`.
2. Activa el "Modo desarrollador" en la esquina superior derecha.
3. Haz clic en "Cargar descomprimida" (Load unpacked).
4. Selecciona la carpeta `extension` ubicada dentro del repositorio.

## Cómo Probar `docs/formulario_prueba.html`

El proyecto incluye un formulario de demostración completamente en local.
1. Abre el archivo `docs/formulario_prueba.html` directamente en tu navegador Chrome.
2. Haz clic en el ícono de la extensión cargada previamente.
3. Asegúrate de que el backend esté corriendo (debería decir "Conectado").
4. Haz clic en "Detectar campos", selecciona un alumno y luego "Generar respuestas".
5. Finalmente, presiona "Rellenar borrador". Verás cómo se rellenan los campos en la página.

## Cómo Usar `docs/admin.html` (Fase 2)

El proyecto incluye ahora un panel de administración estático que consume la API del backend.
1. Abre el archivo `docs/admin.html` en Chrome.
2. Desde allí podrás visualizar los alumnos existentes, agregar nuevos alumnos y gestionar observaciones (académicas, comportamiento, apoyo, general).
3. También dispones de una función de importación masiva mediante archivo CSV. Un archivo de prueba se encuentra en `data/ejemplo_alumnos.csv`.

## Cómo Revisar GitHub Actions

El repositorio cuenta con validación continua de CI a través de GitHub Actions.
Para verificar el estado de los *pipelines*:
1. Dirígete a la pestaña **Actions** en tu repositorio de GitHub.
2. Allí podrás ver las validaciones realizadas sobre tu último *commit* o *pull request*.
3. El *pipeline* clona el código, verifica la sintaxis de Python, corre los tests automatizados y valida que el archivo de configuración `manifest.json` esté correctamente escrito.

## Estado Actual
El proyecto se encuentra en la **Fase 2 (Administración de Datos Reales)** finalizada y estable. 
Se ha completado el desarrollo del CRUD con base de datos real (SQLite) mediante FastAPI y la UI administrativa básica se encuentra operacional para ingestar alumnos vía CSV.

## Próximos Pasos
* Iniciar la **Fase 3**: Integración real con la API de modelos grandes de lenguaje (LLM), reemplazando el módulo mock y estructurando un motor capaz de redactar respuestas mucho más sofisticadas basadas en las observaciones guardadas.
* Agregar pruebas en formularios externos complejos.

## Fase 3: IA real opcional
El proyecto soporta el uso opcional de OpenAI para la generaci�n de respuestas de borradores.
- **Modo Mock (por defecto)**: Si AI_PROVIDER=mock, la aplicacion cruza palabras clave del formulario con las notas y categorias de las observaciones del alumno localmente, sin hacer llamadas externas.
- **Modo OpenAI**: Si AI_PROVIDER=openai y se configura OPENAI_API_KEY en el archivo .env, la IA analizara todo el contexto del alumno y los campos para generar respuestas mas contextualizadas. Si no se provee la API Key o hay problemas de red, el sistema hace un _fallback_ seguro al modo mock automaticamente para no bloquear el flujo.
- No se suben claves al repositorio. La extension no envia el formulario de forma automatica bajo ningun concepto.

Para probar la IA, visita docs/admin.html (o http://127.0.0.1:8000/docs/admin.html si lo sirves localmente) y usa el panel de Diagnostico IA.

## Modo Evaluación Autorizada - Base de Datos
Este modo especial permite utilizar el sistema para evaluaciones autorizadas (ej. Canvas Student) basándose estrictamente en el material del proyecto del curso.

**Límites Éticos y Técnicos:**
- NUNCA se enviará el formulario automáticamente. El envío es siempre manual.
- No simula comportamiento humano para engañar a Canvas. Solo es una ayuda de borrador visible.
- Si se activa KNOWLEDGE_ONLY_MODE=true, no usará material externo, solo el importado.

**Cómo usar:**
1. Crea una carpeta Material para responder en la raíz.
2. Agrega subcarpetas: E1, E2, E3 y syllabus.
3. Entra a docs/knowledge_admin.html (o usa la UI) y presiona **Importar desde Carpeta Local**.
4. En el popup de la extensión, selecciona el **Modo Evaluación Autorizada**, presiona **Detectar pregunta actual** y luego **Buscar en material y sugerir**.
5. Las búsquedas priorizan siempre E1, E2, E3 para asegurar fidelidad a lo entregado.
6. Revisa las fuentes listadas antes de presionar **Rellenar borrador**.
