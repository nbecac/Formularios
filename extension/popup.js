const API_URL = "http://127.0.0.1:8000";
let currentFields = [];
let currentAnswers = [];

function log(msg) {
    const logsArea = document.getElementById('logsArea');
    logsArea.innerText = msg + '\n' + logsArea.innerText;
}

function setStatus(connected) {
    const badge = document.getElementById('statusBadge');
    if (connected) {
        badge.className = 'badge success';
        badge.innerText = 'Conectado';
    } else {
        badge.className = 'badge error';
        badge.innerText = 'Desconectado';
    }
}

async function apiCall(path, options = {}) {
    try {
        const response = await new Promise((resolve) => {
            chrome.runtime.sendMessage(
                { action: "fetch_api", url: `${API_URL}${path}`, options },
                (res) => resolve(res)
            );
        });
        
        if (!response || response.error) {
            throw new Error(response ? response.error : "Unknown error");
        }
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }
        return response.data;
    } catch (e) {
        console.error("API Call failed:", e);
        throw e;
    }
}

async function checkHealth() {
    try {
        await apiCall('/health');
        setStatus(true);
        loadStudents();
    } catch (e) {
        setStatus(false);
        log("Error conectando al backend local.");
    }
}

async function loadStudents() {
    try {
        const students = await apiCall('/api/students');
        const select = document.getElementById('studentSelect');
        select.innerHTML = '<option value="">Selecciona un alumno...</option>';
        students.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s.id;
            opt.innerText = `${s.name} (${s.course})`;
            select.appendChild(opt);
        });
        select.disabled = false;
        log("Alumnos cargados.");
    } catch(e) {
        log("No se pudieron cargar alumnos.");
    }
}

document.getElementById('btnDetect').addEventListener('click', async () => {
    log("Detectando campos en la página...");
    
    // Get active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) return log("No hay tab activo.");

    // Enviar mensaje al content script
    chrome.tabs.sendMessage(tab.id, { action: "detect_fields" }, async (response) => {
        if (chrome.runtime.lastError) {
            return log("Error: Recarga la página y vuelve a intentar.");
        }
        
        if (response && response.fields) {
            log(`Se detectaron ${response.fields.length} campos.`);
            
            try {
                // Send to backend for normalization
                const resData = await apiCall('/api/forms/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ fields: response.fields })
                });
                
                currentFields = resData.fields;
                document.getElementById('fieldCount').innerText = currentFields.length;
                renderFields(currentFields);
                document.getElementById('btnGenerate').disabled = false;
                log("Campos analizados por el backend.");
            } catch(e) {
                log("Error al analizar campos: " + e.message);
            }
        }
    });
});

document.getElementById('btnGenerate').addEventListener('click', async () => {
    const studentId = document.getElementById('studentSelect').value;
    if (!studentId) {
        return log("Debes seleccionar un alumno primero.");
    }
    
    log("Generando respuestas...");
    
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    try {
        const response = await apiCall('/api/forms/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                fields: currentFields,
                student_id: parseInt(studentId),
                url: tab.url,
                page_title: tab.title
            })
        });
        
        currentAnswers = response.answers;
        log(`Se generaron ${currentAnswers.length} respuestas.`);
        renderFields(currentFields, currentAnswers);
        document.getElementById('btnFill').disabled = false;
    } catch(e) {
        log("Error al generar respuestas: " + e.message);
    }
});

document.getElementById('btnFill').addEventListener('click', async () => {
    log("Rellenando borrador...");
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    chrome.tabs.sendMessage(tab.id, { action: "fill_fields", answers: currentAnswers }, async (response) => {
        if (response && response.success) {
            log("Campos rellenados (borrador).");
            
            // Guardar historial
            try {
                const studentId = document.getElementById('studentSelect').value;
                await apiCall('/api/history', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        url: tab.url,
                        page_title: tab.title,
                        student_id: parseInt(studentId),
                        detected_fields_json: JSON.stringify(currentFields),
                        generated_answers_json: JSON.stringify(currentAnswers)
                    })
                });
                log("Historial guardado.");
            } catch(e) {
                log("No se pudo guardar el historial.");
            }
        } else {
            log("Error al rellenar campos.");
        }
    });
});

document.getElementById('btnClear').addEventListener('click', () => {
    currentFields = [];
    currentAnswers = [];
    renderFields([]);
    document.getElementById('fieldCount').innerText = '0';
    document.getElementById('btnGenerate').disabled = true;
    document.getElementById('btnFill').disabled = true;
    log("Sugerencias limpiadas.");
});

function renderFields(fields, answers = []) {
    const list = document.getElementById('fieldList');
    list.innerHTML = '';
    
    if (fields.length === 0) {
        list.innerHTML = '<p class="empty-state">No hay campos detectados.</p>';
        return;
    }
    
    fields.forEach(f => {
        const item = document.createElement('div');
        item.className = 'field-item';
        
        const ans = answers.find(a => a.fieldId === f.fieldId);
        
        item.innerHTML = `
            <span class="label">${f.normalizedLabel || 'Sin nombre'} (${f.normalizedType})</span>
            ${ans ? `<span class="answer">Sugerencia: ${ans.answer || '[Vacio]'}</span>` : ''}
        `;
        list.appendChild(item);
    });
}

// Inicializar
checkHealth();
