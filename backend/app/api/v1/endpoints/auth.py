# ==================================================
# backend/app/api/v1/endpoints/auth.py
# Endpoints de autenticacion: registro, login,
# perfil y cierre de sesion.
# ==================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from backend.app.core.database import get_db
from backend.app.core.security import hash_password, verify_password, create_access_token
from backend.app.core.dependencies import get_current_user
from backend.app.models.user import User, Role, Session as UserSession
from backend.app.schemas.user import (
    UserCreate, UserResponse, LoginRequest, TokenResponse, UserWithRole
)
from backend.app.core.config import settings

# -- ROUTER -------------------------------------------
# Prefijo /auth para todos los endpoints de este archivo
router = APIRouter(prefix="/auth", tags=["Autenticacion"])


# -- REGISTRO -----------------------------------------
@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema.
    Verifica que el email no exista antes de crear.
    La contrasena se almacena como hash bcrypt.
    """
    # Verifica si el email ya esta registrado
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya esta registrado"
        )

    # Verifica que el rol exista
    role = db.query(Role).filter(Role.id == user_data.role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )

    # Crea el nuevo usuario con contrasena hasheada
    new_user = User(
        id=str(uuid.uuid4()),
        role_id=user_data.role_id,
        full_name=user_data.full_name,
        email=user_data.email,
        phone=user_data.phone,
        password_hash=hash_password(user_data.password),
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# -- LOGIN --------------------------------------------
@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Autentica un usuario y retorna un token JWT.
    Actualiza last_login y crea registro de sesion.
    """
    # Busca el usuario por email
    user = db.query(User).filter(User.email == credentials.email).first()

    # Verifica contrasena — mismo mensaje para no revelar si existe el email
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contrasena incorrectos"
        )

    # Verifica que el usuario este activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    # Genera el token JWT con id y rol del usuario
    token = create_access_token(data={
        "sub": user.id,
        "role": user.role.name
    })

    # Actualiza la fecha de ultimo login
    user.last_login = datetime.utcnow()

    # Registra la sesion activa
    session = UserSession(
        id=str(uuid.uuid4()),
        user_id=user.id,
        token=token,
        channel="web",
        is_active=True,
        expires_at=datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    db.add(session)
    db.commit()

    return TokenResponse(access_token=token, user=user)


# -- PERFIL -------------------------------------------
@router.get("/me", response_model=UserWithRole)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna el perfil completo del usuario autenticado
    incluyendo su rol y permisos.
    Requiere token JWT valido en el header.
    """
    # Carga el usuario con su rol (eager load)
    user = db.query(User).filter(User.id == current_user.id).first()
    return user


# -- LOGOUT -------------------------------------------
@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Invalida la sesion activa del usuario.
    Marca el token como inactivo en la base de datos.
    """
    # Desactiva todas las sesiones activas del usuario
    db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.is_active == True
    ).update({"is_active": False})

    db.commit()

    return {"message": "Sesion cerrada correctamente"}
