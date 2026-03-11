# ==================================================
# backend/app/nlp/response_generator.py
# Genera respuestas automaticas del chatbot
# segun la intencion detectada y el contexto.
# Consulta la base de datos para dar respuestas
# con informacion real del sistema.
# ==================================================

from sqlalchemy.orm import Session
from backend.app.models.catalog import Product, Inventory
from backend.app.models.orders import Order, Repair
from backend.app.models.tickets import Ticket
from backend.app.models.knowledge import FAQ, KnownIssue
from backend.app.nlp.intent_classifier import extract_entities
import random


# -- RESPUESTAS PREDEFINIDAS ----------------------
# Mensajes para intenciones que no necesitan BD
RESPONSES = {
    "saludo": [
        "Hola! Soy TechBot, el asistente de SekaiTech. Como puedo ayudarte hoy?",
        "Buenos dias! Estoy aqui para ayudarte. En que te puedo asistir?",
        "Hola! Bienvenido a SekaiTech. Como puedo ayudarte?"
    ],
    "despedida": [
        "Hasta luego! Si necesitas algo mas, aqui estare.",
        "Fue un placer ayudarte. Que tengas un excelente dia!",
        "Adios! Recuerda que puedes contactarnos cuando necesites."
    ],
    "desconocido": [
        "No entendi bien tu consulta. Puedes reformularla?",
        "Hmm, no estoy seguro de como ayudarte con eso. Quieres hablar con un agente?",
        "No comprendi tu mensaje. Puedo ayudarte con: precios, stock, soporte tecnico, rastrear pedidos o reparaciones."
    ]
}

# -- SUGERENCIAS POR INTENCION --------------------
# Botones de respuesta rapida que se muestran al usuario
SUGGESTIONS = {
    "saludo": [
        "Ver productos", "Rastrear pedido",
        "Soporte tecnico", "Hablar con agente"
    ],
    "consulta_precio": [
        "Ver mas productos", "Consultar stock", "Hacer pedido"
    ],
    "consulta_stock": [
        "Ver precio", "Unirme a lista de espera", "Ver alternativas"
    ],
    "soporte_tecnico": [
        "Ver solucion paso a paso", "Hablar con tecnico", "Crear ticket"
    ],
    "rastrear_pedido": [
        "Ver detalle del pedido", "Hablar con agente"
    ],
    "rastrear_reparacion": [
        "Ver detalle de reparacion", "Hablar con tecnico"
    ],
    "desconocido": [
        "Consultar precios", "Rastrear pedido",
        "Soporte tecnico", "Hablar con agente"
    ]
}


def generate_response(intent: str, message: str, db: Session) -> dict:
    """
    Genera una respuesta automatica segun la intencion.

    Para intenciones que requieren datos (precio, stock,
    rastreo), consulta la base de datos y devuelve
    informacion real. Para saludos y despedidas usa
    respuestas predefinidas.

    Retorna:
        {
            "message": "El precio de la RTX 4090 es ",
            "suggestions": ["Ver stock", "Hacer pedido"],
            "escalate": False,
            "data": {...}
        }
    """
    entities = extract_entities(message)

    # -- Enruta segun intencion -------------------
    if intent == "saludo":
        return _simple_response("saludo")

    elif intent == "despedida":
        return _simple_response("despedida")

    elif intent == "consulta_precio":
        return _handle_price_query(message, db)

    elif intent == "consulta_stock":
        return _handle_stock_query(message, db)

    elif intent == "soporte_tecnico":
        return _handle_support_query(message, db)

    elif intent == "rastrear_pedido":
        return _handle_order_tracking(entities, db)

    elif intent == "rastrear_reparacion":
        return _handle_repair_tracking(entities, db)

    elif intent == "hablar_agente":
        return {
            "message": "Entendido! Te voy a conectar con un agente humano. Un momento por favor.",
            "suggestions": [],
            "escalate": True,  # Activa escalamiento automatico
            "data": {}
        }

    else:
        return _simple_response("desconocido")


def _simple_response(intent: str) -> dict:
    # Selecciona una respuesta aleatoria de las predefinidas
    message = random.choice(RESPONSES.get(intent, RESPONSES["desconocido"]))
    return {
        "message": message,
        "suggestions": SUGGESTIONS.get(intent, []),
        "escalate": False,
        "data": {}
    }


def _handle_price_query(message: str, db: Session) -> dict:
    """
    Busca productos que coincidan con el mensaje
    y retorna sus precios.
    """
    # Extrae palabras clave del mensaje para buscar productos
    words = [w for w in message.lower().split() if len(w) > 3]

    products = []
    for word in words:
        results = db.query(Product).filter(
            Product.is_active == True,
            Product.name.ilike(f"%{word}%")
        ).limit(3).all()
        products.extend(results)

    # Elimina duplicados
    seen = set()
    unique_products = []
    for p in products:
        if p.id not in seen:
            seen.add(p.id)
            unique_products.append(p)

    if not unique_products:
        return {
            "message": "No encontre productos que coincidan con tu busqueda. Puedes ser mas especifico?",
            "suggestions": ["Ver catalogo completo", "Hablar con agente"],
            "escalate": False,
            "data": {}
        }

    # Formatea la respuesta con precios
    response_lines = ["Encontre estos productos:\n"]
    for p in unique_products[:3]:
        response_lines.append(f"- {p.name}: ")

    return {
        "message": "\n".join(response_lines),
        "suggestions": SUGGESTIONS["consulta_precio"],
        "escalate": False,
        "data": {"products": [{"name": p.name, "price": str(p.price)} for p in unique_products[:3]]}
    }


