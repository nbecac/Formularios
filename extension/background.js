// background.js maneja la comunicación con el backend si es necesario, 
// o simplemente sirve como proxy seguro para peticiones.

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "fetch_api") {
        fetch(request.url, request.options)
            .then(res => res.json().then(data => ({ status: res.status, ok: res.ok, data })).catch(() => ({ status: res.status, ok: res.ok, data: {} })))
            .then(response => sendResponse(response))
            .catch(error => {
                console.error("Background fetch failed:", error);
                sendResponse({ error: "No se pudo conectar al backend. Revisa que esté corriendo en 127.0.0.1:8000. Detalles: " + error.message });
            });
        return true; 
    }
});
