from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime, date
from decimal import Decimal


# --------------------------------------------------
# ESQUEMAS DE AUDITORÍA (AUDIT LOGS)
# Registro inmutable de toda acción del sistema.
# Nunca se edita ni elimina — solo se inserta.
# --------------------------------------------------

class AuditLogCreate(BaseModel):
    # Datos necesarios para registrar una acción
    user_id: Optional[str] = None      # NULL si es acción automática del sistema
    action: str                         # Ej: "user.login", "ticket.escalated"
    entity_type: str                    # Tabla afectada: "tickets", "users", etc.
    entity_id: Optional[str] = None    # ID del registro afectado
    detail: Dict[str, Any] = {}        # Datos antes/después del cambio en JSON
    ip_address: Optional[str] = None   # IP desde donde se realizó la acción
    channel: Optional[str] = None      # Canal: web, whatsapp, etc.

class AuditLogResponse(BaseModel):
    # Respuesta completa del log de auditoría
    id: str
    user_id: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    detail: Dict[str, Any]
    ip_address: Optional[str] = None
    channel: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True  # Permite convertir modelos ORM a Pydantic


# --------------------------------------------------
# ESQUEMAS DE MÉTRICAS DIARIAS
# Resumen agregado por día para el panel de admin.
# Se calcula automáticamente con un job nocturno.
# --------------------------------------------------

class MetricsDailyResponse(BaseModel):
    # Respuesta completa de métricas de un día
    id: str
    date: date

    # Contadores de conversaciones
    total_conversations: int
    resolved_by_bot: int        # Resueltas automáticamente
    resolved_by_agent: int      # Resueltas por humano
    escalated: int              # Escaladas a agente

    # Tiempos promedio
    avg_response_time_sec: Decimal    # Tiempo promedio de respuesta del bot
    avg_resolution_time_min: Decimal  # Tiempo promedio hasta resolución

    # Datos adicionales
    top_intent: Optional[str] = None  # Intención más consultada del día
    by_channel: Dict[str, Any] = {}   # Desglose por canal: {web: 45, whatsapp: 30}
    by_category: Dict[str, Any] = {}  # Desglose por categoría

    created_at: datetime

    class Config:
        from_attributes = True


# --------------------------------------------------
# ESQUEMA DE RESUMEN DEL DASHBOARD
# Datos agregados para mostrar en el panel
# principal del administrador en tiempo real
# --------------------------------------------------

class DashboardSummary(BaseModel):
    # Totales generales del sistema
    total_users: int                    # Clientes registrados
    total_products: int                 # Productos en catálogo
    total_conversations_today: int      # Conversaciones del día
    total_open_tickets: int             # Tickets sin resolver
    total_pending_repairs: int          # Reparaciones en proceso
    total_pending_orders: int           # Pedidos pendientes

    # Tasas de rendimiento
    bot_resolution_rate: float          # % resuelto por bot hoy
    avg_response_time_sec: float        # Tiempo promedio respuesta

    # Últimas métricas disponibles
    last_metrics: Optional[MetricsDailyResponse] = None
