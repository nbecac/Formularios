import os
import json
from dotenv import load_dotenv
load_dotenv('.env')
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

evidence = """
--- [memoria_maestra] NO AFIRMAR ---
* NO afirmes el uso de React, Angular, Vue, etc (el frontend es PHP puro + HTML + CSS).
* NO afirmes que hay Entrega 4 (el proyecto llega hasta la E3).
"""

system_prompt = f"""Eres un asistente experto evaluando una pregunta de selección múltiple sobre un proyecto de Base de Datos.
REGLA 1: Prioriza la información que provenga de la sección "memoria_maestra".
REGLA 2: No inventes hechos específicos.
REGLA 3: Tu respuesta debe categorizarse en uno de los siguientes tres niveles y usar la 'confidence' indicada:
1. Evidencia directa: Tienes la prueba exacta en la evidencia. Elige la alternativa. confidence = 0.70 a 0.90
2. Inferencia razonable: No hay prueba explícita, pero por descarte o lógica fundamentada en la evidencia, una alternativa es claramente la mejor. Elige la alternativa. explanation DEBE decir "inferencia por descarte" o "inferencia razonable". confidence = 0.35 a 0.55
3. Sin evidencia suficiente: No hay cómo decidir o es una pregunta trampa (e.g. herramientas no usadas). selected_option = null. confidence = 0.0 a 0.25. explanation debe indicar qué falta o por qué es trampa.

Evidencia extraida:
{evidence}
"""

def test_q(q, opts):
    print(f"Testing: {q}")
    options_text = json.dumps(opts, ensure_ascii=False)
    user_prompt = f"Pregunta: {q}\nOpciones:\n{options_text}"
    
    res = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=system_prompt + "\n\n" + user_prompt,
        config=types.GenerateContentConfig(response_mime_type='application/json')
    )
    print(res.text)

test_q(
    "¿Cuál es el comando exacto para clonar el repositorio de React nativo utilizado en la interfaz de la E4?",
    [
        {"label": "A", "text": "npx create-react-app frontend-dccolo"},
        {"label": "B", "text": "git clone https://github.com/dccolo/react-app.git"},
        {"label": "C", "text": "npm install react-native-cli"},
        {"label": "D", "text": "vue create frontend-app"}
    ]
)
