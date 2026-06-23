// background.js maneja la comunicación con el backend si es necesario, 
// o simplemente sirve como proxy seguro para peticiones.

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "fetch_api") {
        fetch(request.url, request.options)
            .then(res => res.json().then(data => ({ status: res.status, ok: res.ok, data })))
            .then(response => sendResponse(response))
            .catch(error => sendResponse({ error: error.message }));
        return true; // Keep the messaging channel open for sendResponse
    }
});
