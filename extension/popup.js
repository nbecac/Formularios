const API_URL = "http://127.0.0.1:8000";
let currentFields = [];
let currentAnswers = [];

const diagBackend = document.getElementById('diagBackend');
const diagUrl = document.getElementById('diagUrl');
const diagFields = document.getElementById('diagFields');
const diagStudent = document.getElementById('diagStudent');
const diagBackendResp = document.getElementById('diagBackendResp');
const diagError = document.getElementById('diagError');
const diagCs = document.getElementById('diagCs');

function log(msg) {
    const logsArea = document.getElementById('logsArea');
    logsArea.innerText = msg + '\n' + logsArea.innerText;
}

function setError(msg) {
    log("ERROR: " + msg);
    diagError.innerText = msg;
    console.error(msg);
}

function setStatus(connected) {
    const badge = document.getElementById('statusBadge');
    if (connected) {
        badge.className = 'badge success';
        badge.innerText = 'Conectado';
        diagBackend.innerText = 'Sí';
    } else {
        badge.className = 'badge error';
        badge.innerText = 'Desconectado';
        diagBackend.innerText = 'No';
    }
}

async function apiCall(path, options = {}) {
    try {
        const response = await new Promise((resolve) => {
            chrome.runtime.sendMessage(
                { action: "fetch_api", url: API_URL + path, options: options },
                (res) => {
                    if (chrome.runtime.lastError) {
                        resolve({ ok: false, error: chrome.runtime.lastError.message });
                    } else {
                        resolve(res);
                    }
                }
            );
        });
        
        if (!response) throw new Error("No hay respuesta del Service Worker.");
        if (response.error) throw new Error(response.error);
        if (!response.ok) throw new Error("HTTP " + response.status);
        
        diagBackendResp.innerText = String(response.status || "") + " OK";
        return response.data;
    } catch (e) {
        diagBackendResp.innerText = "Error";
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
        setError("No se pudo conectar al backend.");
    }
}

document.getElementById('btnTestConn').addEventListener('click', async () => {
    log("Probando conexión...");
    try {
        const data = await apiCall('/health');
        if (data && data.status === 'ok') {
            log("Conectado correctamente.");
            setStatus(true);
        } else {
            setError("Backend no responde correctamente.");
        }
    } catch(e) {
        setError("Error de conexión. " + e.message);
        setStatus(false);
    }
});

async function loadStudents() {
    try {
        const students = await apiCall('/api/students');
        const select = document.getElementById('studentSelect');
        select.innerHTML = '<option value="">Selecciona un alumno...</option>';
        if (students.length === 0) {
            select.innerHTML = '<option value="">No hay alumnos en la BD</option>';
            select.disabled = true;
            log("No hay alumnos registrados.");
        } else {
            students.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s.id;
                opt.innerText = (s.name || "Alumno " + s.id);
                select.appendChild(opt);
            });
            select.disabled = false;
            log("Alumnos cargados.");
        }
    } catch(e) {
        setError("No se pudieron cargar alumnos.");
    }
}

document.getElementById('btnReloadStudents').addEventListener('click', () => {
    log("Recargando alumnos...");
    loadStudents();
});

document.getElementById('studentSelect').addEventListener('change', (e) => {
    const sel = e.target;
    diagStudent.innerText = sel.options[sel.selectedIndex].text;
});

document.getElementById('btnDetect').addEventListener('click', async () => {
    log("Detectando campos...");
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) return setError("No hay tab activo.");
    
    diagUrl.innerText = tab.url.substring(0, 30) + "...";

    chrome.tabs.sendMessage(tab.id, { action: "detect_fields" }, async (response) => {
        if (chrome.runtime.lastError) {
            diagCs.innerText = 'No cargado / Bloqueado';
            return setError("Error CS: Recarga página o permite URLs de archivo.");
        }
        
        diagCs.innerText = 'Cargado';
        
        if (response && response.fields) {
            if (response.fields.length === 0) return setError("No se detectaron campos.");
            log("Detectados " + response.fields.length + " campos.");
            
            try {
                const resData = await apiCall('/api/forms/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ fields: response.fields })
                });
                
                currentFields = resData.fields;
                document.getElementById('fieldCount').innerText = currentFields.length;
                diagFields.innerText = currentFields.length;
                renderFields(currentFields);
                document.getElementById('btnGenerate').disabled = false;
            } catch(e) {
                setError("Error al analizar: " + e.message);
            }
        }
    });
});

document.getElementById('btnGenerate').addEventListener('click', async () => {
    const studentId = document.getElementById('studentSelect').value;
    if (!studentId) return setError("No hay alumno seleccionado.");
    
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
        log("Se generaron " + currentAnswers.length + " respuestas.");
        renderFields(currentFields, currentAnswers);
        document.getElementById('btnFill').disabled = false;
    } catch(e) {
        setError("Error al generar: " + e.message);
    }
});

