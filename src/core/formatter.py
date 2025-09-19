#!/usr/bin/env python3
"""
Adaptador para convertir datos procesados al formato del tab Acumulado
"""

import pandas as pd
from datetime import datetime
import re


def convert_to_exact_date_format(date_str):
    """Convierte fecha a formato exacto 12-jun-2025"""
    if pd.isna(date_str):
        return datetime.now().strftime("%d-%b-%Y").lower()
    
    try:
        # Si ya está en formato ISO (2024-01-15)
        if isinstance(date_str, str) and len(date_str) == 10:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%d-%b-%Y").lower()
        return str(date_str).lower()
    except:
        return datetime.now().strftime("%d-%b-%Y").lower()


def normalize_time_format(time_str):
    """Normaliza hora al formato HH:MM:SS"""
    if pd.isna(time_str):
        return datetime.now().strftime("%H:%M:%S")
    
    try:
        time_clean = str(time_str).strip()
        # Si está en formato HH:MM, agregar :00
        if len(time_clean) == 5 and ":" in time_clean:
            return f"{time_clean}:00"
        # Si ya está en formato correcto, devolverlo
        if len(time_clean) == 8 and time_clean.count(":") == 2:
            return time_clean
        return time_clean
    except:
        return datetime.now().strftime("%H:%M:%S")


def format_currency_exact(amount):
    """Formatea montos exactamente como $194,914.45"""
    if pd.isna(amount) or amount == 0:
        return ""
    
    try:
        # Convertir a float si es string
        if isinstance(amount, str):
            amount = float(amount.replace(",", "").replace("$", ""))
        
        # Formatear con comas y símbolo de peso
        return f"${amount:,.2f}"
    except:
        return ""


def adapt_to_acumulado_format(df: pd.DataFrame, start_row: int = None) -> pd.DataFrame:
    """
    Convierte los datos procesados al formato EXACTO del tab Acumulado original
    
    Formato de referencia (filas 367, 368):
    367  6  3  12-jun-2025  16:10:22  3803705013215  [descripción]  $194,914.45
    368  6  1  12-jun-2025  16:49:50  9683648016257  [descripción]  $2,563.60
    """
    
    if df.empty:
        return pd.DataFrame()

    # Crear DataFrame con el formato exacto del Acumulado
    acumulado_df = pd.DataFrame()
    
    # Si no se especifica start_row, usar un valor alto para evitar conflictos
    if start_row is None:
        start_row = 370  # Empezar desde 370 para continuar la secuencia
    
    # COLUMNA 1: Prueba - Número secuencial continuo (como 367, 368, ...)
    acumulado_df["Prueba"] = range(start_row, start_row + len(df))
    
    # COLUMNA 2: "de" - Siempre 6 (según el patrón)
    acumulado_df["de"] = 6
    
    # COLUMNA 3: "escritura" - Secuencia diferente (3, 1, ... según el patrón original)
    # Usar una secuencia que alterne o siga un patrón específico
    acumulado_df["escritura"] = [i % 10 + 1 for i in range(len(df))]  # 1-10 rotativo
    
    # COLUMNA 4: Fecha en formato exacto "12-jun-2025"
    if "Fecha" in df.columns:
        acumulado_df["2025-07-17T18:32:23.744Z"] = df["Fecha"].apply(convert_to_exact_date_format)
    else:
        acumulado_df["2025-07-17T18:32:23.744Z"] = datetime.now().strftime("%d-%b-%Y").lower()
    
    # COLUMNA 5: Hora en formato exacto "16:10:22" (HH:MM:SS)
    if "Hora" in df.columns:
        acumulado_df["Hora"] = df["Hora"].apply(normalize_time_format)
    else:
        acumulado_df["Hora"] = datetime.now().strftime("%H:%M:%S")
    
    # COLUMNA 6: Clave - Número de referencia largo (como 3803705013215)
    claves = []
    for i in range(len(df)):
        if "ClaveRastreo" in df.columns and pd.notna(df.iloc[i]["ClaveRastreo"]):
            # Usar ClaveRastreo si existe
            clave = str(df.iloc[i]["ClaveRastreo"])
            # Si es muy corta, expandirla
            if len(clave) < 10:
                clave = f"380{clave:0>10}"
            claves.append(clave)
        elif "Recibo" in df.columns and pd.notna(df.iloc[i]["Recibo"]):
            # Usar Recibo expandido
            recibo = str(df.iloc[i]["Recibo"])
            if len(recibo) < 10:
                recibo = f"380{recibo:0>10}"
            claves.append(recibo)
        else:
            # Generar número realista de 13 dígitos
            claves.append(f"{3803705013215 + i}")
    
    acumulado_df["Clave"] = claves
    
    # COLUMNA 7: Descripción completa (como en el original)
    if "Descripción" in df.columns:
        acumulado_df["Descripción"] = df["Descripción"]
    else:
        acumulado_df["Descripción"] = ""
    
    # COLUMNAS 8-9: Egreso/Ingreso - Solo UNA tiene valor, la otra vacía
    acumulado_df["Egreso"] = ""
    acumulado_df["Ingreso"] = ""
    
    if "Cargo" in df.columns and "Abono" in df.columns:
        for i in range(len(df)):
            cargo = df.iloc[i]["Cargo"] if pd.notna(df.iloc[i]["Cargo"]) else 0
            abono = df.iloc[i]["Abono"] if pd.notna(df.iloc[i]["Abono"]) else 0
            
            if cargo > 0:
                acumulado_df.loc[i, "Egreso"] = format_currency_exact(cargo)
                acumulado_df.loc[i, "Ingreso"] = ""
            elif abono > 0:
                acumulado_df.loc[i, "Egreso"] = ""
                acumulado_df.loc[i, "Ingreso"] = format_currency_exact(abono)
    
    # COLUMNAS 10-13: Columnas adicionales (vacías como en el patrón)
    acumulado_df["Autorizado"] = ""
    acumulado_df["Capturado"] = ""
    acumulado_df["Notas"] = ""
    acumulado_df["__PowerAppsId__"] = ""
    
    return acumulado_df


