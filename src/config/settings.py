#!/usr/bin/env python3
"""
Configuración Profesional - Conciliador Bancario
Manejo centralizado de configuración y variables de entorno
"""

import os
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class Config:
    """Clase de configuración profesional"""
    
    def __init__(self):
        """Inicializar configuración"""
        self._load_environment()
        self._validate_required_settings()
    
    def _load_environment(self):
        """Cargar variables de entorno"""
        load_dotenv(override=True)
        
        self.settings = {
            # Configuración básica
            "SHEET_ID": os.getenv("SHEET_ID", ""),
            "SHEET_TAB": os.getenv("SHEET_TAB", "Movimientos_Nuevos"),
            
            # Configuración avanzada
            "BATCH_SIZE": int(os.getenv("BATCH_SIZE", "1000")),
            "ENABLE_CACHE": os.getenv("ENABLE_CACHE", "true").lower() == "true",
            "LOG_IMPORTS": os.getenv("LOG_IMPORTS", "true").lower() == "true",
            
            # Credenciales de Google
            "GOOGLE_SA_JSON": os.getenv("GOOGLE_SA_JSON", ""),
            "GOOGLE_APPLICATION_CREDENTIALS": os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""),
            
            # Configuración de logging
            "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
            "LOG_FILE": os.getenv("LOG_FILE", "logs/app.log"),
            
            # Configuración de seguridad
            "DEMO_MODE": os.getenv("DEMO_MODE", "false").lower() == "true",
            "MAX_FILE_SIZE": int(os.getenv("MAX_FILE_SIZE", "200")),  # MB
            
            # Configuración de rendimiento
            "CACHE_TTL": int(os.getenv("CACHE_TTL", "300")),  # segundos
            "RATE_LIMIT": int(os.getenv("RATE_LIMIT", "100")),  # requests por minuto
        }
    
    def _validate_required_settings(self):
        """Validar configuraciones requeridas"""
        required_settings = ["SHEET_ID", "SHEET_TAB"]
        
        for setting in required_settings:
            if not self.settings.get(setting):
                logger.warning(f"Configuración requerida faltante: {setting}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtener valor de configuración"""
        return self.settings.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """Obtener toda la configuración"""
        return self.settings.copy()
    
    def is_demo_mode(self) -> bool:
        """Verificar si está en modo demo"""
        return self.settings.get("DEMO_MODE", False)
    
    def is_production(self) -> bool:
        """Verificar si está en modo producción"""
        return not self.is_demo_mode() and bool(self.settings.get("SHEET_ID"))

# Instancia global de configuración
config = Config()

def load_config() -> Dict[str, Any]:
    """Cargar configuración (función de compatibilidad)"""
    return config.get_all()


def validate_config(config):
    """Valida que la configuración sea correcta"""
    errors = []

    if not config["SHEET_ID"]:
        errors.append("SHEET_ID no está configurado")

    if not config["SHEET_TAB"]:
        errors.append("SHEET_TAB no está configurado")

    if config["BATCH_SIZE"] < 1 or config["BATCH_SIZE"] > 10000:
        errors.append("BATCH_SIZE debe estar entre 1 y 10000")

    return errors


def get_google_credentials():
    """Obtiene las credenciales de Google"""
    load_dotenv(override=True)  # Cargar variables de entorno desde .env
    sa_json = os.getenv("GOOGLE_SA_JSON")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if not sa_json and not credentials_path:
        raise ValueError(
            "Debes configurar GOOGLE_SA_JSON o GOOGLE_APPLICATION_CREDENTIALS"
        )

    return {"sa_json": sa_json, "credentials_path": credentials_path}
