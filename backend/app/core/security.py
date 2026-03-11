# ==================================================
# backend/app/core/security.py
# Modulo central de seguridad del sistema.
# Maneja: hash de contrasenas, generacion y
# verificacion de tokens JWT.
# ==================================================

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from backend.app.core.config import settings


# -- CONFIGURACION DE BCRYPT ----------------------
# bcrypt incluye salt automatico y es resistente
# a ataques de fuerza bruta.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    # Convierte contrasena en texto plano a hash bcrypt.
    # Nunca se almacena la contrasena original.
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Verifica si una contrasena coincide con su hash.
    # Retorna True si coincide, False si no.
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    # Genera un token JWT firmado con los datos del usuario.
    # El token contiene: sub (user_id), role, exp (expiracion)
    to_encode = data.copy()

    # Calcula la fecha de expiracion
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Agrega la expiracion al payload
    to_encode.update({"exp": expire})

    # Firma el token con la clave secreta
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    # Decodifica y verifica un token JWT.
    # Retorna el payload si es valido, None si no lo es.
    # Verifica automaticamente: firma, expiracion y formato.
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        # Token invalido, expirado o malformado
        return None
