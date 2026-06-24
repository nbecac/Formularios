const API_URL = "http://127.0.0.1:8000";
let questionCache = {}; // Mapea tabId -> cache object

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
    
    if (request.action === "prefetch_question") {
        const tabId = sender.tab.id;
        const qData = request.data;
        
        // Inicializar estado de carga
        questionCache[tabId] = {
            status: "loading",
            questionText: qData.question,
            data: null,
            error: null
        };
        
        // Hacer la petición en background
        fetch(`${API_URL}/api/ai/canvas`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(qData)
        })
        .then(res => res.json())
        .then(data => {
            if (questionCache[tabId] && questionCache[tabId].questionText === qData.question) {
                questionCache[tabId].status = "done";
                questionCache[tabId].data = data;
            }
        })
        .catch(err => {
            if (questionCache[tabId] && questionCache[tabId].questionText === qData.question) {
                questionCache[tabId].status = "error";
                questionCache[tabId].error = err.message;
            }
        });
        
        sendResponse({ received: true });
        return false;
    }
    
    if (request.action === "get_cached_answer") {
        const tabId = request.tabId;
        sendResponse(questionCache[tabId] || null);
        return false;
    }
});

// Limpiar cache si se cierra la pestaña
chrome.tabs.onRemoved.addListener((tabId) => {
    delete questionCache[tabId];
});
