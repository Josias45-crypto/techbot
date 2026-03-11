# ==================================================
# backend/app/api/v1/endpoints/chat.py
# Endpoint principal del chatbot.
# Recibe el mensaje del usuario, clasifica la
# intencion, genera respuesta y maneja el contexto
# de la conversacion.
# ==================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from backend.app.core.database import get_db
from backend.app.core.dependencies import get_optional_user
from backend.app.core.config import settings
from backend.app.models.user import User, Session as UserSession
from backend.app.models.chatbot import Conversation, Message, MessageIntent, Intent, Escalation
from backend.app.models.tickets import Ticket, TicketHistory
from backend.app.schemas.chatbot import ChatInput, ChatResponse
from backend.app.nlp.intent_classifier import classify_intent, extract_entities
from backend.app.nlp.response_generator import generate_response

router = APIRouter(prefix="/chat", tags=["Chatbot"])


@router.post("", response_model=ChatResponse)
def chat(
    data: ChatInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """
    Endpoint principal del chatbot.

    Flujo completo:
    1. Obtiene o crea sesion del usuario
    2. Obtiene o crea conversacion activa
    3. Guarda el mensaje del usuario
    4. Clasifica la intencion con NLP
    5. Genera respuesta automatica
    6. Guarda la respuesta del bot
    7. Si debe escalar, crea ticket automatico
    8. Retorna respuesta al cliente
    """

    # -- PASO 1: Obtener o crear sesion ------------
    session = db.query(UserSession).filter(
        UserSession.token == data.session_token,
        UserSession.is_active == True
    ).first()

    if not session:
        # Crea nueva sesion anonima si no existe
        session = UserSession(
            id=str(uuid.uuid4()),
            user_id=current_user.id if current_user else None,
            token=data.session_token,
            channel=data.channel,
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        db.add(session)
        db.flush()  # Guarda sin commit para obtener el ID

    # -- PASO 2: Obtener o crear conversacion ------
    conversation = db.query(Conversation).filter(
        Conversation.session_id == session.id,
        Conversation.status == "active"
    ).first()

    if not conversation:
        conversation = Conversation(
            id=str(uuid.uuid4()),
            session_id=session.id,
            user_id=current_user.id if current_user else None,
            channel=data.channel,
            status="active"
        )
        db.add(conversation)
        db.flush()

    # -- PASO 3: Guardar mensaje del usuario -------
    user_message = Message(
        id=str(uuid.uuid4()),
        conversation_id=str(conversation.id),
        sender_type="user",
        sender_id=current_user.id if current_user else None,
        content=data.message,
        extra_data={}
    )
    db.add(user_message)
    db.flush()

    # -- PASO 4: Clasificar intencion con NLP ------
    intent_result = classify_intent(data.message)
    entities = extract_entities(data.message)

    # Guarda la intencion detectada en la BD
    intent_record = db.query(Intent).filter(
        Intent.name == intent_result["intent"]
    ).first()

    if intent_record:
        message_intent = MessageIntent(
            id=str(uuid.uuid4()),
            message_id=user_message.id,
            intent_id=intent_record.id,
            confidence=intent_result["confidence"],
            detected_entities=entities
        )
        db.add(message_intent)

    # -- PASO 5: Generar respuesta -----------------
    response_data = generate_response(
        intent=intent_result["intent"],
        message=data.message,
        db=db
    )

    # -- PASO 6: Guardar respuesta del bot ---------
    bot_message = Message(
        id=str(uuid.uuid4()),
        conversation_id=str(conversation.id),
        sender_type="bot",
        sender_id=None,
        content=response_data["message"],
        extra_data={
            "intent": intent_result["intent"],
            "confidence": intent_result["confidence"],
            "suggestions": response_data["suggestions"]
        }
    )
    db.add(bot_message)

    # -- PASO 7: Escalar si es necesario -----------
    escalated = response_data.get("escalate", False)

    if escalated:
        # Crea escalamiento automatico
        escalation = Escalation(
            id=str(uuid.uuid4()),
            conversation_id=str(conversation.id),
            reason="user_request",
            confidence_score=intent_result["confidence"],
            escalated_at=datetime.utcnow()
        )
        db.add(escalation)

        # Actualiza estado de la conversacion
        conversation.status = "escalated"

        # Crea ticket automatico si no existe uno para esta conversacion
        existing_ticket = db.query(Ticket).filter(
            Ticket.conversation_id == conversation.id
        ).first()

        if not existing_ticket:
            count = db.query(Ticket).count() + 1
            ticket = Ticket(
                id=str(uuid.uuid4()),
                conversation_id=str(conversation.id),
                user_id=current_user.id if current_user else None,
                reference_code=f"TKT-{datetime.utcnow().year}{count:04d}",
                category="general",
                priority="medium",
                status="open",
                channel_origin=data.channel,
                notes=f"Ticket creado automaticamente. Intencion: {intent_result['intent']}"
            )
            db.add(ticket)

            # Registra en historial del ticket
            history = TicketHistory(
                id=str(uuid.uuid4()),
                ticket_id=ticket.id,
                previous_status=None,
                new_status="open",
                note="Ticket creado automaticamente por el chatbot"
            )
            db.add(history)

    # -- PASO 8: Commit y retornar respuesta -------
    db.commit()

    return ChatResponse(
        message=response_data["message"],
        intent=intent_result["intent"],
        confidence=intent_result["confidence"],
        escalated=escalated,
        conversation_id=str(conversation.id),
        suggestions=response_data["suggestions"]
    )


@router.get("/history/{conversation_id}")
def get_conversation_history(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """
    Retorna el historial completo de una conversacion.
    Util para mostrar el chat anterior al usuario.
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(404, detail="Conversacion no encontrada")

    # Obtiene todos los mensajes ordenados por fecha
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()

    return {
        "conversation_id": conversation_id,
        "status": conversation.status,
        "messages": [
            {
                "id": m.id,
                "sender_type": m.sender_type,
                "content": m.content,
                "created_at": m.created_at.isoformat()
            }
            for m in messages
        ]
    }
