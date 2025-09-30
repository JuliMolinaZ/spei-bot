import pandas as pd
import re
from datetime import datetime


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    colmap = {}
    for c in df.columns:
        lc = str(c).strip().lower()
        if "fecha" in lc and "mov" in lc:
            colmap[c] = "Fecha"
        elif lc == "fecha":
            colmap[c] = "Fecha"
        elif "hora" in lc:
            colmap[c] = "Hora"
        elif "recibo" in lc or "referencia" in lc or "folio" in lc:
            colmap[c] = "Recibo"
        elif "descrip" in lc or "concepto" in lc or "detalle" in lc:
            colmap[c] = "Descripción"
        elif "cargo" in lc:
            colmap[c] = "Cargo"
        elif "abono" in lc or "deposito" in lc:
            colmap[c] = "Abono"
        elif "saldo" in lc:
            colmap[c] = "Saldo"
        elif "rastre" in lc:
            colmap[c] = "ClaveRastreo"
        elif lc.startswith("#"):
            colmap[c] = "Idx"
    df2 = df.rename(columns=colmap).copy()
    for col in ["Fecha", "Hora", "Recibo", "Descripción", "Cargo", "Abono", "Saldo"]:
        if col not in df2.columns:
            df2[col] = None
    if "ClaveRastreo" not in df2.columns:

        def extract_cr(desc):
            if not isinstance(desc, str):
                return None
            # Buscar patrones específicos de BanBajío
            m = re.search(r"clave de rastreo:\s*([A-Za-z0-9\-]{6,})", desc, flags=re.I)
            if m:
                return m.group(1)
            m = re.search(r"clave de rastreo\s*([A-Za-z0-9\-]{6,})", desc, flags=re.I)
            if m:
                return m.group(1)
            # Buscar otros patrones de clave de rastreo
            m = re.search(r"\b([A-Za-z0-9]{12,})\b", desc)
            if m:
                return m.group(1)
            return None

        df2["ClaveRastreo"] = df2["Descripción"].map(extract_cr)
    return df2


def _to_iso_date(val):
    if pd.isna(val):
        return None
    s = str(val).strip()
    if not s:
        return None  # Handle empty strings

    # Check for obviously invalid years in slash/dash date formats
    # This catches Excel corruption like "4/01/1901"
    date_patterns = [
        r"(\d{1,2})/(\d{1,2})/(\d{2,4})$",  # MM/DD/YY or MM/DD/YYYY format (full string)
        r"(\d{1,2})-(\d{1,2})-(\d{2,4})$",  # MM-DD-YY or MM-DD-YYYY format (full string)
    ]

    for pattern in date_patterns:
        match = re.match(pattern, s)
        if match:
            year_str = match.group(3)  # Third group is always the year
            try:
                year = int(year_str)
                # Convert 2-digit years to 4-digit (assuming 2000s for < 50, 1900s for >= 50)
                if year < 100:
                    year = 2000 + year if year < 50 else 1900 + year

                # Reject obviously invalid years for bank data
                # Bank data should be from recent years (2020-2030 typically)
                if year < 2020 or year > 2030:
                    print(f"Warning: Rejecting date with suspicious year: {s} (year: {year})")
                    return None
            except (ValueError, TypeError):
                continue
            break  # Only check first pattern that matches

    # Formato específico de BanBajío: 21-Jul-2025 (prioritize this format)
    fmts = [
        "%d-%b-%Y",  # Priority format for BanBajío
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d/%m/%y",
        "%Y/%m/%d",
    ]
    for f in fmts:
        try:
            parsed_date = datetime.strptime(s, f).date()
            # Additional validation for reasonable date range for bank data
            if parsed_date.year < 2020 or parsed_date.year > 2030:
                continue
            return parsed_date.isoformat()
        except Exception:
            pass

    # Handle Spanish month names
    meses = {
        "ene": "Jan",
        "feb": "Feb",
        "mar": "Mar",
        "abr": "Apr",
        "may": "May",
        "jun": "Jun",
        "jul": "Jul",
        "ago": "Aug",
        "sep": "Sep",
        "oct": "Oct",
        "nov": "Nov",
        "dic": "Dec",
    }
    m = re.match(r"(\d{1,2})-([A-Za-z]{3})-(\d{4})", s)
    if m:
        d, mon, y = m.groups()
        year = int(y)
        if year < 2020 or year > 2030:
            print(f"Warning: Rejecting date with suspicious year: {s} (year: {year})")
            return None
        mon_en = meses.get(mon.lower(), mon)
        try:
            return datetime.strptime(f"{d}-{mon_en}-{y}", "%d-%b-%Y").date().isoformat()
        except Exception:
            pass

    print(f"Warning: Could not parse date: {s}")
    return s


