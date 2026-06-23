// Formularios AI Assistant - Content Script
// ATENCIÓN: Este script NUNCA debe ejecutar form.submit() ni hacer click en botones de envío.

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "detect_fields") {
        const fields = detectFields();
        sendResponse({ fields: fields });
    } else if (request.action === "fill_fields") {
        fillFields(request.answers);
        sendResponse({ success: true });
    }
    return true;
});

function detectFields() {
    const fields = [];
    let fieldCounter = 0;
    
    // Selectores para campos estándar
    const inputs = document.querySelectorAll('input:not([type="hidden"]):not([type="submit"]):not([type="button"]), textarea, select, [contenteditable="true"]');
    
    inputs.forEach(el => {
        // Ignorar campos no visibles
        if (el.offsetWidth === 0 || el.offsetHeight === 0) return;
        
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
        
        // Heurística Google Forms básica (buscando div padre con role=heading)
        if (!label) {
            const formContainer = el.closest('[role="listitem"]');
            if (formContainer) {
                const titleEl = formContainer.querySelector('[role="heading"]');
                if (titleEl) label = titleEl.innerText;
            }
        }
        
        const type = el.tagName.toLowerCase() === 'input' ? el.type :
                     el.hasAttribute('contenteditable') ? 'contenteditable' : el.tagName.toLowerCase();
                     
        let options = [];
        if (type === 'select' || type === 'select-one') {
            options = Array.from(el.options).map(o => o.value || o.text);
        } else if (type === 'radio' || type === 'checkbox') {
            options = [el.value];
        }
        
        // Google Forms select workaround (usually very complex, keeping it simple for MVP)

        fields.push({
            fieldId: el.id || fieldId,
            type: type,
            label: label.trim().substring(0, 200), // Evitar labels gigantes
            placeholder: el.placeholder || '',
            ariaLabel: el.getAttribute('aria-label') || '',
            options: options,
            required: el.required || el.getAttribute('aria-required') === 'true',
            selector: selector
        });
    });
    
    return fields;
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
        } else if (type === 'contenteditable') {
            el.innerText = ans.answer;
        } else if (type === 'select' || type === 'select-one') {
            // Find best option matching ans.answer
            const opts = Array.from(el.options);
            const match = opts.find(o => (o.value || o.text).toLowerCase() === String(ans.answer).toLowerCase()) || opts[0];
            if (match) {
                el.value = match.value;
            }
        } else if (type === 'radio' || type === 'checkbox') {
            if (String(el.value).toLowerCase() === String(ans.answer).toLowerCase()) {
                el.checked = true;
            } else if (String(ans.answer).toLowerCase() === 'sí' || String(ans.answer).toLowerCase() === 'yes') {
                el.checked = true;
            }
        }
        
        // Disparar eventos
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
        el.dispatchEvent(new Event('blur', { bubbles: true }));
    });
}
