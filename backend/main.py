# ==================================================
# backend/main.py
# Punto de entrada principal de TechBot API.
# Configura FastAPI, CORS, routers y health checks.
# ==================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import check_db_connection
from backend.app.api.v1.router import api_router

# -- Instancia principal de FastAPI ---------------
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema inteligente de soporte tecnico con NLP",
    docs_url="/docs",
    redoc_url="/redoc"
)

# -- Middleware CORS --------------------------------
# Permite peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -- Registro del router principal -----------------
# Todos los endpoints quedan bajo /api/v1/
app.include_router(api_router)

# -- Eventos de inicio -----------------------------
@app.on_event("startup")
async def startup_event():
    print(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    if check_db_connection():
        print("Conexion a base de datos exitosa")
    else:
        print("Error conectando a la base de datos")

# -- Health checks ---------------------------------
@app.get("/", tags=["Health"])
def root():
    return {"app": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running"}

@app.get("/health", tags=["Health"])
def health():
    db_ok = check_db_connection()
    return {"status": "ok" if db_ok else "error", "database": "connected" if db_ok else "disconnected"}