def _normalize_numbers(series):
    def parse_num(x):
        if pd.isna(x):
            return 0.0
        s = str(x).strip().replace(",", "")
        try:
            return float(s)
        except Exception:
            try:
                return float(s.replace(",", ".").replace(" ", ""))
            except Exception:
                return 0.0

    return series.map(parse_num)


def classify_tipo(desc):
    if not isinstance(desc, str):
        return ""
    d = desc.lower()
    if "spei" in d:
        if "recibido" in d or "ingreso" in d or "dep" in d:
            return "SPEI Recibido"
        if "enviado" in d or "salida" in d or "transf" in d:
            return "SPEI Enviado"
        return "SPEI"
    if "comision" in d or "comisión" in d:
        return "Comisión"
    if "iva" in d:
        return "IVA"
    if "pos" in d:
        return "POS"
    if "domicilia" in d or "domiciliacion" in d:
        return "Domiciliación"
    if "deposito" in d or "depósito" in d:
        return "Depósito"
    if "retiro" in d:
        return "Retiro"
    if "entrega de recursos" in d:
        return "Entrega de Recursos"
    if "retiro de nomina" in d:
        return "Retiro de Nómina"
    return ""


def _build_uid(row):
    """
    Genera UID único y robusto para cada transacción.
    Usa múltiples campos para garantizar unicidad.
    """
    cr = row.get("ClaveRastreo")
    tipo = str(row.get("Tipo") or "")

    # Para SPEI con clave de rastreo válida
    if cr and len(str(cr)) >= 6 and tipo.startswith("SPEI"):
        return f"SPEI:{cr}"

    # Para todas las demás transacciones, usar combinación robusta de campos
    fecha = row.get("Fecha") or ""
    hora = row.get("Hora") or ""
    recibo = str(row.get("Recibo") or "")
    cargo = str(row.get("Cargo") or "0")
    abono = str(row.get("Abono") or "0")
    desc = str(row.get("Descripción") or "")

    # Limpiar descripción (primeros 20 caracteres sin espacios)
    desc_key = re.sub(r"\s+", "", desc)[:20]

    # UID robusto: fecha|hora|recibo|cargo|abono|descripción
    # Esto garantiza que incluso transacciones similares tengan UIDs únicos
    return f"TXN:{fecha}|{hora}|{recibo}|{cargo}|{abono}|{desc_key}"


def parse_bank_txt(df_raw: pd.DataFrame) -> pd.DataFrame:
    # Verificar si el DataFrame tiene la estructura correcta
    if len(df_raw.columns) < 7:
        # Si no tiene suficientes columnas, intentar leer correctamente
        return pd.DataFrame()

    # Normalizar columnas
    df = _normalize_columns(df_raw)

    # Filtrar filas vacías o con datos inválidos
    df = df.dropna(subset=["Fecha", "Descripción"])

    # Procesar fechas
    df["Fecha"] = df["Fecha"].map(_to_iso_date)

    # Procesar números
    df["Cargo"] = _normalize_numbers(df["Cargo"])
    df["Abono"] = _normalize_numbers(df["Abono"])
    df["Saldo"] = _normalize_numbers(df["Saldo"])

    # Limpiar datos
    df = df[df["Fecha"].notna() & (df["Fecha"] != "")]
    df = df[df["Descripción"].notna() & (df["Descripción"] != "")]

    return df


def add_uids(df: pd.DataFrame) -> pd.DataFrame:
    if "Tipo" not in df.columns:
        df["Tipo"] = df["Descripción"].map(classify_tipo)

    # Ensure ClaveRastreo is extracted if not present
    if "ClaveRastreo" not in df.columns:

        def extract_cr(desc):
            if not isinstance(desc, str):
                return None
            # Buscar patrones específicos de BanBajío
            m = re.search(r"clave de rastreo:\s*([A-Za-z0-9\-]{6,})", desc, flags=re.I)
            if m:
                return m.group(1)
            m = re.search(r"clave de rastreo\s*([A-Za-z0-9\-]{6,})", desc, flags=re.I)
            if m:
                return m.group(1)
            # Buscar otros patrones de clave de rastreo
            m = re.search(r"\b([A-Za-z0-9]{12,})\b", desc)
            if m:
                return m.group(1)
            return None

        df["ClaveRastreo"] = df["Descripción"].map(extract_cr)

    df["UID"] = df.apply(_build_uid, axis=1)
    return df
