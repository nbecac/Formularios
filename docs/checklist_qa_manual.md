# Checklist de QA Manual

Sigue estos pasos para validar el ecosistema "Formularios AI Assistant" en Windows desde cero:

## 1. Setup e Instalación
- [ ] Clonar repositorio en `C:\Users\Nicolás\Desktop\Formularios`.
- [ ] Ejecutar `scripts\setup.bat`.
- [ ] Verificar que se cree la carpeta `.venv` y no haya errores de dependencias.
- [ ] Verificar que termine con el mensaje "Database seeded successfully." (Se crea `data/formularios_agent.db`).

## 2. Validación de Backend Local
- [ ] Ejecutar `backend\run_backend.bat` (o mediante `scripts\run_all.bat`).
- [ ] Acceder en el navegador a `http://127.0.0.1:8000/health`.
  - **Esperado**: JSON con `"status": "ok"`.
- [ ] Acceder a `http://127.0.0.1:8000/api/students`.
  - **Esperado**: JSON con una lista de alumnos (ej. Juan Pérez).
- [ ] Acceder a `http://127.0.0.1:8000/api/debug/status`.
  - **Esperado**: JSON con el estado de conexión de BD y métricas.

## 3. Instalación de la Extensión Chrome
- [ ] Abrir `chrome://extensions/`.
- [ ] Activar "Modo desarrollador".
- [ ] Hacer click en "Cargar descomprimida" y seleccionar la carpeta `extension/`.
- [ ] Hacer click en los detalles de la extensión recién cargada y activar "Permitir acceso a URLs de archivo" (necesario para probar `formulario_prueba.html` si se abre desde local).

## 4. Prueba del Popup y Extensión
- [ ] Abrir `docs/formulario_prueba.html` en Chrome.
- [ ] Abrir el popup de la extensión.
- [ ] Verificar la sección "Diagnóstico": Debe decir Backend Conectado y mostrar la URL.
- [ ] Probar el botón "Probar conexión".
  - **Esperado**: Mostrar mensaje "Conectado correctamente." o alertar si hay error.
- [ ] Hacer click en "Detectar campos".
  - **Esperado**: El contador de campos debe incrementar y listar los elementos.
- [ ] Seleccionar un Alumno en el desplegable.
- [ ] Hacer click en "Generar respuestas".
  - **Esperado**: Ver sugerencias al lado de cada campo detectado.
- [ ] Hacer click en "Rellenar borrador".
  - **Esperado**: Los inputs, radios, selects de la página se llenan automáticamente.

## 5. Validaciones Críticas
- [ ] **NO SUBMIT AUTOMÁTICO**: Al rellenar los campos, el formulario bajo ninguna circunstancia debe enviarse. La página de prueba alertará con un cartel rojo o un `alert()` si se detecta un submit.
- [ ] **Revisión de Errores de Consola (Página)**: Presionar F12 en la pestaña del formulario. No deben aparecer excepciones del `contentScript.js`.
- [ ] **Revisión de Errores del Popup**: Clic derecho en el ícono de la extensión -> Inspeccionar popup. Validar ausencia de errores en Console.
- [ ] **Revisión de Background Service Worker**: En `chrome://extensions/`, hacer clic en "Service worker" de la extensión y revisar si hay errores (ej. CORS).
