const API_URL = "http://127.0.0.1:8000";

async function analyzeQuestion() {
    const btn = document.getElementById('btnExecute');
    const loading = document.getElementById('loading');
    const resultArea = document.getElementById('resultArea');
    const ansEl = document.getElementById('canvasAnswer');
    const expEl = document.getElementById('canvasExplanation');
    
    btn.disabled = true;
    loading.style.display = 'block';
    resultArea.style.display = 'none';
    
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        chrome.tabs.sendMessage(tab.id, { action: "detect_canvas_question" }, async (response) => {
            if (chrome.runtime.lastError || !response || !response.question) {
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

// Ejecutar automáticamente al abrir el popup
document.addEventListener('DOMContentLoaded', () => {
    analyzeQuestion();
});

// Permitir re-ejecutar si el usuario hace scroll a otra pregunta sin cerrar el popup
document.getElementById('btnExecute').addEventListener('click', analyzeQuestion);
