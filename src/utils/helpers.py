#!/usr/bin/env python3
"""
Utilidades Profesionales - Conciliador Bancario
Funciones helper y utilidades generales
"""

import os
import logging
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Set, Tuple
import pandas as pd

logger = logging.getLogger(__name__)

def setup_logging(log_level: str = "INFO", log_file: str = "logs/app.log"):
    """
    Configurar logging profesional
    
    Args:
        log_level: Nivel de logging
        log_file: Archivo de log
    """
    # Crear directorio de logs si no existe
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configurar formato de logging
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configurar handler para archivo
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # Configurar handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

def analyze_duplicates_exhaustive(df: pd.DataFrame, existing_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Análisis exhaustivo de duplicados con mejoras de rendimiento

    Args:
        df: DataFrame con datos a analizar
        existing_analysis: Análisis de datos existentes

    Returns:
        Diccionario con análisis de duplicados
    """
    logger.info("Iniciando análisis exhaustivo de duplicados")
    
    existing_uids = existing_analysis.get("existing_uids", set())
    uid_amount_map = existing_analysis.get("uid_amount_map", {})
    
    safe_to_insert = []
    duplicates = []
    conflicts = []
    
    for idx, row in df.iterrows():
        uid = row.get('UID')
        if not uid:
            continue

        # Calcular monto neto
        cargo = float(row.get('Cargo', 0) or 0)
        abono = float(row.get('Abono', 0) or 0)
        monto_neto = abono - cargo
        
        if uid in existing_uids:
            # Verificar si es conflicto (mismo UID, monto diferente)
            existing_amount = uid_amount_map.get(uid, 0)
            if abs(existing_amount - monto_neto) > 0.01:  # Tolerancia de 1 centavo
                conflicts.append({
                    "row_index": idx,
                        "uid": uid,
                    "existing_amount": existing_amount,
                    "new_amount": monto_neto,
                    "difference": monto_neto - existing_amount
                })
                logger.warning(f"Conflicto detectado para UID {uid}: {existing_amount} vs {monto_neto}")
            else:
                duplicates.append({
                    "row_index": idx,
                    "uid": uid,
                    "amount": monto_neto
                })
        else:
            safe_to_insert.append({
                "row_index": idx,
                "uid": uid,
                "amount": monto_neto
            })
    
    summary = {
        "safe_to_insert": len(safe_to_insert),
        "duplicates": len(duplicates),
        "conflicts": len(conflicts),
        "total_analyzed": len(df)
    }
    
    logger.info(f"Análisis completado: {summary}")
    
    return {
        "safe_to_insert": safe_to_insert,
        "duplicates": duplicates,
        "conflicts": conflicts,
        "summary": summary
    }

def validate_insertion_safety(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validar seguridad de inserción

    Args:
        analysis: Resultado del análisis de duplicados

    Returns:
        Diccionario con validación de seguridad
    """
    safe_count = analysis.get("summary", {}).get("safe_to_insert", 0)
    conflict_count = analysis.get("summary", {}).get("conflicts", 0)
    
    is_safe = conflict_count == 0
    warnings = []
    
    if conflict_count > 0:
        warnings.append(f"{conflict_count} conflictos detectados")
    
    if safe_count == 0:
        warnings.append("No hay registros seguros para insertar")
    
    return {
        "is_safe": is_safe,
        "safe_count": safe_count,
        "conflict_count": conflict_count,
        "warnings": warnings,
        "recommendation": "Proceder con inserción" if is_safe else "Revisar conflictos antes de insertar"
    }

def estimate_processing_time(record_count: int) -> float:
    """
    Estimar tiempo de procesamiento
    
    Args:
        record_count: Número de registros
        
    Returns:
        Tiempo estimado en segundos
    """
    # Estimación basada en experiencia: ~0.1 segundos por registro
    base_time = record_count * 0.1
    
    # Agregar overhead mínimo
    overhead = 5
    
    return base_time + overhead

def generate_file_hash(file_content: bytes) -> str:
    """
    Generar hash MD5 de archivo
    
    Args:
        file_content: Contenido del archivo en bytes
        
    Returns:
        Hash MD5 como string hexadecimal
    """
    return hashlib.md5(file_content).hexdigest()

def format_currency(amount: float) -> str:
    """
    Formatear cantidad como moneda mexicana
    
    Args:
        amount: Cantidad a formatear
        
    Returns:
        String formateado como moneda
    """
    return f"${amount:,.2f} MXN"

def format_datetime(dt: datetime) -> str:
    """
    Formatear datetime para mostrar
    
    Args:
        dt: Datetime a formatear
        
    Returns:
        String formateado
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    División segura evitando división por cero
    
    Args:
        numerator: Numerador
        denominator: Denominador
        default: Valor por defecto si denominador es cero
        
    Returns:
        Resultado de la división o valor por defecto
    """
    if denominator == 0:
        return default
    return numerator / denominator

def validate_file_size(file_size: int, max_size_mb: int = 200) -> bool:
    """
    Validar tamaño de archivo

    Args:
        file_size: Tamaño del archivo en bytes
        max_size_mb: Tamaño máximo en MB

    Returns:
        True si el archivo es válido
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes

def clean_filename(filename: str) -> str:
    """
    Limpiar nombre de archivo para uso seguro
    
    Args:
        filename: Nombre original del archivo
        
    Returns:
        Nombre limpio y seguro
    """
    # Remover caracteres peligrosos
    dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    clean_name = filename
    
    for char in dangerous_chars:
        clean_name = clean_name.replace(char, '_')
    
    # Limitar longitud
    if len(clean_name) > 100:
        name, ext = os.path.splitext(clean_name)
        clean_name = name[:95] + ext
    
    return clean_name

def create_backup_filename(original_filename: str) -> str:
    """
    Crear nombre de archivo para backup
    
    Args:
        original_filename: Nombre original
        
    Returns:
        Nombre para backup con timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(original_filename)
    return f"{name}_backup_{timestamp}{ext}"

def get_file_extension(filename: str) -> str:
    """
    Obtener extensión de archivo en minúsculas
    
    Args:
        filename: Nombre del archivo
        
    Returns:
        Extensión en minúsculas
    """
    return os.path.splitext(filename)[1].lower()

def is_supported_file_type(filename: str) -> bool:
    """
    Verificar si el tipo de archivo es soportado
    
    Args:
        filename: Nombre del archivo
        
    Returns:
        True si es soportado
    """
    supported_extensions = ['.txt', '.csv']
    extension = get_file_extension(filename)
    return extension in supported_extensions

def log_performance(func):
    """
    Decorator para logging de rendimiento

    Args:
        func: Función a decorar

    Returns:
        Función decorada
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logger.info(f"{func.__name__} ejecutado en {execution_time:.2f} segundos")
        
        return result
    
    return wrapper

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator para reintentar en caso de fallo
    
    Args:
        max_retries: Número máximo de reintentos
        delay: Delay entre reintentos en segundos
        
    Returns:
        Función decorada
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Intento {attempt + 1} falló para {func.__name__}: {e}")
                        time.sleep(delay)
                    else:
                        logger.error(f"Todos los intentos fallaron para {func.__name__}")
            
            raise last_exception
        
        return wrapper
    return decorator