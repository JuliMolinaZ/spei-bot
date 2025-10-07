#!/usr/bin/env python3
"""
Sistema de Autenticación para SPEI BOT
Maneja login, validación de sesiones y seguridad
"""

import os
import jwt
import bcrypt
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import streamlit as st
import logging

logger = logging.getLogger(__name__)

# Importar configuración de usuarios
try:
    import sys
    from pathlib import Path
    # Agregar directorio raíz al path para importar users_config
    root_dir = Path(__file__).parent.parent.parent
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))

    from users_config import USERS_CONFIG, SECURITY_CONFIG, get_enabled_users
except ImportError as e:
    logger.error(f"❌ No se pudo importar users_config.py: {e}")
    USERS_CONFIG = {}
    SECURITY_CONFIG = {
        "max_login_attempts": 5,
        "block_duration_minutes": 5,
        "session_timeout_hours": 1,
    }
    get_enabled_users = lambda: {}


class AuthManager:
    """Gestor de autenticación y sesiones"""

    def __init__(self):
        """Inicializar gestor de autenticación"""
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION_2025")
        self.jwt_algorithm = "HS256"
        self.session_timeout = timedelta(hours=SECURITY_CONFIG.get("session_timeout_hours", 1))

        # Inicializar session_state
        if "auth" not in st.session_state:
            st.session_state.auth = {
                "authenticated": False,
                "username": None,
                "role": None,
                "name": None,
                "login_time": None,
                "token": None
            }

        if "login_attempts" not in st.session_state:
            st.session_state.login_attempts = {}

    def hash_password(self, password: str) -> str:
        """
        Generar hash de contraseña con bcrypt

        Args:
            password: Contraseña en texto plano

        Returns:
            Hash de la contraseña
        """
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verificar contraseña contra hash

        Args:
            password: Contraseña en texto plano
            password_hash: Hash almacenado

        Returns:
            True si la contraseña es correcta
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error verificando contraseña: {e}")
            return False

    def is_account_blocked(self, username: str) -> Tuple[bool, Optional[int]]:
        """
        Verificar si una cuenta está bloqueada por intentos fallidos

        Args:
            username: Nombre de usuario

        Returns:
            (bloqueado: bool, tiempo_restante: int en segundos)
        """
        if username not in st.session_state.login_attempts:
            return False, None

        attempts_data = st.session_state.login_attempts[username]
        attempts = attempts_data.get("count", 0)
        last_attempt = attempts_data.get("last_attempt", 0)

        max_attempts = SECURITY_CONFIG.get("max_login_attempts", 5)
        block_duration = SECURITY_CONFIG.get("block_duration_minutes", 5) * 60

        if attempts >= max_attempts:
            time_since_last = time.time() - last_attempt
            if time_since_last < block_duration:
                remaining = int(block_duration - time_since_last)
                return True, remaining
            else:
                # Bloqueo expirado, resetear
                st.session_state.login_attempts[username] = {"count": 0, "last_attempt": 0}
                return False, None

        return False, None

    def record_failed_attempt(self, username: str):
        """
        Registrar intento de login fallido

        Args:
            username: Nombre de usuario
        """
        if username not in st.session_state.login_attempts:
            st.session_state.login_attempts[username] = {"count": 0, "last_attempt": 0}

        st.session_state.login_attempts[username]["count"] += 1
        st.session_state.login_attempts[username]["last_attempt"] = time.time()

    def reset_failed_attempts(self, username: str):
        """
        Resetear intentos fallidos después de login exitoso

        Args:
            username: Nombre de usuario
        """
        if username in st.session_state.login_attempts:
            st.session_state.login_attempts[username] = {"count": 0, "last_attempt": 0}

    def generate_token(self, username: str, role: str) -> str:
        """
        Generar token JWT para sesión

        Args:
            username: Nombre de usuario
            role: Rol del usuario

        Returns:
            Token JWT
        """
        payload = {
            "username": username,
            "role": role,
            "exp": datetime.utcnow() + self.session_timeout,
            "iat": datetime.utcnow()
        }

        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verificar y decodificar token JWT

        Args:
            token: Token JWT

        Returns:
            Payload del token si es válido, None si no
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expirado")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token inválido: {e}")
            return None

    def authenticate(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Autenticar usuario

        Args:
            username: Nombre de usuario
            password: Contraseña

        Returns:
            (éxito: bool, mensaje: str)
        """
        # Verificar si la cuenta está bloqueada
        blocked, remaining = self.is_account_blocked(username)
        if blocked:
            minutes = remaining // 60
            seconds = remaining % 60
            return False, f"⏱️ Cuenta bloqueada. Intenta nuevamente en {minutes}m {seconds}s"

        # Obtener usuarios habilitados
        enabled_users = get_enabled_users()

        # Verificar si el usuario existe
        if username not in enabled_users:
            self.record_failed_attempt(username)
            return False, "❌ Usuario o contraseña incorrectos"

        user_data = enabled_users[username]

        # Verificar contraseña
        if not self.verify_password(password, user_data["password_hash"]):
            self.record_failed_attempt(username)
            attempts_data = st.session_state.login_attempts.get(username, {})
            attempts = attempts_data.get("count", 0)
            max_attempts = SECURITY_CONFIG.get("max_login_attempts", 5)
            remaining_attempts = max_attempts - attempts

            if remaining_attempts > 0:
                return False, f"❌ Usuario o contraseña incorrectos. Te quedan {remaining_attempts} intentos"
            else:
                return False, f"⏱️ Cuenta bloqueada por {SECURITY_CONFIG.get('block_duration_minutes', 5)} minutos"

        # Login exitoso
        self.reset_failed_attempts(username)

        # Generar token
        token = self.generate_token(username, user_data["role"])

        # Actualizar session_state
        st.session_state.auth = {
            "authenticated": True,
            "username": username,
            "role": user_data["role"],
            "name": user_data.get("name", username),
            "login_time": datetime.now(),
            "token": token
        }

        logger.info(f"✅ Login exitoso: {username} ({user_data['role']})")
        return True, f"✅ Bienvenido, {user_data.get('name', username)}!"

    def check_session(self) -> bool:
        """
        Verificar si hay una sesión válida

        Returns:
            True si la sesión es válida
        """
        if not st.session_state.auth.get("authenticated", False):
            return False

        token = st.session_state.auth.get("token")
        if not token:
            return False

        # Verificar token
        payload = self.verify_token(token)
        if not payload:
            # Token inválido o expirado
            self.logout()
            return False

        return True

    def logout(self):
        """Cerrar sesión del usuario"""
        username = st.session_state.auth.get("username", "Usuario")

        st.session_state.auth = {
            "authenticated": False,
            "username": None,
            "role": None,
            "name": None,
            "login_time": None,
            "token": None
        }

        logger.info(f"👋 Logout: {username}")

    def get_session_info(self) -> Dict:
        """
        Obtener información de la sesión actual

        Returns:
            Diccionario con información de sesión
        """
        if not self.check_session():
            return {}

        auth = st.session_state.auth
        login_time = auth.get("login_time")

        if login_time:
            elapsed = datetime.now() - login_time
            remaining = self.session_timeout - elapsed

            return {
                "username": auth.get("username"),
                "name": auth.get("name"),
                "role": auth.get("role"),
                "login_time": login_time,
                "elapsed_minutes": int(elapsed.total_seconds() / 60),
                "remaining_minutes": max(0, int(remaining.total_seconds() / 60)),
                "remaining_seconds": max(0, int(remaining.total_seconds() % 60))
            }

        return {}

    def require_auth(self, allowed_roles: list = None):
        """
        Decorator para requerir autenticación

        Args:
            allowed_roles: Lista de roles permitidos (None = todos)
        """
        if not self.check_session():
            st.warning("⚠️ Sesión expirada. Por favor inicia sesión nuevamente.")
            st.stop()

        if allowed_roles:
            user_role = st.session_state.auth.get("role")
            if user_role not in allowed_roles:
                st.error("❌ No tienes permisos para acceder a esta sección")
                st.stop()


# Función auxiliar para generar hashes (CLI)
def generate_password_hash(password: str) -> str:
    """
    Función auxiliar para generar hash de contraseña
    Uso: python auth.py "mi_contraseña"
    """
    auth = AuthManager()
    return auth.hash_password(password)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        password = sys.argv[1]
        hash_result = generate_password_hash(password)
        print(f"\n🔐 Hash generado para contraseña:")
        print(f"\n{hash_result}\n")
        print("Copia este hash en users_config.py")
    else:
        print("Uso: python auth.py \"tu_contraseña\"")
