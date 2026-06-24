chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    try {
        if (request.action === "detect_fields") {
            const fields = detectFields();
            sendResponse({ fields: fields });
        } else if (request.action === "fill_fields") {
            fillFields(request.answers);
            sendResponse({ success: true });
        } else if (request.action === "detect_canvas_question") {
            sendResponse(extractMultipleChoiceQuestion());
        }
    } catch (e) {
        console.error("Content Script Error:", e);
        sendResponse({ error: "Error en content script: " + e.message });
    }
    return true;
});

function detectFields() {
    const fieldsMap = new Map();
    let fieldCounter = 0;
    
    const inputs = document.querySelectorAll('input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="reset"]), textarea, select, [contenteditable="true"]');
    
    inputs.forEach(el => {
        if (el.offsetWidth === 0 || el.offsetHeight === 0) return;
        
        const type = el.tagName.toLowerCase() === 'input' ? el.type :
                     el.hasAttribute('contenteditable') ? 'contenteditable' : el.tagName.toLowerCase();
                     
        const isGroupable = (type === 'radio' || type === 'checkbox') && el.name;
        const groupKey = isGroupable ? el.name : Symbol();
        
        if (fieldsMap.has(groupKey)) {
            const existingField = fieldsMap.get(groupKey);
            existingField.options.push(el.value);
            return;
        }

        fieldCounter++;
        const fieldId = el.id || "auto_field_" + fieldCounter;
        if (!el.id) el.setAttribute('data-ai-id', fieldId);
        
        const selector = el.id ? "#" + el.id : "[data-ai-id='" + fieldId + "']";
        
        let label = '';
        if (el.id) {
            const labelEl = document.querySelector("label[for='" + el.id + "']");
            if (labelEl) label = labelEl.innerText;
        }
        if (!label) {
            const closestLabel = el.closest('label');
            if (closestLabel) label = closestLabel.innerText;
        }
        if (!label) label = el.getAttribute('aria-label') || '';
        if (!label && el.placeholder) label = el.placeholder;
        
        if (!label && el.previousElementSibling && el.previousElementSibling.innerText) {
            label = el.previousElementSibling.innerText;
        }
        
        if (!label && isGroupable) {
            const groupContainer = el.closest('fieldset, .form-group, .radio-group, [role="radiogroup"]');
            if (groupContainer) {
                const legend = groupContainer.querySelector('legend, label:first-child');
                if (legend) label = legend.innerText;
            }
        }
        
        if (!label) {
            const formContainer = el.closest('[role="listitem"]');
            if (formContainer) {
                const titleEl = formContainer.querySelector('[role="heading"]');
                if (titleEl) label = titleEl.innerText;
            }
        }
        
        let options = [];
        if (type === 'select' || type === 'select-one') {
            options = Array.from(el.options).map(o => o.value || o.text);
        } else if (type === 'radio' || type === 'checkbox') {
            options = [el.value];
        }

        const fieldObj = {
            fieldId: el.id || fieldId,
            type: type,
            label: label.trim().substring(0, 200),
            placeholder: el.placeholder || '',
            ariaLabel: el.getAttribute('aria-label') || '',
            options: options,
            required: el.required || el.getAttribute('aria-required') === 'true',
            selector: selector,
            name: el.name || null
        };
        
        fieldsMap.set(groupKey, fieldObj);
    });
    
    return Array.from(fieldsMap.values());
}

function fillFields(answers) {
    // REGLA DE SEGURIDAD ABSOLUTA: PROHIBIDO MARCAR CHECKBOX O RADIO AUTOMATICAMENTE
    answers.forEach(ans => {
        if (!ans.answer) return;
        
        const el = document.querySelector("#" + ans.fieldId) || document.querySelector("[data-ai-id='" + ans.fieldId + "']");
        if (!el) return;
        
        const type = el.tagName.toLowerCase() === 'input' ? el.type :
                     el.hasAttribute('contenteditable') ? 'contenteditable' : el.tagName.toLowerCase();
                     
        if (type === 'text' || type === 'textarea' || type === 'email' || type === 'number' || type === 'date') {
            el.value = ans.answer;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            el.dispatchEvent(new Event('blur', { bubbles: true }));
        } else if (type === 'contenteditable') {
            el.innerText = ans.answer;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            el.dispatchEvent(new Event('blur', { bubbles: true }));
        } else if (type === 'select' || type === 'select-one') {
            const opts = Array.from(el.options);
            const match = opts.find(o => String(o.value || o.text).toLowerCase() === String(ans.answer).toLowerCase()) || opts[0];
            if (match) {
                el.value = match.value;
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('blur', { bubbles: true }));
            }
        }
        // Eliminado intencionalmente el soporte para type === 'radio' || type === 'checkbox' para evitar autollenado inseguro.
    });
}

