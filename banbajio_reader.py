#!/usr/bin/env python3
"""
Lector especializado para archivos de BanBajío
"""

import pandas as pd
import io

def is_banbajio_format(content: str) -> bool:
    """
    Detecta si el archivo es formato BanBajío
    """
    lines = content.split('\n')
    if len(lines) < 2:
        return False
    
    # Verificar que la segunda línea tenga el formato esperado de BanBajío
    second_line = lines[1].strip()
    return second_line.startswith('#,Fecha Movimiento,Hora,Recibo,Descripción')

def read_banbajio_file(content: str) -> pd.DataFrame:
    """
    Lee un archivo de formato BanBajío correctamente
    
    Formato esperado:
    Línea 1: Metadata (empresa, cuenta, etc.) - se ignora
    Línea 2: Headers (#,Fecha Movimiento,Hora,Recibo,Descripción,Cargos,Abonos,Saldo)
    Línea 3+: Datos reales
    """
    lines = content.split('\n')
    
    if len(lines) < 3:
        raise ValueError("Archivo BanBajío debe tener al menos 3 líneas")
    
    # Tomar desde la línea 2 en adelante (línea 2 = headers, línea 3+ = datos)
    data_content = '\n'.join(lines[1:])
    
    # Leer con pandas
    df = pd.read_csv(io.StringIO(data_content), sep=',')
    
    # Limpiar datos vacíos al final
    df = df.dropna(how='all')
    
    return df

def read_smart_csv(uploaded_file_or_content):
    """
    Lee un archivo CSV de manera inteligente, detectando si es BanBajío o formato estándar
    """
    # Si es un uploaded_file de streamlit, leer el contenido
    if hasattr(uploaded_file_or_content, 'read'):
        content = uploaded_file_or_content.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        uploaded_file_or_content.seek(0)  # Reset para otras operaciones
    else:
        content = uploaded_file_or_content
    
    # Detectar si es formato BanBajío
    if is_banbajio_format(content):
        print("🏦 Detectado formato BanBajío - usando lector especializado")
        return read_banbajio_file(content)
    else:
        print("📋 Formato CSV estándar - usando pandas normal")
        return pd.read_csv(io.StringIO(content), sep=None, engine="python")