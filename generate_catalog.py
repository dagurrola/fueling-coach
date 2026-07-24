#!/usr/bin/env python3
"""Regenera el bloque CATALOGO de index.html desde dacoach/fueling_catalog.json.

R-43 ítem 3: el widget tenía el catálogo copiado a mano — dos fuentes de verdad,
deriva garantizada (mismo patrón de falla silenciosa de R-35/R-37/R-38). Este
script hace que las CIFRAS (carbs_g) salgan siempre de fueling_catalog.json;
la curación editorial (grupo/porque/limpieza/unidad de despliegue) no existe en
el catálogo crudo — vive aquí, en CURATION.

Nota: consolidado 2026-07-23 — existía una versión duplicada en OC/Runcierge/
(otra sesión, 21 jul) apuntando a una copia espejo del HTML, no al repo real.
Esta es la única versión canónica, vive en el repo con remote a GitHub.

Uso: correr después de cualquier cambio a fueling_catalog.json o a CURATION.
    python3 generate_catalog.py
"""
import json
import re
from pathlib import Path

CATALOGO_JSON = Path("/Users/dagurrola/Desktop/OC/dacoach/fueling_catalog.json")
HTML = Path(__file__).parent / "index.html"

# Selección curada para el widget (9 productos, 3 grupos). Cada entrada apunta a
# un nombre EXACTO en fueling_catalog.json (lista "oficiales" o "real_food") —
# el generador falla fuerte si no lo encuentra, en vez de dejar el número viejo.
CURATION = [
    {
        "nombre": "Papas a la sal", "fuente_lista": "real_food",
        "fuente_nombre": "Papas a la sal (Sabritas Original)",
        "unidad": "bolsa 45g", "plural": "bolsas", "grupo": "Comida real",
        "porque": "almidón puro + sodio, cero fructosa — el perfil más limpio para el estómago en sesiones largas",
        "limpieza": 2,
    },
    {
        "nombre": "SIS GO Isotonic", "fuente_lista": "oficiales",
        "fuente_nombre": "SIS GO Isotonic Gel",
        "unidad": "gel", "plural": "geles", "grupo": "Gel deportivo",
        "porque": "maltodextrina, isotónico — no necesita agua extra para digerirse",
        "limpieza": 2,
    },
    {
        "nombre": "GU Energy Gel", "fuente_lista": "oficiales",
        "fuente_nombre": "GU Energy Gel",
        "unidad": "gel", "plural": "geles", "grupo": "Gel deportivo",
        "porque": "clásico, fácil de conseguir en MX; algo de fructosa pero balanceado",
        "limpieza": 1,
    },
    {
        "nombre": "Maurten Gel 100", "fuente_lista": "oficiales",
        "fuente_nombre": "Maurten Gel 100",
        "unidad": "gel", "plural": "geles", "grupo": "Gel deportivo",
        "porque": "hidrogel diseñado para absorción alta; más fructosa relativa, mejor a carga alta",
        "limpieza": 0,
    },
    {
        "nombre": "Precision PF 30", "fuente_lista": "oficiales",
        "fuente_nombre": "Precision Fuel & Hydration PF 30 Gel",
        "unidad": "gel", "plural": "geles", "grupo": "Gel deportivo",
        "porque": "30g por gel — menos sobres para el mismo total; ratio 2:1 glucosa:fructosa",
        "limpieza": 1,
    },
    {
        "nombre": "Dátil Medjool", "fuente_lista": "real_food",
        "fuente_nombre": "Dátil Medjool",
        "unidad": "pieza", "plural": "dátiles", "grupo": "Comida real",
        "porque": "natural, denso, con potasio; fructosa alta — mejor combinado con algo de glucosa",
        "limpieza": 0,
    },
    {
        "nombre": "Plátano mediano", "fuente_lista": "real_food",
        "fuente_nombre": "Plátano mediano",
        "unidad": "pieza", "plural": "plátanos", "grupo": "Comida real",
        "porque": "barato y accesible; mejor en la primera hora, luego el volumen estorba",
        "limpieza": 1,
    },
    {
        "nombre": "Gomitas", "fuente_lista": "real_food",
        "fuente_nombre": "Gomitas (gummy bears, Sour Patch, Nerds Gummy Clusters)",
        "unidad": "puño 40g", "plural": "puños", "grupo": "Comida real",
        "porque": "azúcar rápido y barato; rompe la fatiga de comer solo geles. Suma sodio aparte",
        "limpieza": 1,
    },
    {
        "nombre": "Tailwind (mezcla)", "fuente_lista": "oficiales",
        "fuente_nombre": "Tailwind Endurance Fuel",
        "unidad": "porción", "plural": "porciones", "grupo": "Bebida",
        "porque": "carbs + sodio en el mismo líquido — resuelve hidratación y fuel de un solo golpe",
        "limpieza": 1,
    },
]


def _carbs_g(raw):
    """Extrae un entero de carbs_g del catálogo crudo — puede ser int, string
    'lo-hi', o dict {"valor": ...} en cualquiera de esas dos formas."""
    valor = raw.get("carbs_g") if isinstance(raw, dict) and "carbs_g" in raw else raw
    if isinstance(valor, dict):
        valor = valor.get("valor")
    if isinstance(valor, (int, float)):
        return round(valor)
    if isinstance(valor, str):
        m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*$", valor)
        if m:
            return round((float(m.group(1)) + float(m.group(2))) / 2)
        return round(float(valor))
    raise ValueError(f"carbs_g no parseable: {valor!r}")


def _buscar(catalogo, lista, nombre_exacto):
    clave = "producto" if lista == "oficiales" else "alimento"
    for item in catalogo[lista]:
        if item.get(clave) == nombre_exacto:
            return item
    raise KeyError(f"'{nombre_exacto}' no encontrado en fueling_catalog.json[{lista}]")


def generar():
    catalogo = json.loads(CATALOGO_JSON.read_text(encoding="utf-8"))

    filas = []
    for c in CURATION:
        item = _buscar(catalogo, c["fuente_lista"], c["fuente_nombre"])
        carbs = _carbs_g(item)
        filas.append(
            '  { nombre: "%s", carbs_g: %d, unidad: "%s", plural: "%s", grupo: "%s", '
            'porque: "%s", limpieza: %d },'
            % (c["nombre"], carbs, c["unidad"], c["plural"], c["grupo"], c["porque"], c["limpieza"])
        )

    bloque = "const CATALOGO = [\n" + "\n".join(filas) + "\n];"

    html = HTML.read_text(encoding="utf-8")
    patron = re.compile(
        r"(// CATALOGO:START\n).*?(\n// CATALOGO:END)", re.DOTALL
    )
    if not patron.search(html):
        raise RuntimeError("Marcadores CATALOGO:START/END no encontrados en index.html")
    html_nuevo = patron.sub(lambda m: m.group(1) + bloque + m.group(2), html)
    HTML.write_text(html_nuevo, encoding="utf-8")
    print(f"Catálogo regenerado — {len(filas)} productos, fuente: {CATALOGO_JSON}")


if __name__ == "__main__":
    generar()
