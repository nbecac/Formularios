# Formularios AI Assistant

MVP de ecosistema local para ayudar a rellenar formularios administrativos repetitivos utilizando Inteligencia Artificial (o reglas mock) de forma autorizada.

## Seguridad y Limitaciones (CRÍTICO)
**ESTA EXTENSIÓN NUNCA ENVÍA FORMULARIOS AUTOMÁTICAMENTE.**
- Solo detecta campos.
- Sugiere textos para rellenar a modo de "borrador".
- El usuario humano debe revisar, corregir y presionar "Enviar" manualmente.
- No está diseñada para evadir restricciones, ocultar automatización ni automatizar evaluaciones/exámenes.

## Arquitectura
El sistema consta de dos partes:
1. **Backend Local (FastAPI + SQLite)**: Almacena estudiantes, historial y configuraciones. Expone una API para generar sugerencias.
2. **Extensión de Chrome**: Lee el DOM, extrae labels, y rellena los inputs de manera segura.

## Instalación y Ejecución

### 1. Requisitos
- Python 3.9+
- Google Chrome

### 2. Levantar el Backend
1. Ejecuta el script de configuración inicial (crea entorno virtual e inicializa la BD):
   ```cmd
   scripts\setup.bat
   ```
2. Ejecuta el backend (puedes usar el script unificado):
   ```cmd
   scripts\run_all.bat
   ```
   (El servidor quedará corriendo en `http://127.0.0.1:8000`)

### 3. Cargar la Extensión en Chrome
1. Abre Chrome y navega a `chrome://extensions/`.
2. Activa el modo de desarrollador (esquina superior derecha).
3. Haz clic en "Cargar descomprimida".
4. Selecciona la carpeta `extension` dentro de este proyecto.

### 4. Probar
1. Abre el archivo local `docs/formulario_prueba.html` en tu navegador.
2. Abre el Popup de la extensión.
3. Presiona "Detectar campos".
4. Selecciona un alumno de la lista.
5. Presiona "Generar respuestas".
6. Presiona "Rellenar borrador".
7. Revisa las respuestas y envía manualmente.

## IA y Modo Mock
Actualmente, el sistema funciona en modo `mock` para evitar depender de API Keys en la fase de prueba. Si deseas conectar una IA real más adelante, edita el archivo `.env`.

## Google Forms
El soporte inicial para Google Forms es **experimental**. Google Forms usa un DOM dinámico muy complejo. El sistema intenta capturar las preguntas mediante reglas heurísticas, pero puede fallar dependiendo de la plantilla. Se validará principalmente usando el formulario local de prueba.
