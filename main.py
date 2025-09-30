#!/usr/bin/env python3
"""
SPEI BOT - Aplicación Principal
Sistema profesional de conciliación automática de transacciones SPEI con Google Sheets
"""

import os
import sys
import logging
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configurar logging para producción
# Nivel WARNING para consola (solo errores importantes)
# Nivel INFO para archivo (registro completo)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Configurar nivel WARNING para la consola en producción
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.WARNING)  # Solo warnings y errores en consola
console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

# Obtener el logger root y ajustar handlers
root_logger = logging.getLogger()
root_logger.handlers = [
    logging.FileHandler('logs/app.log'),  # INFO para archivo
    console_handler  # WARNING para consola
]

logger = logging.getLogger(__name__)

def main():
    """Función principal de la aplicación"""
    try:
        logger.info("Iniciando SPEI BOT v2.0")

        # Importar y ejecutar la aplicación Streamlit
        from ui.app import run_app
        run_app()

    except Exception as e:
        logger.error(f"Error fatal en la aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
