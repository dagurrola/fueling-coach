#!/usr/bin/env python3
"""
generate_catalog.py — R-43 #3: elimina la copia manual del catálogo del widget.

Antes: el CATALOGO del widget (9 productos) estaba hardcodeado a mano en
index.html, duplicando datos que ya viven en dacoach/fueling_catalog.json —
dos fuentes de verdad, deriva garantizada (mismo patrón de falla silenciosa
de R-35/R-37/R-38).

Ahora: los NÚMEROS (carbs_g, tipo) se leen de fueling_catalog.json — única
fuente de verdad. La capa EDITORIAL (unidad, plural, grupo, "porqué", orden
de limpieza) es contenido curado para el widget que no pertenece al catálogo
de research general — vive aquí, en CURACION, no en el JSON fuente.

Uso: correr este script cada vez que fueling_catalog.json cambie, para
regenerar el bloque CATALOGO dentro de index.html. No hay build step ni
servidor — el widget sigue siendo HTML/JS estático puro.
"""
import json
import re
import sys
from pathlib import Path

FUENTE = Path("/Users/dagurrola/Desktop/OC/dacoach/fueling_catalog.json")
WIDGET = Path(__file__).parent / "index.html"

# Nombre en el widget -> (sección en fueling_catalog.json, clave exacta en esa sección)
NAME_MAP = {
    "Papas a la sal":       ("real_food", "Papas a la sal (Sabritas Original)"),
    "SIS GO Isotonic":       ("oficiales", "SIS GO Isotonic Gel"),
    "GU Energy Gel":         ("oficiales", "GU Energy Gel"),
    "Maurten Gel 100":       ("oficiales", "Maurten Gel 100"),
    "Precision PF 30":       ("oficiales", "Precision Fuel & Hydration PF 30 Gel"),
    "Dátil Medjool":         ("real_food", "Dátil Medjool"),
    "Plátano mediano":       ("real_food", "Plátano mediano"),
    "Gomitas":               ("real_food", "Gomitas (gummy bears, Sour Patch, Nerds Gummy Clusters)"),
    "Tailwind (mezcla)":     ("oficiales", "Tailwind Endurance Fuel"),
}

# Capa editorial — curada para el widget, NO vive en fueling_catalog.json.
# (unidad, plural, grupo, porqué, limpieza 0=más fructosa..2=más limpio)
CURACION = {
    "Papas a la sal":    ("bolsa 45g", "bolsas",  "Comida real",    "almidón puro + sodio, cero fructosa — el perfil más limpio para el estómago en sesiones largas", 2),
    "SIS GO Isotonic":   ("gel",       "geles",   "Gel deportivo",  "maltodextrina, isotónico — no necesita agua extra para digerirse", 2),
    "GU Energy Gel":     ("gel",       "geles",   "Gel deportivo",  "clásico, fácil de conseguir en MX; algo de fructosa pero balanceado", 1),
    "Maurten Gel 100":   ("gel",       "geles",   "Gel deportivo",  "hidrogel diseñado para absorción alta; más fructosa relativa, mejor a carga alta", 0),
    "Precision PF 30":   ("gel",       "geles",   "Gel deportivo",  "30g por gel — menos sobres para el mismo total; ratio 2:1 glucosa:fructosa", 1),
    "Dátil Medjool":     ("pieza",     "dátiles", "Comida real",    "natural, denso, con potasio; fructosa alta — mejor combinado con algo de glucosa", 0),
    "Plátano mediano":   ("pieza",     "plátanos","Comida real",   "barato y accesible; mejor en la primera hora, luego el volumen estorba", 1),
    "Gomitas":           ("puño 40g",  "puños",   "Comida real",    "azúcar rápido y barato; rompe la fatiga de comer solo geles. Suma sodio aparte", 1),
    "Tailwind (mezcla)": ("porción",   "porciones","Bebida",        "carbs + sodio en el mismo líquido — resuelve hidratación y fuel de un solo golpe", 1),
}


def extraer_carbs(valor) -> float:
    """fueling_catalog.json mezcla formatos: número plano, rango 'a-b', o dict
    {'valor': 'a-b', 'confirmado': bool}. Siempre se resuelve al punto medio."""
    if isinstance(valor, dict):
        valor = valor.get("valor")
    if isinstance(valor, (int, float)):
        return float(valor)
    m = re.match(r"([\d.]+)\s*-\s*([\d.]+)", str(valor))
    if m:
        return (float(m.group(1)) + float(m.group(2))) / 2
    m = re.match(r"([\d.]+)", str(valor))
    return float(m.group(1)) if m else 0.0


def cargar_fuente() -> dict:
    fuente = json.loads(FUENTE.read_text())
    por_nombre = {}
    for seccion in ("oficiales", "real_food"):
        for p in fuente.get(seccion, []):
            clave = p.get("producto") or p.get("alimento")
            carbs_raw = p.get("carbs_g")
            por_nombre[(seccion, clave)] = round(extraer_carbs(carbs_raw))
    return por_nombre


def generar_js(por_nombre: dict) -> str:
    lineas = ["const CATALOGO = ["]
    faltantes = []
    for nombre_widget, (seccion, clave_fuente) in NAME_MAP.items():
        carbs = por_nombre.get((seccion, clave_fuente))
        if carbs is None:
            faltantes.append(f"{nombre_widget} -> ({seccion}, {clave_fuente!r})")
            continue
        unidad, plural, grupo, porque, limpieza = CURACION[nombre_widget]
        lineas.append(
            f'  {{ nombre: "{nombre_widget}", carbs_g: {carbs:g}, unidad: "{unidad}", '
            f'plural: "{plural}", grupo: "{grupo}", porque: "{porque}", limpieza: {limpieza} }},'
        )
    lineas.append("];")

    if faltantes:
        print("✗ ERROR: no se encontraron en fueling_catalog.json:", file=sys.stderr)
        for f in faltantes:
            print(" -", f, file=sys.stderr)
        sys.exit(1)

    return "\n".join(lineas)


def actualizar_widget(nuevo_bloque: str):
    html = WIDGET.read_text()
    patron = re.compile(r"const CATALOGO = \[.*?\];", re.DOTALL)
    if not patron.search(html):
        print("✗ ERROR: no se encontró el bloque 'const CATALOGO = [...]' en index.html", file=sys.stderr)
        sys.exit(1)
    nuevo_html = patron.sub(nuevo_bloque.replace("\\", "\\\\"), html, count=1)
    WIDGET.write_text(nuevo_html)
    print(f"✓ {WIDGET} actualizado — {len(NAME_MAP)} productos generados desde {FUENTE.name}")


if __name__ == "__main__":
    fuente = cargar_fuente()
    bloque = generar_js(fuente)
    actualizar_widget(bloque)