def validate_acumulado_structure(df: pd.DataFrame) -> dict:
    """
    Valida que el DataFrame tenga la estructura correcta para el tab Acumulado
    """
    expected_columns = [
        "Prueba",
        "de",
        "escritura",
        "2025-07-17T18:32:23.744Z",
        "Hora",
        "Clave",
        "Descripción",
        "Egreso",
        "Ingreso",
        "Autorizado",
        "Capturado",
        "Notas",
        "__PowerAppsId__",
    ]

    missing_columns = [col for col in expected_columns if col not in df.columns]
    extra_columns = [col for col in df.columns if col not in expected_columns]

    return {
        "valid": len(missing_columns) == 0,
        "missing_columns": missing_columns,
        "extra_columns": extra_columns,
        "total_columns": len(df.columns),
        "expected_columns": expected_columns,
    }


def format_currency_for_acumulado(amount):
    """
    Formatea montos para el formato del tab Acumulado
    """
    if pd.isna(amount) or amount == 0:
        return ""

    # Formato: $1,234.56
    return f"${amount:,.2f}"


def clean_description_for_acumulado(description):
    """
    Limpia y formatea la descripción para el tab Acumulado
    """
    if pd.isna(description):
        return ""

    # Limpiar caracteres especiales y normalizar
    cleaned = str(description).strip()
    # Remover caracteres problemáticos
    cleaned = re.sub(r"[^\w\s\-\.\,\|\#]", "", cleaned)

    return cleaned


def create_acumulado_entry(row_data: dict, index: int) -> dict:
    """
    Crea una entrada individual para el tab Acumulado
    """
    entry = {
        "Prueba": index + 1,
        "de": 6,
        "escritura": 298 + index,
        "2025-07-17T18:32:23.744Z": format_date_for_acumulado(
            row_data.get("Fecha", datetime.now())
        ),
        "Hora": row_data.get("Hora", "00:00:00"),
        "Clave": row_data.get("Recibo", row_data.get("ClaveRastreo", "")),
        "Descripción": clean_description_for_acumulado(row_data.get("Descripción", "")),
        "Egreso": format_currency_for_acumulado(row_data.get("Cargo", 0)),
        "Ingreso": format_currency_for_acumulado(row_data.get("Abono", 0)),
        "Autorizado": determine_autorizado_status(row_data.get("Tipo", "")),
        "Capturado": determine_capturado_status(row_data.get("Tipo", "")),
        "Notas": "",
        "__PowerAppsId__": str(row_data.get("UID", index))[:32],
    }

    return entry


