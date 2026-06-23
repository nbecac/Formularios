# Formularios AI Assistant

MVP local para autocompletado inteligente de formularios autorizados.

## Instalación y Uso Local

1. Clona el repositorio.
2. Ejecuta scripts\setup.bat (solo Windows).
3. Ejecuta scripts\run_all.bat.
4. Carga la extensión en Chrome.
5. Abre docs\formulario_prueba.html y abre la extensión.

## Validación automática con GitHub Actions

El repositorio cuenta con un pipeline de Integración Continua (CI) que corre automáticamente en cada push o pull request.
- **Qué valida el CI:** Clona el repositorio, instala Python 3.11, instala las dependencias de ackend/requirements.txt, ejecuta la compilación de todos los archivos fuente de Python, y ejecuta los tests automáticos (pytest).
- **Cómo revisar si está en verde:** Puedes ir a la pestaña "Actions" del repositorio en GitHub para revisar si el workflow pasó con éxito (✓) o falló (×).
- **Qué hacer si falla:** Si el build falla, entra al detalle del workflow para ver los logs, corrige los tests, dependencias o el código que produjo el error, y vuelve a hacer un push.
- **Regla estricta:** No se debe avanzar a Fase 2 hasta que CI esté verde.

