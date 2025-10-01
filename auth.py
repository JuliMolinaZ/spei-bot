#!/usr/bin/env python3
"""
Sistema de Autenticación Seguro para SPEI BOT
Implementa JWT, bcrypt, y protección contra ataques
"""

import jwt
import bcrypt
import time
import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
import hashlib
import os

logger = logging.getLogger(__name__)

# Configuración de seguridad
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "spei-bot-secret-key-change-in-production-2025")
ALGORITHM = "HS256"
TOKEN_EXPIRY_HOURS = 1  # Token expira después de 1 hora

# Importar configuración de usuarios
try:
    from users_config import USERS_CONFIG, get_enabled_users, SECURITY_CONFIG
    USERS_DB = get_enabled_users()
    logger.info(f"✅ Configuración de usuarios cargada: {len(USERS_DB)} usuarios activos")
except ImportError:
    logger.warning("⚠️ No se encontró users_config.py, usando configuración por defecto")
    USERS_DB = {
        "admin": {
            "username": "admin",
            "password_hash": "$2b$12$LKzx.oqvVZqKJX8qQxK5Oe7HjBK8Zqp5vKGLKJxPBMXo0Vy3vR0yS",  # admin123
            "role": "admin",
            "name": "Administrador",
            "enabled": True
        }
    }
    SECURITY_CONFIG = {
        "max_login_attempts": 5,
        "block_duration_minutes": 5,
        "session_timeout_hours": 1
    }

class RateLimiter:
    """Rate limiter para prevenir ataques de fuerza bruta"""
    def __init__(self, max_attempts: int = 5, window_seconds: int = 300):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.attempts = {}  # {ip: [(timestamp, success), ...]}

    def _clean_old_attempts(self, identifier: str):
        """Limpia intentos antiguos fuera de la ventana de tiempo"""
        if identifier not in self.attempts:
            return

        current_time = time.time()
        cutoff_time = current_time - self.window_seconds

        # Mantener solo intentos dentro de la ventana
        self.attempts[identifier] = [
            (timestamp, success)
            for timestamp, success in self.attempts[identifier]
            if timestamp > cutoff_time
        ]

    def is_blocked(self, identifier: str) -> bool:
        """Verifica si un identificador está bloqueado"""
        self._clean_old_attempts(identifier)

        if identifier not in self.attempts:
            return False

        # Contar intentos fallidos en la ventana
        failed_attempts = sum(
            1 for _, success in self.attempts[identifier]
            if not success
        )

        return failed_attempts >= self.max_attempts

    def record_attempt(self, identifier: str, success: bool):
        """Registra un intento de login"""
        if identifier not in self.attempts:
            self.attempts[identifier] = []

        self.attempts[identifier].append((time.time(), success))
        self._clean_old_attempts(identifier)

    def get_remaining_attempts(self, identifier: str) -> int:
        """Obtiene intentos restantes"""
        self._clean_old_attempts(identifier)

        if identifier not in self.attempts:
            return self.max_attempts

        failed_attempts = sum(
            1 for _, success in self.attempts[identifier]
            if not success
        )

        return max(0, self.max_attempts - failed_attempts)

    def get_block_time_remaining(self, identifier: str) -> int:
        """Obtiene tiempo restante de bloqueo en segundos"""
        if not self.is_blocked(identifier):
            return 0

        if identifier not in self.attempts or not self.attempts[identifier]:
            return 0

        # Encontrar el intento fallido más antiguo
        oldest_failed = min(
            timestamp for timestamp, success in self.attempts[identifier]
            if not success
        )

        time_elapsed = time.time() - oldest_failed
        return max(0, int(self.window_seconds - time_elapsed))

# Rate limiter global
rate_limiter = RateLimiter(max_attempts=5, window_seconds=300)  # 5 intentos en 5 minutos

def hash_password(password: str) -> str:
    """Hashea una contraseña usando bcrypt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)  # 12 rounds es seguro y rápido
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verifica una contraseña contra su hash"""
    try:
        password_bytes = password.encode('utf-8')
        hash_bytes = password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as e:
        logger.error(f"Error verificando contraseña: {e}")
        return False

def create_access_token(username: str, role: str = "user") -> str:
    """Crea un token JWT de acceso"""
    payload = {
        "sub": username,
        "role": role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS),
        "type": "access"
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifica y decodifica un token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Verificar que no haya expirado
        exp_timestamp = payload.get("exp")
        if exp_timestamp and datetime.utcnow() > datetime.fromtimestamp(exp_timestamp):
            logger.warning("Token expirado")
            return None

        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expirado (ExpiredSignatureError)")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token inválido: {e}")
        return None
    except Exception as e:
        logger.error(f"Error verificando token: {e}")
        return None