document.getElementById('btnFill').addEventListener('click', async () => {
    log("Rellenando borrador...");
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    chrome.tabs.sendMessage(tab.id, { action: "fill_fields", answers: currentAnswers }, async (response) => {
        if (chrome.runtime.lastError) return setError("El content script falló al rellenar.");
        
        if (response && response.success) {
            log("Campos rellenados.");
            try {
                await apiCall('/api/history', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        url: tab.url,
                        page_title: tab.title,
                        student_id: parseInt(document.getElementById('studentSelect').value),
                        detected_fields_json: JSON.stringify(currentFields),
                        generated_answers_json: JSON.stringify(currentAnswers)
                    })
                });
            } catch(e) {
                console.error("Historial falló", e);
            }
        } else {
            setError("Error al rellenar en la página.");
        }
    });
});

document.getElementById('btnClear').addEventListener('click', () => {
    currentFields = [];
    currentAnswers = [];
    renderFields([]);
    document.getElementById('fieldCount').innerText = '0';
    diagFields.innerText = '0';
    document.getElementById('btnGenerate').disabled = true;
    document.getElementById('btnFill').disabled = true;
    log("Sugerencias limpiadas.");
    diagError.innerText = '-';
});

function renderFields(fields, answers = []) {
    const list = document.getElementById('fieldList');
    list.innerHTML = '';
    
    if (fields.length === 0) {
        const p = document.createElement('p');
        p.className = 'empty-state';
        p.innerText = 'No hay campos detectados.';
        list.appendChild(p);
        return;
    }
    
    fields.forEach(f => {
        const item = document.createElement('div');
        item.className = 'field-item';
        
        const spanLabel = document.createElement('span');
        spanLabel.className = 'label';
        spanLabel.innerText = (f.normalizedLabel || "Sin nombre") + " (" + (f.type || "") + ")";
        item.appendChild(spanLabel);
        
        const ans = answers.find(a => a.fieldId === f.fieldId);
        if (ans) {
            const spanAns = document.createElement('span');
            spanAns.className = 'answer';
            spanAns.innerText = "Sugerencia: " + (ans.value || ans.answer || "");
            item.appendChild(document.createElement('br'));
            item.appendChild(spanAns);
            
            const spanMeta = document.createElement('span');
            spanMeta.style.fontSize = '0.75rem';
            spanMeta.style.color = '#6b7280';
            spanMeta.style.display = 'block';
            spanMeta.style.marginTop = '0.25rem';
            spanMeta.innerText = "Fuente: " + (ans.source || "-") + " - " + (ans.explanation || "");
            item.appendChild(spanMeta);
        }
        list.appendChild(item);
    });
}

checkHealth();

// ----- CANVAS MODE LOGIC -----
const btnDetectCanvas = document.getElementById('btnDetectCanvas');
const btnGenerateCanvas = document.getElementById('btnGenerateCanvas');
const canvasResponseArea = document.getElementById('canvasResponseArea');
const canvasAnswer = document.getElementById('canvasAnswer');
const canvasExplanation = document.getElementById('canvasExplanation');
const canvasSources = document.getElementById('canvasSources');

let currentCanvasQuestion = null;

function logMsg(msg) {
    log(msg);
}

if (btnDetectCanvas) {
    btnDetectCanvas.addEventListener('click', async () => {
        logMsg("Detectando pregunta de Canvas...");
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        chrome.tabs.sendMessage(tab.id, { action: "detect_canvas_question" }, response => {
            if (chrome.runtime.lastError) {
                logMsg("Error en tab: " + chrome.runtime.lastError.message);
                return;
            }
            if (response && response.question) {
                currentCanvasQuestion = response;
                let detMsg = "Pregunta detectada: " + response.question.substring(0, 50) + "...";
                if (response.options && response.options.length > 0) {
                    detMsg += "\nAlternativas detectadas: " + response.options.length + " (" + response.selection_mode + ")";
                }
                logMsg(detMsg);
                btnGenerateCanvas.disabled = false;
            } else {
                logMsg("No se detectó pregunta clara.");
            }
        });
    });
}

if (btnGenerateCanvas) {
    btnGenerateCanvas.addEventListener('click', async () => {
        if (!currentCanvasQuestion) return;
        logMsg("Sugerencia solicitada. Consultando backend...");
        btnGenerateCanvas.disabled = true;
        
        try {
            const resData = await apiCall('/api/ai/canvas', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(currentCanvasQuestion)
            });
            
            canvasResponseArea.style.display = 'block';
            canvasAnswer.innerText = resData.answer || 'Sin respuesta';
            
            let explText = "Confianza: " + resData.confidence.toFixed(2);
            if (resData.explanation) {
                explText += "\nMotivo: " + resData.explanation;
            }
            if (resData.question_type === 'multiple_choice' && currentCanvasQuestion.selection_mode === 'multiple') {
                explText += "\n\nADVERTENCIA: Pregunta de selección múltiple detectada. Revisa manualmente las opciones sugeridas.";
            }
            canvasExplanation.innerText = explText;
            
            if (resData.sources && resData.sources.length > 0) {
                canvasSources.innerHTML = "<strong>Fuentes:</strong><br>" + 
                    resData.sources.map(s => "- [" + s.section + "] " + s.filename).join("<br>");
            } else {
                canvasSources.innerHTML = "<em>Sin fuentes locales encontradas.</em>";
            }
            
            logMsg("Sugerencia mostrada. Acción manual requerida.");
        } catch (e) {
            logMsg("Error al generar: " + e.message);
        } finally {
            btnGenerateCanvas.disabled = false;
        }
    });
}
