# Decisiones Técnicas

- **Chrome Extension vs Google Forms API**: Se optó por una extensión porque permite interactuar con formularios sin necesidad de acceso de API (que en entornos corporativos o educativos suele estar bloqueado) y mantiene al humano en el loop antes del envío.
- **SQLite**: No requiere instalación de servicios y es ideal para MVP.
- **Modo Mock**: Dado que no contamos con una API Key, el mock asegura el funcionamiento determinista para la prueba.
- **FastAPI**: Maneja concurrencia asíncrona de manera eficiente y define esquemas claros.
