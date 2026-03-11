# ==================================================
# backend/app/api/v1/router.py
# Router principal de la API v1.
# Registra todos los sub-routers de cada modulo.
# Todos los endpoints quedan bajo /api/v1/
# ==================================================

from fastapi import APIRouter
from backend.app.api.v1.endpoints import auth, catalog, tickets, orders, knowledge

# Router principal que agrupa todos los modulos
api_router = APIRouter(prefix="/api/v1")

# -- Registro de routers por modulo ---------------
api_router.include_router(auth.router)        # /api/v1/auth/...
api_router.include_router(catalog.router)     # /api/v1/catalog/...
api_router.include_router(tickets.router)     # /api/v1/tickets/...
api_router.include_router(orders.router)      # /api/v1/orders/...
api_router.include_router(knowledge.router)   # /api/v1/knowledge/...
