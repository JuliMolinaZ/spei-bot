#!/usr/bin/env python3
"""
Configuración de Usuarios para SPEI BOT - EJEMPLO
IMPORTANTE: Copia este archivo a 'users_config.py' y configura tus usuarios reales

Para generar hashes de contraseña, ejecuta:
    python auth.py "tu_contraseña_aquí"
"""

# Usuarios del sistema
USERS_CONFIG = {
    # Usuario administrador ejemplo
    "admin": {
        "username": "admin",
        "password_hash": "$2b$12$LKzx.oqvVZqKJX8qQxK5Oe7HjBK8Zqp5vKGLKJxPBMXo0Vy3vR0yS",  # Hash de "admin123"
        "role": "admin",
        "name": "Administrador SPEI BOT",
        "enabled": True
    },

    # Ejemplo de usuario adicional (comentado)
    # "usuario1": {
    #     "username": "usuario1",
    #     "password_hash": "$2b$12$...",  # Generar con: python auth.py "contraseña"
    #     "role": "user",
    #     "name": "Usuario Ejemplo 1",
    #     "enabled": True
    # },

    # "finanzas": {
    #     "username": "finanzas",
    #     "password_hash": "$2b$12$...",  # Generar con: python auth.py "contraseña"
    #     "role": "user",
    #     "name": "Equipo de Finanzas",
    #     "enabled": True
    # }
}

# Configuración de seguridad
SECURITY_CONFIG = {
    "max_login_attempts": 5,          # Intentos máximos antes de bloqueo
    "block_duration_minutes": 5,      # Duración del bloqueo en minutos
    "session_timeout_hours": 1,       # Timeout de sesión por inactividad
    "require_strong_password": True,  # Requiere contraseñas fuertes
    "password_min_length": 8,         # Longitud mínima de contraseña
}

def get_enabled_users():
    """Retorna solo usuarios habilitados"""
    return {
        username: user_data
        for username, user_data in USERS_CONFIG.items()
        if user_data.get("enabled", True)
    }


# ========================
# INSTRUCCIONES DE USO
# ========================
#
# 1. Copia este archivo a 'users_config.py':
#    cp users_config.example.py users_config.py
#
# 2. Genera hashes para tus contraseñas:
#    python auth.py "MiContraseñaSegura123"
#
# 3. Edita users_config.py con tus usuarios y hashes reales
#
# 4. ⚠️ NUNCA subas users_config.py a Git (está en .gitignore)
#
# 5. En producción, usa contraseñas fuertes:
#    - Mínimo 8 caracteres
#    - Mayúsculas y minúsculas
#    - Números y símbolos
#    - No usar palabras comunes