function extractMultipleChoiceQuestion() {
    let qText = '';
    let options = [];
    let qType = 'unknown';
    let selectionMode = 'single';
    
    // Buscar contenedores comunes de preguntas
    const containers = document.querySelectorAll('.question:not(.answered_question), .display_question, .multiple-choice-question, fieldset');
    
    let questionContainer = null;
    let minDistanceToCenter = Infinity;
    const viewportCenterY = window.innerHeight / 2;
    
    containers.forEach(container => {
        const rect = container.getBoundingClientRect();
        if (rect.width > 0 && rect.height > 0) {
            // Check if it's at least partially in the viewport
            if (rect.top < window.innerHeight && rect.bottom > 0) {
                const containerCenterY = rect.top + (rect.height / 2);
                const distance = Math.abs(viewportCenterY - containerCenterY);
                if (distance < minDistanceToCenter) {
                    minDistanceToCenter = distance;
                    questionContainer = container;
                }
            }
        }
    });
    
    // Fallback al primero si nada est visible (ej. scroll extrao)
    if (!questionContainer && containers.length > 0) {
        questionContainer = containers[0];
    }
    
    if (questionContainer) {
        const titleEl = questionContainer.querySelector('.question_text, legend, h3, h2, .title');
        if (titleEl) qText = titleEl.innerText;
        
        const inputs = questionContainer.querySelectorAll('input[type="radio"], input[type="checkbox"]');
        if (inputs.length > 0) {
            qType = 'multiple_choice';
            selectionMode = inputs[0].type === 'checkbox' ? 'multiple' : 'single';
            
            inputs.forEach(i => {
                let labelText = '';
                
                // Intento 1: label for
                if (i.id) {
                    const labelEl = questionContainer.querySelector(`label[for="${i.id}"]`);
                    if (labelEl) labelText = labelEl.innerText;
                }
                
                // Intento 2: label padre
                if (!labelText) {
                    const parentLabel = i.closest('label');
                    if (parentLabel) labelText = parentLabel.innerText;
                }
                
                // Intento 3: texto siguiente
                if (!labelText && i.nextSibling && i.nextSibling.nodeType === 3) {
                    labelText = i.nextSibling.textContent.trim();
                }
                
                // Limpiar texto y buscar patron A/B/C/D
                labelText = labelText.trim();
                let labelLetter = i.value || `Opt_${options.length + 1}`;
                
                // Si el label visible empieza por A) o B), lo usamos como identificador corto
                const match = labelText.match(/^([A-E])[\)\.]?\s+(.*)/i);
                if (match) {
                    labelLetter = match[1].toUpperCase();
                    labelText = match[2];
                }

                options.push({
                    label: labelLetter,
                    text: labelText
                });
            });
        } else if (questionContainer.querySelector('textarea, input[type="text"]')) {
            qType = 'text';
        }
    } else {
        // Fallback genérico si no hay contenedor visible
        const activeField = document.activeElement;
        if (activeField && (activeField.tagName === 'INPUT' || activeField.tagName === 'TEXTAREA')) {
            const labelEl = document.querySelector(`label[for="${activeField.id}"]`);
            if (labelEl) qText = labelEl.innerText;
            else qText = activeField.placeholder || activeField.getAttribute('aria-label') || '';
            qType = activeField.type || activeField.tagName.toLowerCase();
        }
    }
    
    return {
        question: qText.trim().substring(0, 500),
        options: options,
        question_type: qType,
        selection_mode: selectionMode
    };
}

// Lógica de pre-fetch (observador de scroll)
// Usamos var en vez de let para que no tire error si el script se re-inyecta
var prefetchTimeout = null;
var lastPrefetchedQuestion = null;

function handleScrollDebounced() {
    clearTimeout(prefetchTimeout);
    prefetchTimeout = setTimeout(() => {
        const qData = extractMultipleChoiceQuestion();
        if (qData && qData.question && qData.question !== lastPrefetchedQuestion) {
            lastPrefetchedQuestion = qData.question;
            chrome.runtime.sendMessage({
                action: "prefetch_question",
                data: qData
            });
        }
    }, 800); // Esperar 800ms tras dejar de scrollear
}

// Remover listeners anteriores si es una re-inyección
window.removeEventListener('scroll', handleScrollDebounced);
window.addEventListener('scroll', handleScrollDebounced, { passive: true });
setTimeout(handleScrollDebounced, 1000); // Disparar una vez que cargue la página