def _handle_stock_query(message: str, db: Session) -> dict:
    """
    Verifica disponibilidad de productos en inventario.
    """
    words = [w for w in message.lower().split() if len(w) > 3]

    products = []
    for word in words:
        results = db.query(Product).filter(
            Product.is_active == True,
            Product.name.ilike(f"%{word}%")
        ).limit(3).all()
        products.extend(results)

    if not products:
        return {
            "message": "No encontre el producto que buscas. Puedes darme mas detalles?",
            "suggestions": ["Ver catalogo", "Hablar con agente"],
            "escalate": False,
            "data": {}
        }

    # Consulta inventario de cada producto encontrado
    seen = set()
    response_lines = ["Disponibilidad actual:\n"]
    for p in products:
        if p.id in seen:
            continue
        seen.add(p.id)
        inv = db.query(Inventory).filter(Inventory.product_id == p.id).first()
        stock = inv.stock if inv else 0
        status = "En stock" if stock > 0 else "Sin stock"
        response_lines.append(f"- {p.name}: {status} ({stock} unidades)")

    return {
        "message": "\n".join(response_lines),
        "suggestions": SUGGESTIONS["consulta_stock"],
        "escalate": False,
        "data": {}
    }


def _handle_support_query(message: str, db: Session) -> dict:
    """
    Busca soluciones en la base de problemas conocidos.
    Si no encuentra solucion, escala a agente.
    """
    # Busca en problemas conocidos
    words = [w for w in message.lower().split() if len(w) > 3]

    issues = []
    for word in words:
        results = db.query(KnownIssue).filter(
            KnownIssue.is_active == True,
            KnownIssue.description.ilike(f"%{word}%") |
            KnownIssue.title.ilike(f"%{word}%")
        ).limit(2).all()
        issues.extend(results)

    if issues:
        issue = issues[0]  # Toma el mas relevante
        steps = issue.solution_steps
        steps_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(steps[:4])])
        return {
            "message": f"Encontre una solucion para '{issue.title}':\n\n{steps_text}",
            "suggestions": SUGGESTIONS["soporte_tecnico"],
            "escalate": False,
            "data": {"issue_id": issue.id}
        }

    # Busca en FAQs
    faqs = []
    for word in words:
        results = db.query(FAQ).filter(
            FAQ.is_active == True,
            FAQ.question.ilike(f"%{word}%")
        ).limit(2).all()
        faqs.extend(results)

    if faqs:
        faq = faqs[0]
        return {
            "message": f"{faq.question}\n\n{faq.answer}",
            "suggestions": SUGGESTIONS["soporte_tecnico"],
            "escalate": False,
            "data": {"faq_id": faq.id}
        }

    # No encontro solucion — escala a agente
    return {
        "message": "No encontre una solucion automatica para tu problema. Te voy a conectar con un tecnico especializado.",
        "suggestions": ["Crear ticket", "Hablar con agente"],
        "escalate": True,
        "data": {}
    }


def _handle_order_tracking(entities: dict, db: Session) -> dict:
    """
    Rastrea un pedido por codigo de referencia.
    """
    ref_code = entities.get("reference_code")

    if not ref_code or not ref_code.startswith("ORD"):
        return {
            "message": "Para rastrear tu pedido necesito el codigo de referencia. Ejemplo: ORD-20240001",
            "suggestions": ["Hablar con agente"],
            "escalate": False,
            "data": {}
        }

    order = db.query(Order).filter(Order.reference_code == ref_code).first()
    if not order:
        return {
            "message": f"No encontre el pedido {ref_code}. Verifica el codigo e intenta de nuevo.",
            "suggestions": ["Hablar con agente"],
            "escalate": False,
            "data": {}
        }

    return {
        "message": f"Pedido {ref_code}:\n- Estado: {order.status}\n- Total: \n- Fecha: {order.created_at.strftime('%d/%m/%Y')}",
        "suggestions": SUGGESTIONS["rastrear_pedido"],
        "escalate": False,
        "data": {"order_id": order.id, "status": order.status}
    }


def _handle_repair_tracking(entities: dict, db: Session) -> dict:
    """
    Rastrea una reparacion por codigo de referencia.
    """
    ref_code = entities.get("reference_code")

    if not ref_code or not ref_code.startswith("REP"):
        return {
            "message": "Para rastrear tu reparacion necesito el codigo de referencia. Ejemplo: REP-20240001",
            "suggestions": ["Hablar con agente"],
            "escalate": False,
            "data": {}
        }

    repair = db.query(Repair).filter(Repair.reference_code == ref_code).first()
    if not repair:
        return {
            "message": f"No encontre la reparacion {ref_code}. Verifica el codigo e intenta de nuevo.",
            "suggestions": ["Hablar con agente"],
            "escalate": False,
            "data": {}
        }

    return {
        "message": f"Reparacion {ref_code}:\n- Estado: {repair.status}\n- Dispositivo: {repair.device_description}\n- Fecha ingreso: {repair.created_at.strftime('%d/%m/%Y')}",
        "suggestions": SUGGESTIONS["rastrear_reparacion"],
        "escalate": False,
        "data": {"repair_id": repair.id, "status": repair.status}
    }
