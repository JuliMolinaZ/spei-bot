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
    # Formato específico de BanBajío: 21-Jul-2025
    fmts = [
        "%d-%b-%Y",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d-%b-%Y",
        "%d/%m/%y",
        "%Y/%m/%d",
    ]
    for f in fmts:
        try:
            return datetime.strptime(s, f).date().isoformat()
        except Exception:
            pass
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
        mon_en = meses.get(mon.lower(), mon)
        try:
            return datetime.strptime(f"{d}-{mon_en}-{y}", "%d-%b-%Y").date().isoformat()
        except Exception:
            pass
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
    cr = row.get("ClaveRastreo")
    tipo = str(row.get("Tipo") or "")
    if cr and len(str(cr)) >= 6 and tipo.startswith("SPEI"):
        return f"SPEI:{cr}"
    desc = str(row.get("Descripción") or "")
    desc_key = re.sub(r"\s+", "", desc)[:24]
    fecha = row.get("Fecha") or ""
    hora = row.get("Hora") or ""
    recibo = str(row.get("Recibo") or "")
    return f"REC:{recibo}|{fecha}|{hora}|{desc_key}"


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


class BankParser:
    """Parser principal para archivos bancarios"""
    
    def __init__(self):
        """Inicializar el parser"""
        pass
    
    def parse_data(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """
        Parsear datos bancarios desde DataFrame raw
        
        Args:
            df_raw: DataFrame con datos sin procesar
            
        Returns:
            DataFrame parseado y normalizado
        """
        return parse_bank_txt(df_raw)
    
    def classify_transaction_type(self, description: str) -> str:
        """
        Clasificar el tipo de transacción basado en la descripción
        
        Args:
            description: Descripción de la transacción
            
        Returns:
            Tipo de transacción clasificado
        """
        return classify_tipo(description)
    
    def add_unique_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Agregar UIDs únicos al DataFrame
        
        Args:
            df: DataFrame al cual agregar UIDs
            
        Returns:
            DataFrame con UIDs agregados
        """
        return add_uids(df)
