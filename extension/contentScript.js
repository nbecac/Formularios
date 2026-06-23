// Formularios AI Assistant - Content Script
// ATENCIÓN: Este script NUNCA debe ejecutar form.submit() ni hacer click en botones de envío.

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    try {
        if (request.action === "detect_fields") {
            const fields = detectFields();
            sendResponse({ fields: fields });
        } else if (request.action === "fill_fields") {
            fillFields(request.answers);
            sendResponse({ success: true });
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
    
    // Selectores para campos estándar
    const inputs = document.querySelectorAll('input:not([type="hidden"]):not([type="submit"]):not([type="button"]), textarea, select, [contenteditable="true"]');
    
    inputs.forEach(el => {
        // Ignorar campos no visibles
        if (el.offsetWidth === 0 || el.offsetHeight === 0) return;
        
        const type = el.tagName.toLowerCase() === 'input' ? el.type :
                     el.hasAttribute('contenteditable') ? 'contenteditable' : el.tagName.toLowerCase();
                     
        const isGroupable = (type === 'radio' || type === 'checkbox') && el.name;
        const groupKey = isGroupable ? el.name : Symbol();
        
        if (fieldsMap.has(groupKey)) {
            const existingField = fieldsMap.get(groupKey);
            existingField.options.push(el.value);
            // Optionally add selectors
            existingField.groupElements = existingField.groupElements || [];
            existingField.groupElements.push(el);
            return;
        }

        fieldCounter++;
        const fieldId = el.id || `auto_field_${fieldCounter}`;
        if (!el.id) el.setAttribute('data-ai-id', fieldId); // Asignar un ID si no tiene
        
        const selector = el.id ? `#${el.id}` : `[data-ai-id="${fieldId}"]`;
        
        // Extraer Label
        let label = '';
        if (el.id) {
            const labelEl = document.querySelector(`label[for="${el.id}"]`);
            if (labelEl) label = labelEl.innerText;
        }
        if (!label) label = el.closest('label')?.innerText || '';
        if (!label) label = el.getAttribute('aria-label') || '';
        if (!label && el.placeholder) label = el.placeholder;
        
        // Heurística básica: texto previo cercano
        if (!label && el.previousElementSibling && el.previousElementSibling.innerText) {
            label = el.previousElementSibling.innerText;
        }
        
        // Heurística de contenedor padre agrupador
        if (!label && isGroupable) {
            const groupContainer = el.closest('fieldset, .form-group, .radio-group, [role="radiogroup"]');
            if (groupContainer) {
                const legend = groupContainer.querySelector('legend, label:first-child');
                if (legend) label = legend.innerText;
            }
        }
        
        // Heurística Google Forms básica
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
            groupElements: [el],
            name: el.name || null
        };
        
        fieldsMap.set(groupKey, fieldObj);
    });
    
    // Clean up internal properties before sending
    return Array.from(fieldsMap.values()).map(f => {
        delete f.groupElements;
        return f;
    });
}

function fillFields(answers) {
    answers.forEach(ans => {
        if (!ans.answer) return;
        
        const el = document.querySelector(`#${ans.fieldId}`) || document.querySelector(`[data-ai-id="${ans.fieldId}"]`);
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
            const match = opts.find(o => (o.value || o.text).toLowerCase() === String(ans.answer).toLowerCase()) || opts[0];
            if (match) {
                el.value = match.value;
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('blur', { bubbles: true }));
            }
        } else if (type === 'radio' || type === 'checkbox') {
            let targets = [el];
            if (el.name) {
                targets = Array.from(document.querySelectorAll(`input[name="${el.name}"]`));
            }
            
            targets.forEach(t => {
                if (String(t.value).toLowerCase() === String(ans.answer).toLowerCase()) {
                    t.checked = true;
                    t.dispatchEvent(new Event('change', { bubbles: true }));
                } else if ((String(ans.answer).toLowerCase() === 'sí' || String(ans.answer).toLowerCase() === 'yes') && (String(t.value).toLowerCase() === 'sí' || String(t.value).toLowerCase() === 'yes')) {
                     t.checked = true;
                     t.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });
        }
    });
}
