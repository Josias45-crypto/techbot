from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings

# Motor de conexión
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # Verifica conexión antes de usarla
    pool_size=10,             # Conexiones simultáneas
    max_overflow=20,          # Conexiones extra en picos
    echo=settings.DEBUG       # Muestra SQL en consola si DEBUG=True
)

# Sesión de base de datos
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para los modelos ORM
Base = declarative_base()


def get_db():
    """
    Dependencia de FastAPI que provee una sesión de base de datos
    y la cierra automáticamente al terminar el request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection():
    """
    Verifica que la conexión a la base de datos funcione correctamente.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"❌ Error de conexión a la base de datos: {e}")
        return False
