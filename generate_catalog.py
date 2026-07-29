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
    # R-47 (Jona): faltaba un drink mix ALTO en carbos — "aportan 80-90 por toma
    # y ya quitas 6 geles". De los 7 de oficiales_extendido.bebidas_polvo este es
    # el ÚNICO con carbs_g confirmado:true; los otros son estimados de la fuente.
    # Se agrega solo este a propósito: meter 6 cifras estimadas al widget iría
    # contra la disciplina del catálogo. Aviso de disponibilidad en el "porque"
    # porque la sección extendido declara "no como catálogo de compra inmediata
    # en MX" (la marca sí tiene presencia MX, este SKU no está verificado).
    {
        "nombre": "Maurten Drink Mix 320", "fuente_lista": "oficiales_extendido.bebidas_polvo",
        "fuente_nombre": "Drink Mix 320",
        "unidad": "sobre", "plural": "sobres", "grupo": "Bebida",
        "porque": "80g en un solo sobre — cubre casi toda la sesión sin cargar geles; premium e importado, confirma disponibilidad antes de contar con él",
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


def _sodio(item):
    """Extrae el sodio del catálogo para mostrarlo en el widget (R-46).

    NO inventa ni normaliza: el catálogo trae los valores en formas distintas
    (int, rango 'lo-hi', o string con variantes por SKU tipo '10 (estándar) /
    118 (Energy+Electrolyte)'). Devolvemos dos cosas:
      - `label`: versión corta para la fila (solo la cifra/rango, sin paréntesis)
      - `detalle`: el string COMPLETO del catálogo, va en el title= del elemento
        para no perder el matiz (varía por sabor, por SKU, etc.)
    `None` cuando el catálogo no tiene dato confirmado — la fila entonces dice
    "sin dato" en vez de un número inventado.
    """
    s = item.get("sodio_mg") or {}
    valor = s.get("valor")
    if valor is None:
        return None, None
    if isinstance(valor, (int, float)):
        return f"{round(valor)} mg", None
    texto = str(valor).strip()
    # Corta el primer número o rango del string; el resto (paréntesis con
    # variantes/matices) se conserva íntegro como detalle en el tooltip.
    m = re.match(r"^\s*(\d+(?:\.\d+)?(?:\s*[-–]\s*\d+(?:\.\d+)?)?)", texto)
    if not m:
        return None, texto
    cifra = re.sub(r"\s*[-–]\s*", "–", m.group(1))
    hay_mas = texto[m.end():].strip(" ()")
    return f"{cifra} mg", (texto if hay_mas else None)


def _buscar(catalogo, lista, nombre_exacto):
    # `lista` acepta ruta anidada con punto para la sección oficiales_extendido
    # (p.ej. "oficiales_extendido.bebidas_polvo") — R-47.
    if "." in lista:
        raiz, sub = lista.split(".", 1)
        items = catalogo[raiz][sub]
        clave = "producto"
    else:
        items = catalogo[lista]
        clave = "producto" if lista == "oficiales" else "alimento"
    for item in items:
        if item.get(clave) == nombre_exacto:
            return item
    raise KeyError(f"'{nombre_exacto}' no encontrado en fueling_catalog.json[{lista}]")


def generar():
    catalogo = json.loads(CATALOGO_JSON.read_text(encoding="utf-8"))

    filas = []
    for c in CURATION:
        item = _buscar(catalogo, c["fuente_lista"], c["fuente_nombre"])
        carbs = _carbs_g(item)
        sodio, sodio_detalle = _sodio(item)
        campos = (
            '  { nombre: "%s", carbs_g: %d, unidad: "%s", plural: "%s", grupo: "%s", '
            'porque: "%s", limpieza: %d'
            % (c["nombre"], carbs, c["unidad"], c["plural"], c["grupo"], c["porque"], c["limpieza"])
        )
        # sodio: null explícito cuando el catálogo no lo confirma — el widget
        # muestra "sin dato", nunca un número inventado (R-46).
        campos += ", sodio: %s" % (f'"{sodio}"' if sodio else "null")
        if sodio_detalle:
            campos += ', sodio_detalle: "%s"' % sodio_detalle.replace('"', "'")
        filas.append(campos + " },")

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
