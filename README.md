# Fueling Coach

Calculadora de fueling para trail running: cuánto carbohidrato y líquido llevar por hora, y qué producto usar — calculado, no adivinado.

## Segmento
Corredores de trail (principiante a avanzado) que necesitan un plan de fueling para una sesión de entreno o competencia.

## Scope
- Cuestionario (nivel de experiencia, tipo de sesión, duración, terreno/temperatura)
- Cálculo determinista de carbs/h y líquido/h (mismas bandas que el motor real de Runcierge)
- Abanico de productos (comida real / gel deportivo / bebida) con unidades prácticas y fuentes
- CTA a waitlist + analytics mínimos

## Agentes
- KOHD: Tech Lead — construcción
- LUMEN: Design Lead — wireframes
- AXIS: PM — coordinación y documentación en Notion

## Nota
El widget es standalone y determinista (cero LLM en runtime). El catálogo de productos se genera desde una fuente de datos privada (`dacoach/fueling_catalog.json`, en el repo interno) vía `generar_catalogo_fueling.py` — ese generador y su fuente no viven en este repo público; aquí solo está el artefacto compilado (`index.html`).