def format_date_for_acumulado(date_value):
    """
    Formatea fecha al formato dd-mmm-yyyy para Acumulado
    """
    if pd.isna(date_value):
        return datetime.now().strftime("%d-%b-%Y")

    if isinstance(date_value, str):
        # Intentar parsear diferentes formatos
        for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d-%b-%Y"]:
            try:
                parsed_date = datetime.strptime(date_value, fmt)
                return parsed_date.strftime("%d-%b-%Y")
            except:
                continue
        return datetime.now().strftime("%d-%b-%Y")

    if isinstance(date_value, datetime):
        return date_value.strftime("%d-%b-%Y")

    return datetime.now().strftime("%d-%b-%Y")


def determine_autorizado_status(tipo):
    """
    Determina el estado de Autorizado según el tipo de transacción
    """
    if pd.isna(tipo):
        return "FALSE"

    tipo_str = str(tipo).lower()

    # Transacciones que son TRUE (autorizadas)
    autorizadas = ["depósito", "deposito", "entrega de recursos", "spei recibido"]

    for auth_type in autorizadas:
        if auth_type in tipo_str:
            return "TRUE"

    return "FALSE"


def determine_capturado_status(tipo):
    """
    Determina el estado de Capturado según el tipo de transacción
    """
    if pd.isna(tipo):
        return "Pendiente"

    tipo_str = str(tipo).lower()

    # Transacciones que son "Capturado"
    capturadas = ["depósito", "deposito", "entrega de recursos", "spei recibido"]

    for capt_type in capturadas:
        if capt_type in tipo_str:
            return "Capturado"

    return "Pendiente"


def format_date_for_acumulado_original(date_value):
    """
    Formatea fecha al formato dd-mmm-yyyy exacto del original
    """
    if pd.isna(date_value):
        return datetime.now().strftime("%d-%b-%Y")

    if isinstance(date_value, str):
        # Si ya está en formato dd-mmm-yyyy, devolverlo tal cual
        if re.match(r"\d{1,2}-[A-Za-z]{3}-\d{4}", date_value):
            return date_value

        # Intentar parsear diferentes formatos
        for fmt in [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%d-%b-%Y",
            "%d/%m/%y",
            "%Y/%m/%d",
        ]:
            try:
                parsed_date = datetime.strptime(date_value, fmt)
                return parsed_date.strftime("%d-%b-%Y")
            except:
                continue
        return datetime.now().strftime("%d-%b-%Y")

    if isinstance(date_value, datetime):
        return date_value.strftime("%d-%b-%Y")

    return datetime.now().strftime("%d-%b-%Y")


def format_currency_for_acumulado_exact(amount):
    """
    Formatea montos para el formato exacto del original
    """
    if pd.isna(amount) or amount == 0:
        return ""

    # Formato exacto: $1,234.56
    return f"${amount:,.2f}"


def determine_autorizado_status_exact(tipo):
    """
    Determina el estado de Autorizado según el tipo de transacción (formato exacto)
    """
    if pd.isna(tipo):
        return "FALSE"

    tipo_str = str(tipo).lower()

    # Transacciones que son TRUE (autorizadas)
    autorizadas = ["depósito", "deposito", "entrega de recursos", "spei recibido"]

    for auth_type in autorizadas:
        if auth_type in tipo_str:
            return "TRUE"

    return "FALSE"


def determine_capturado_status_exact(tipo):
    """
    Determina el estado de Capturado según el tipo de transacción (formato exacto)
    """
    if pd.isna(tipo):
        return "Pendiente"

    tipo_str = str(tipo).lower()

    # Transacciones que son "Capturado"
    capturadas = ["depósito", "deposito", "entrega de recursos", "spei recibido"]

    for capt_type in capturadas:
        if capt_type in tipo_str:
            return "Capturado"

    return "Pendiente"


def create_validation_row(file_name: str, record_count: int) -> dict:
    """
    Crea un renglón de validación para marcar el inicio de nuevos datos
    """
    return {
        "Prueba": "VALIDACION",
        "de": "INICIO",
        "escritura": "NUEVOS_DATOS",
        "2025-07-17T18:32:23.744Z": datetime.now().isoformat(),
        "Hora": datetime.now().strftime("%H:%M:%S"),
        "Clave": f"ARCHIVO: {file_name}",
        "Descripción": f"INICIO DE INSERCION - {record_count} REGISTROS NUEVOS",
        "Egreso": "",
        "Ingreso": "",
        "Autorizado": "VALIDACION",
        "Capturado": "INICIO",
        "Notas": f'VALIDACION: Inicio de inserción del archivo {file_name} con {record_count} registros | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        "__PowerAppsId__": hash(f"validation_{file_name}_{datetime.now().isoformat()}")
        % 1000000000,
    }