def get_user_identifier() -> str:
    """Obtiene un identificador único del usuario (simulado, Streamlit no expone IP)"""
    # En producción, podrías usar headers de proxy o session ID
    # Por ahora usamos un hash del session state
    session_id = id(st.session_state)
    return hashlib.md5(f"{session_id}".encode()).hexdigest()[:16]

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Autentica un usuario y retorna sus datos si es válido"""

    # Rate limiting por identificador de usuario
    user_identifier = f"{username}_{get_user_identifier()}"

    # Verificar si está bloqueado
    if rate_limiter.is_blocked(user_identifier):
        remaining_time = rate_limiter.get_block_time_remaining(user_identifier)
        logger.warning(f"Usuario bloqueado: {username} - {remaining_time}s restantes")
        return {
            "success": False,
            "error": "blocked",
            "remaining_time": remaining_time
        }

    # Verificar que el usuario existe
    if username not in USERS_DB:
        rate_limiter.record_attempt(user_identifier, success=False)
        remaining = rate_limiter.get_remaining_attempts(user_identifier)
        logger.warning(f"Usuario no encontrado: {username}")
        return {
            "success": False,
            "error": "invalid_credentials",
            "remaining_attempts": remaining
        }

    user = USERS_DB[username]

    # Verificar contraseña
    if user["password_hash"] and verify_password(password, user["password_hash"]):
        # Login exitoso
        rate_limiter.record_attempt(user_identifier, success=True)
        logger.info(f"Login exitoso: {username}")

        return {
            "success": True,
            "username": username,
            "role": user["role"],
            "name": user["name"]
        }
    else:
        # Login fallido
        rate_limiter.record_attempt(user_identifier, success=False)
        remaining = rate_limiter.get_remaining_attempts(user_identifier)
        logger.warning(f"Contraseña incorrecta para: {username}")

        return {
            "success": False,
            "error": "invalid_credentials",
            "remaining_attempts": remaining
        }

def init_session_state():
    """Inicializa el estado de sesión para autenticación"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "user_data" not in st.session_state:
        st.session_state.user_data = None

    if "token" not in st.session_state:
        st.session_state.token = None

    if "last_activity" not in st.session_state:
        st.session_state.last_activity = None

def check_session_timeout() -> bool:
    """Verifica si la sesión ha expirado por inactividad"""
    if not st.session_state.get("authenticated", False):
        return False

    last_activity = st.session_state.get("last_activity")
    if not last_activity:
        return True

    # Verificar si pasó más de 1 hora desde la última actividad
    time_elapsed = datetime.now() - last_activity
    if time_elapsed > timedelta(hours=TOKEN_EXPIRY_HOURS):
        logger.info("Sesión expirada por inactividad")
        return True

    return False

def update_activity():
    """Actualiza el timestamp de última actividad"""
    st.session_state.last_activity = datetime.now()

def logout():
    """Cierra la sesión del usuario"""
    logger.info(f"Logout: {st.session_state.get('user_data', {}).get('username', 'unknown')}")
    st.session_state.authenticated = False
    st.session_state.user_data = None
    st.session_state.token = None
    st.session_state.last_activity = None

def is_authenticated() -> bool:
    """Verifica si el usuario está autenticado y la sesión es válida"""
    if not st.session_state.get("authenticated", False):
        return False

    # Verificar timeout de sesión
    if check_session_timeout():
        logout()
        return False

    # Verificar token JWT
    token = st.session_state.get("token")
    if not token:
        logout()
        return False

    payload = verify_token(token)
    if not payload:
        logout()
        return False

    # Actualizar actividad
    update_activity()

    return True

def require_auth(func):
    """Decorador para requerir autenticación en una función"""
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            st.warning("⚠️ Debes iniciar sesión para acceder a esta función")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def configure_user(username: str, password: str, role: str = "user", name: str = "Usuario"):
    """Configura un nuevo usuario (solo para uso inicial)"""
    password_hash = hash_password(password)

    USERS_DB[username] = {
        "username": username,
        "password_hash": password_hash,
        "role": role,
        "name": name
    }

    logger.info(f"Usuario configurado: {username}")
    print(f"\n✅ Usuario configurado exitosamente:")
    print(f"   Username: {username}")
    print(f"   Password Hash: {password_hash}")
    print(f"   Role: {role}")
    print(f"   Name: {name}\n")

def get_session_info() -> Dict[str, Any]:
    """Obtiene información de la sesión actual"""
    if not is_authenticated():
        return {"authenticated": False}

    user_data = st.session_state.get("user_data", {})
    last_activity = st.session_state.get("last_activity")

    time_remaining = None
    if last_activity:
        time_elapsed = datetime.now() - last_activity
        time_remaining = TOKEN_EXPIRY_HOURS * 3600 - time_elapsed.total_seconds()

    return {
        "authenticated": True,
        "username": user_data.get("username"),
        "role": user_data.get("role"),
        "name": user_data.get("name"),
        "last_activity": last_activity,
        "time_remaining_seconds": max(0, time_remaining) if time_remaining else 0
    }

if __name__ == "__main__":
    # Script para generar hash de contraseña
    import sys

    if len(sys.argv) > 1:
        password = sys.argv[1]
        hashed = hash_password(password)
        print(f"\n🔐 Password Hash generado:")
        print(f"   {hashed}\n")
        print(f"Copia este hash a USERS_DB en auth.py\n")
    else:
        print("\n❌ Uso: python auth.py <contraseña>")
        print("   Ejemplo: python auth.py MiContraseñaSegura123\n")
