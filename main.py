#!/usr/bin/env python3
"""
Conciliador Bancario - Aplicación Principal
Sistema profesional de conciliación de movimientos bancarios con Google Sheets
"""

import os
import sys
import logging
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Función principal de la aplicación"""
    try:
        logger.info("Iniciando Conciliador Bancario v2.0")
        
        # Importar y ejecutar la aplicación Streamlit
        from ui.app import run_app
        run_app()
        
    except Exception as e:
        logger.error(f"Error fatal en la aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
