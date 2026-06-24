const API_URL = "http://127.0.0.1:8000";

let pollInterval = null;

async function checkCacheAndRender() {
    const btn = document.getElementById('btnExecute');
    const loading = document.getElementById('loading');
    const resultArea = document.getElementById('resultArea');
    const ansEl = document.getElementById('canvasAnswer');
    const expEl = document.getElementById('canvasExplanation');
    
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        chrome.runtime.sendMessage({ action: "get_cached_answer", tabId: tab.id }, (cache) => {
            if (!cache) {
                // No hay cache, fallback a analisis manual/directo
                analyzeQuestion();
                return;
            }
            
            if (cache.status === "loading") {
                btn.disabled = true;
                loading.style.display = 'block';
                resultArea.style.display = 'none';
                
                // Seguir esperando
                if (!pollInterval) {
                    pollInterval = setInterval(checkCacheAndRender, 500);
                }
                return;
            }
            
            // Ya cargó, limpiar intervalo
            if (pollInterval) {
                clearInterval(pollInterval);
                pollInterval = null;
            }
            
            loading.style.display = 'none';
            btn.disabled = false;
            resultArea.style.display = 'block';
            
            if (cache.status === "error") {
                ansEl.innerText = "❌ Error Backend";
                expEl.innerText = cache.error || "Asegúrate de que el backend esté corriendo.";
                return;
            }
            
            const data = cache.data;
            if (data && data.selected_option) {
                ansEl.innerText = `🎯 Alternativa: ${data.selected_option}`;
            } else {
                ansEl.innerText = `🤔 Dudoso`;
            }
            
            expEl.innerText = (data && data.explanation) ? data.explanation : "No hay explicación.";
        });
    } catch (e) {
        console.error(e);
        analyzeQuestion();
    }
}

async function analyzeQuestion() {
    const btn = document.getElementById('btnExecute');
    const loading = document.getElementById('loading');
    const resultArea = document.getElementById('resultArea');
    const ansEl = document.getElementById('canvasAnswer');
    const expEl = document.getElementById('canvasExplanation');
    
    if (pollInterval) clearInterval(pollInterval);
    
    btn.disabled = true;
    loading.style.display = 'block';
    resultArea.style.display = 'none';
    
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        chrome.tabs.sendMessage(tab.id, { action: "detect_canvas_question" }, async (response) => {
            if (chrome.runtime.lastError) {
                loading.style.display = 'none';
                btn.disabled = false;
                resultArea.style.display = 'block';
                ansEl.innerText = "⚠️ Extensión Desconectada";
                expEl.innerText = "Por favor, RECARGA ESTA PÁGINA (F5) para que la nueva versión de la extensión se conecte correctamente.";
                return;
            }
            if (!response || !response.question) {
                loading.style.display = 'none';
                btn.disabled = false;
                resultArea.style.display = 'block';
                ansEl.innerText = "⚠️ No detectado";
                expEl.innerText = "Haz scroll en la página para centrar bien la pregunta en la pantalla y vuelve a intentarlo.";
                return;
            }
            
            try {
                const res = await fetch(`${API_URL}/api/ai/canvas`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(response)
                });
                
                const data = await res.json();
                
                loading.style.display = 'none';
                btn.disabled = false;
                resultArea.style.display = 'block';
                
                if (data.selected_option) {
                    ansEl.innerText = `🎯 Alternativa: ${data.selected_option}`;
                } else {
                    ansEl.innerText = `🤔 Dudoso`;
                }
                
                expEl.innerText = data.explanation || "No hay explicación.";
                
            } catch (err) {
                loading.style.display = 'none';
                btn.disabled = false;
                resultArea.style.display = 'block';
                ansEl.innerText = "❌ Error Backend";
                expEl.innerText = "Asegúrate de que el backend (02_start_backend.bat) esté corriendo en puerto 8000.";
            }
        });
    } catch (e) {
        loading.style.display = 'none';
        btn.disabled = false;
        resultArea.style.display = 'block';
        ansEl.innerText = "Error";
        expEl.innerText = e.message;
    }
}

// En lugar de ejecutar de cero, revisamos si ya hay respuesta cacheadas
document.addEventListener('DOMContentLoaded', () => {
    checkCacheAndRender();
});

// Permitir forzar el analisis (botón "Volver a Analizar")
document.getElementById('btnExecute').addEventListener('click', analyzeQuestion);
