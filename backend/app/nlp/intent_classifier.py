# ==================================================
# backend/app/nlp/intent_classifier.py
# Clasificador de intenciones del chatbot.
# Analiza el mensaje del usuario y determina
# que quiere hacer: consultar precio, reportar
# problema, rastrear pedido, etc.
# ==================================================

import re
from typing import Optional
from rapidfuzz import fuzz


# -- INTENCIONES CON PALABRAS CLAVE ---------------
# Cada intencion tiene una lista de palabras y frases
# que la identifican. El clasificador busca coincidencias
# en el mensaje del usuario.
INTENT_PATTERNS = {
    "consulta_precio": [
        "precio", "costo", "cuanto cuesta", "cuanto vale",
        "valor", "cuanto es", "precio de", "cuanto cobran"
    ],
    "consulta_stock": [
        "stock", "disponible", "hay", "tienen", "en existencia",
        "queda", "quedan", "disponibilidad", "inventario"
    ],
    "soporte_tecnico": [
        "problema", "error", "falla", "no funciona", "ayuda",
        "no prende", "no enciende", "pantalla", "driver",
        "instalar", "configurar", "arreglar", "danado", "roto"
    ],
    "rastrear_pedido": [
        "pedido", "orden", "compra", "rastrear", "donde esta",
        "cuando llega", "estado de mi pedido", "ORD-", "seguimiento"
    ],
    "rastrear_reparacion": [
        "reparacion", "reparar", "arreglo", "tecnico", "REP-",
        "cuando esta listo", "estado de mi reparacion", "equipo"
    ],
    "consulta_compatibilidad": [
        "compatible", "compatibilidad", "sirve para", "funciona con",
        "puedo usar", "va con", "soporta"
    ],
    "saludo": [
        "hola", "buenos dias", "buenas tardes", "buenas noches",
        "hi", "hey", "saludos", "que tal", "como estan"
    ],
    "despedida": [
        "adios", "hasta luego", "chao", "bye", "nos vemos",
        "hasta pronto", "gracias", "muchas gracias"
    ],
    "hablar_agente": [
        "agente", "humano", "persona", "asesor", "representante",
        "quiero hablar", "comunicar", "operador"
    ]
}


def classify_intent(message: str) -> dict:
    """
    Clasifica la intencion del mensaje del usuario.

    Proceso:
    1. Normaliza el texto (minusculas, sin tildes)
    2. Busca coincidencias exactas con palabras clave
    3. Si no encuentra, usa similitud fuzzy (tolerante a errores)
    4. Retorna la intencion con mayor puntaje

    Retorna:
        {
            "intent": "soporte_tecnico",
            "confidence": 0.85,
            "matched_pattern": "no funciona"
        }
    """
    # Normaliza el mensaje
    text = normalize_text(message)

    best_intent = "desconocido"
    best_score = 0.0
    best_pattern = ""

    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            pattern_norm = normalize_text(pattern)

            # Busqueda exacta — mayor peso
            if pattern_norm in text:
                score = 1.0
            else:
                # Busqueda fuzzy — tolerante a errores tipograficos
                score = fuzz.partial_ratio(pattern_norm, text) / 100.0

            if score > best_score:
                best_score = score
                best_intent = intent
                best_pattern = pattern

    # Si el puntaje es muy bajo, marca como desconocido
    if best_score < 0.6:
        best_intent = "desconocido"

    return {
        "intent": best_intent,
        "confidence": round(best_score, 4),
        "matched_pattern": best_pattern
    }


def normalize_text(text: str) -> str:
    """
    Normaliza el texto para mejorar la deteccion:
    - Convierte a minusculas
    - Elimina tildes y caracteres especiales
    - Elimina espacios extra
    """
    text = text.lower().strip()

    # Elimina tildes
    replacements = {
        "a": ["a", "a"],
        "e": ["e", "e"],
        "i": ["i", "i"],
        "o": ["o", "o"],
        "u": ["u", "u", "u"],
        "n": ["n"]
    }
    for clean, variants in replacements.items():
        for v in variants:
            text = text.replace(v, clean)

    # Elimina caracteres especiales excepto espacios y guiones
    text = re.sub(r"[^a-z0-9\s\-]", "", text)

    # Elimina espacios multiples
    text = re.sub(r"\s+", " ", text).strip()

    return text


def extract_entities(message: str) -> dict:
    """
    Extrae entidades clave del mensaje del usuario.

    Entidades detectadas:
    - reference_code: codigos ORD-, REP-, TKT-
    - product_name: nombres de productos mencionados
    - error_code: codigos de error (ej: ERROR_404, 0x000)

    Retorna:
        {
            "reference_code": "ORD-20240001",
            "error_code": "0x0000007B",
            "product_name": None
        }
    """
    entities = {
        "reference_code": None,
        "error_code": None,
        "product_name": None
    }

    # Detecta codigos de referencia: ORD-, REP-, TKT-
    ref_match = re.search(r"\b(ORD|REP|TKT)-\d{4,}\b", message.upper())
    if ref_match:
        entities["reference_code"] = ref_match.group()

    # Detecta codigos de error Windows (0x...)
    error_match = re.search(r"\b0x[0-9A-Fa-f]{4,8}\b", message)
    if error_match:
        entities["error_code"] = error_match.group()

    # Detecta codigos de error genericos (ERROR_XXX)
    error_match2 = re.search(r"\bERROR[_\s]\w+\b", message.upper())
    if error_match2 and not entities["error_code"]:
        entities["error_code"] = error_match2.group()

    return entities
