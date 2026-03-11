# ==================================================
# backend/app/core/dependencies.py
# Dependencias de FastAPI para autenticacion y
# autorizacion. Se inyectan en los endpoints con
# Depends() para protegerlos automaticamente.
# ==================================================

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import decode_access_token
from backend.app.models.user import User


# -- ESQUEMA DE SEGURIDAD HTTP BEARER -------------
# Extrae el token JWT del header Authorization: Bearer <token>
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependencia principal de autenticacion.
    Extrae y valida el token JWT del header.
    Retorna el usuario autenticado o lanza 401.

    Uso en endpoint:
        @router.get("/perfil")
        def perfil(user: User = Depends(get_current_user)):
            return user
    """
    # Excepcion estandar para credenciales invalidas
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales invalidas o token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decodifica y verifica el token JWT
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise credentials_exception

    # Extrae el ID del usuario del payload
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Busca el usuario en la base de datos
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    # Verifica que el usuario este activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verifica que el usuario autenticado este activo.
    Alias semantico de get_current_user para mayor claridad.
    """
    return current_user


def require_role(*roles: str):
    """
    Dependencia de autorizacion por rol.
    Verifica que el usuario tenga uno de los roles requeridos.

    Uso en endpoint:
        @router.delete("/productos/{id}")
        def eliminar(user: User = Depends(require_role("admin"))):
            ...
    """
    def role_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Obtiene el nombre del rol del usuario
        user_role = db.query(User).filter(
            User.id == current_user.id
        ).first().role.name

        # Verifica si el rol esta en la lista permitida
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere rol: {', '.join(roles)}"
            )
        return current_user

    return role_checker


def get_optional_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(
        HTTPBearer(auto_error=False)
    )
) -> User | None:
    """
    Dependencia opcional - no lanza error si no hay token.
    Retorna el usuario si esta autenticado, None si es anonimo.

    Uso en endpoint:
        @router.post("/chat")
        def chat(user: User | None = Depends(get_optional_user)):
            if user:
                # Usuario autenticado
            else:
                # Usuario anonimo
    """
    if credentials is None:
        return None

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    return db.query(User).filter(User.id == user_id).first()
