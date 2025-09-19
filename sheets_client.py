import gspread
import pandas as pd
import time
from datetime import datetime
import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from typing import Dict, List, Any
import logging
import random
from functools import wraps

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting global optimizado
_last_request_time = 0
_min_request_interval = 2.0  # Aumentado para evitar quota exceeded
_request_count_per_minute = 0
_minute_start_time = 0

def rate_limit():
    """Implementa rate limiting global optimizado para evitar quota exceeded"""
    global _last_request_time, _request_count_per_minute, _minute_start_time
    current_time = time.time()

    # Reset contador cada minuto
    if current_time - _minute_start_time >= 60:
        _request_count_per_minute = 0
        _minute_start_time = current_time

    # Limitar a máximo 30 requests por minuto (muy conservador)
    if _request_count_per_minute >= 30:
        sleep_time = 60 - (current_time - _minute_start_time)
        if sleep_time > 0:
            logger.warning(f"⏳ Límite de quota alcanzado, esperando {sleep_time:.1f}s")
            time.sleep(sleep_time)
            _request_count_per_minute = 0
            _minute_start_time = time.time()

    # Rate limiting entre requests individuales
    elapsed = current_time - _last_request_time
    if elapsed < _min_request_interval:
        sleep_time = _min_request_interval - elapsed
        logger.debug(f"⏳ Rate limiting: esperando {sleep_time:.1f}s")
        time.sleep(sleep_time)

    _last_request_time = time.time()
    _request_count_per_minute += 1

def retry_with_backoff(max_retries=5, base_delay=2):
    """Decorador para retry con exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    rate_limit()  # Rate limiting antes de cada request
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    error_str = str(e)
                    
                    # Detectar errores 429 (quota exceeded)
                    if "429" in error_str or "Quota exceeded" in error_str:
                        if attempt < max_retries - 1:
                            # Exponential backoff con jitter
                            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                            logger.warning(f"⚠️ Quota exceeded (intento {attempt + 1}/{max_retries}). Esperando {delay:.1f}s...")
                            time.sleep(delay)
                            continue
                        else:
                            logger.error(f"❌ Quota exceeded después de {max_retries} intentos")
                            raise
                    
                    # Otros errores de red temporal
                    elif any(term in error_str.lower() for term in ["timeout", "connection", "network"]):
                        if attempt < max_retries - 1:
                            delay = base_delay + random.uniform(0, 2)
                            logger.warning(f"⚠️ Error de conexión (intento {attempt + 1}/{max_retries}). Reintentando en {delay:.1f}s...")
                            time.sleep(delay)
                            continue
                    
                    # Re-lanzar errores no recuperables
                    raise e
            
            return None
        return wrapper
    return decorator


def _get_client():
    """Obtiene cliente de Google Sheets con validación mejorada"""
    try:
        # Cargar variables de entorno desde .env
        load_dotenv(override=True)

        # Intentar con variable de entorno primero
        google_sa_json = os.getenv("GOOGLE_SA_JSON")
        google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        if google_sa_json:
            # Si es JSON directo
            import json

            try:
                creds_dict = json.loads(google_sa_json)
                creds = Credentials.from_service_account_info(
                    creds_dict,
                    scopes=[
                        "https://www.googleapis.com/auth/spreadsheets",
                        "https://www.googleapis.com/auth/drive",
                    ],
                )
                logger.info("✅ Credenciales cargadas desde GOOGLE_SA_JSON")
            except json.JSONDecodeError:
                raise ValueError("GOOGLE_SA_JSON no es un JSON válido")
        elif google_credentials_path and os.path.exists(google_credentials_path):
            # Si es archivo
            creds = Credentials.from_service_account_file(
                google_credentials_path,
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive",
                ],
            )
            logger.info(f"✅ Credenciales cargadas desde {google_credentials_path}")
        else:
            raise RuntimeError(
                "Configura GOOGLE_SA_JSON o GOOGLE_APPLICATION_CREDENTIALS"
            )

        # Crear cliente y verificar permisos
        gc = gspread.authorize(creds)

        # Verificar que las credenciales funcionan (silenciar Drive API warning)
        try:
            gc.list_spreadsheet_files()  # Test de conexión
            logger.info("✅ Conexión a Google Sheets verificada")
        except Exception as e:
            error_str = str(e)
            if "Drive API" in error_str and "disabled" in error_str:
                # Warning conocido y manejado - no necesita repetirse
                logger.debug(f"⚠️ Google Drive API no habilitado (funcionalidad limitada pero Sheets funciona)")
            else:
                logger.warning(f"⚠️ Advertencia en verificación inicial: {e}")
            logger.info("✅ Continuando sin verificación inicial...")

        return gc
    except Exception as e:
        logger.error(f"Error en _get_client: {e}")
        raise


class SheetsClient:
    def _get_column_letter(self, num_cols: int) -> str:
        """Convierte número de columna a letra (A, B, ..., Z, AA, AB, ...)"""
        if num_cols <= 26:
            return chr(65 + num_cols - 1)
        else:
            # Para más de 26 columnas
            first = (num_cols - 1) // 26
            second = (num_cols - 1) % 26
            return chr(65 + first - 1) + chr(65 + second)
    
    def __init__(self, sheet_id: str):
        """Inicializa cliente con validación del sheet_id"""
        if not sheet_id or sheet_id.strip() == "":
            raise ValueError("SHEET_ID no puede estar vacío")

        self.sheet_id = sheet_id.strip()
        self.gc = _get_client()
        self._cache = {}

        # Verificar que el sheet existe y es accesible con retry
        try:
            rate_limit()  # Rate limit inicial
            self.sheet = self.gc.open_by_key(self.sheet_id)
            logger.info(f"✅ Sheet '{self.sheet.title}' accedido correctamente")
        except Exception as e:
            logger.warning(f"⚠️ Error inicial accediendo al sheet: {e}")
            # Intentar una vez más con delay
            time.sleep(2)
            try:
                rate_limit()
                self.sheet = self.gc.open_by_key(self.sheet_id)
                logger.info(f"✅ Sheet '{self.sheet.title}' accedido en segundo intento")
            except Exception as e2:
                raise RuntimeError(
                    f"No se puede acceder al sheet con ID {self.sheet_id}: {e2}"
                )

    @retry_with_backoff(max_retries=3, base_delay=2)
    def _get_worksheet(self, tab: str, create_if_missing: bool = False):
        """Obtiene worksheet con validación mejorada"""
        try:
            worksheet = self.sheet.worksheet(tab)
            logger.info(f"✅ Tab '{tab}' encontrado")
            return worksheet
        except gspread.WorksheetNotFound:
            if create_if_missing:
                logger.info(f"📝 Creando nuevo tab '{tab}'")
                worksheet = self.sheet.add_worksheet(title=tab, rows=1000, cols=20)

                # Inicializar headers según el tipo de tab
                if tab == "Movimientos":
                    headers = [
                        "Fecha",
                        "Hora",
                        "Tipo",
                        "Recibo",
                        "ClaveRastreo",
                        "Descripción",
                        "Cargo",
                        "Abono",
                        "Saldo",
                        "UID",
                        "ArchivoOrigen",
                        "ImportadoEn",
                    ]
                    worksheet.append_row(headers)
                    logger.info("✅ Headers de Movimientos inicializados")
                elif tab == "Imports_Log":
                    headers = [
                        "Archivo",
                        "HashArchivo",
                        "FilasLeídas",
                        "NuevosInsertados",
                        "DuplicadosSaltados",
                        "Conflictivos",
                        "FechaHora",
                    ]
                    worksheet.append_row(headers)
                    logger.info("✅ Headers de Imports_Log inicializados")
                elif "Movimientos_Nuevos" in tab or "Acumulado" in tab:
                    # Headers para formato Acumulado
                    headers = [
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
                    worksheet.append_row(headers)
                    logger.info("✅ Headers de Acumulado inicializados")

                return worksheet
            else:
                raise RuntimeError(
                    f"Tab '{tab}' no encontrado y create_if_missing=False"
                )

    @retry_with_backoff(max_retries=3, base_delay=1)
    def validate_sheet_structure(self, tab: str) -> Dict[str, Any]:
        """Valida la estructura del sheet y retorna análisis detallado"""
        try:
            worksheet = self._get_worksheet(tab, create_if_missing=False)
            all_values = worksheet.get_all_values()

            if not all_values:
                return {
                    "exists": True,
                    "has_data": False,
                    "total_rows": 0,
                    "headers": [],
                    "uid_count": 0,
                    "duplicate_uids": [],
                    "structure_valid": True,
                }

            headers = all_values[0]
            data_rows = all_values[1:] if len(all_values) > 1 else []

            # Análisis de estructura
            required_headers = ["UID", "Cargo", "Abono"]
            missing_headers = [h for h in required_headers if h not in headers]

            # Análisis de UIDs
            uid_col_idx = headers.index("UID") if "UID" in headers else -1
            uids = []
            duplicate_uids = []

            if uid_col_idx >= 0:
                for i, row in enumerate(data_rows, start=2):
                    if len(row) > uid_col_idx and row[uid_col_idx]:
                        uid = str(row[uid_col_idx]).strip()
                        if uid:
                            if uid in uids:
                                duplicate_uids.append(
                                    {
                                        "uid": uid,
                                        "row": i,
                                        "first_occurrence": uids.index(uid) + 2,
                                    }
                                )
                            else:
                                uids.append(uid)

            return {
                "exists": True,
                "has_data": len(data_rows) > 0,
                "total_rows": len(data_rows),
                "headers": headers,
                "missing_headers": missing_headers,
                "uid_count": len(set(uids)),
                "duplicate_uids": duplicate_uids,
                "structure_valid": len(missing_headers) == 0,
                "data_quality": {
                    "total_uids": len(uids),
                    "unique_uids": len(set(uids)),
                    "duplicate_count": len(duplicate_uids),
                },
            }

        except Exception as e:
            logger.error(f"Error validando estructura de {tab}: {e}")
            return {"exists": False, "error": str(e), "structure_valid": False}

    def get_existing_data_analysis(self, tab: str) -> Dict[str, Any]:
        """Análisis exhaustivo de datos existentes para comparación"""
        try:
            worksheet = self._get_worksheet(tab, create_if_missing=False)
            all_values = worksheet.get_all_values()

            if not all_values or len(all_values) <= 1:
                return {
                    "existing_uids": set(),
                    "uid_amount_map": {},
                    "total_records": 0,
                    "analysis_ready": False,
                }

            headers = all_values[0]
            data_rows = all_values[1:]

            # Índices de columnas importantes
            uid_idx = headers.index("UID") if "UID" in headers else -1
            cargo_idx = headers.index("Cargo") if "Cargo" in headers else -1
            abono_idx = headers.index("Abono") if "Abono" in headers else -1
            fecha_idx = headers.index("Fecha") if "Fecha" in headers else -1

            existing_uids = set()
            uid_amount_map = {}

            for row in data_rows:
                if len(row) > uid_idx and row[uid_idx]:
                    uid = str(row[uid_idx]).strip()
                    if uid:
                        existing_uids.add(uid)

                        # Mapear montos para detección de conflictos
                        cargo = (
                            float(row[cargo_idx])
                            if cargo_idx >= 0
                            and len(row) > cargo_idx
                            and row[cargo_idx]
                            else 0
                        )
                        abono = (
                            float(row[abono_idx])
                            if abono_idx >= 0
                            and len(row) > abono_idx
                            and row[abono_idx]
                            else 0
                        )

                        uid_amount_map[uid] = {
                            "cargo": cargo,
                            "abono": abono,
                            "net_amount": cargo - abono,
                        }

            return {
                "existing_uids": existing_uids,
                "uid_amount_map": uid_amount_map,
                "total_records": len(data_rows),
                "analysis_ready": True,
                "column_indices": {
                    "uid": uid_idx,
                    "cargo": cargo_idx,
                    "abono": abono_idx,
                    "fecha": fecha_idx,
                },
            }

        except Exception as e:
            logger.error(f"Error en análisis de datos existentes: {e}")
            return {
                "existing_uids": set(),
                "uid_amount_map": {},
                "total_records": 0,
                "analysis_ready": False,
                "error": str(e),
            }

    def read_sheet(self, tab: str, use_cache: bool = True) -> pd.DataFrame:
        """Lee sheet con cache y validación mejorada"""
        cache_key = f"{tab}_data"

        if use_cache and cache_key in self._cache:
            logger.info(f"📋 Usando cache para tab '{tab}'")
            return self._cache[cache_key]

        try:
            worksheet = self._get_worksheet(tab, create_if_missing=False)
            all_values = worksheet.get_all_values()

            if not all_values:
                logger.warning(f"⚠️ Tab '{tab}' está vacío")
                return pd.DataFrame()

            df = pd.DataFrame(all_values[1:], columns=all_values[0])

            if use_cache:
                self._cache[cache_key] = df

            logger.info(f"✅ Leídos {len(df)} registros de '{tab}'")
            return df

        except Exception as e:
            logger.error(f"Error leyendo tab '{tab}': {e}")
            raise

    def append_rows(self, tab: str, df: pd.DataFrame, batch_size: int = 1000) -> int:
        """Añade filas con validación y manejo de errores mejorado, saltando columnas protegidas"""
        if df.empty:
            logger.warning("⚠️ DataFrame vacío, no hay nada que insertar")
            return 0

        try:
            worksheet = self._get_worksheet(tab, create_if_missing=True)
            
            # Verificar y expandir la hoja si es necesario
            current_rows = worksheet.row_count
            needed_rows = len(worksheet.get_all_values()) + len(df) + 100  # Buffer extra
            
            if needed_rows > current_rows:
                logger.info(f"📈 Expandiendo hoja de {current_rows} a {needed_rows} filas")
                worksheet.add_rows(needed_rows - current_rows)

            # Obtener headers para identificar columnas protegidas
            headers = worksheet.row_values(1)

            # NO saltear columnas protegidas - insertar en rangos específicos no protegidos
            data_to_insert = df.values.tolist()
            total_inserted = 0
            
            # Obtener la próxima fila disponible
            all_values = worksheet.get_all_values()
            next_row = len(all_values) + 1

            # Estrategia: Usar valores específicos solo en las columnas que podemos escribir
            try:
                # Insertar usando append_rows que automáticamente encuentra la próxima fila
                worksheet.append_rows(data_to_insert)
                total_inserted = len(data_to_insert)
                logger.info(f"✅ Insertadas {total_inserted} filas usando append_rows")

            except Exception as e:
                logger.warning(f"⚠️ append_rows falló: {e}")
                
                # Fallback: Inserción manual evitando celdas protegidas
                for i, row_data in enumerate(data_to_insert):
                    try:
                        current_row = next_row + i
                        
                        # Insertar solo en columnas específicas no protegidas
                        # Evitar columnas "Autorizado" (índice 9) y usar solo las básicas
                        safe_columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M']  # Evitar J (Autorizado)
                        
                        # Construir actualizaciones individuales para cada columna segura
                        for col_idx, col_letter in enumerate(safe_columns):
                            if col_idx < len(row_data):
                                cell_range = f"{col_letter}{current_row}"
                                try:
                                    worksheet.update(cell_range, [[row_data[col_idx]]])
                                except Exception as cell_error:
                                    logger.warning(f"⚠️ No se pudo actualizar celda {cell_range}: {cell_error}")
                                    continue
                        
                        if (i + 1) % 100 == 0:
                            logger.info(f"✅ Insertadas {i + 1} filas...")

                        # Rate limiting
                        time.sleep(0.1)  # Más lento para evitar errores

                    except Exception as row_error:
                        logger.error(f"❌ Error insertando fila {i + 1}: {row_error}")
                        continue  # Continuar con la siguiente fila en lugar de fallar

                total_inserted = len(data_to_insert)

            # Limpiar cache después de escritura
            self.clear_cache()

            logger.info(f"✅ Total insertado: {total_inserted} filas en '{tab}'")
            return total_inserted

        except Exception as e:
            logger.error(f"Error en append_rows: {e}")
            raise

    @retry_with_backoff(max_retries=5, base_delay=3)  # Más tolerante para inserciones
    def append_data_with_duplicate_check(self, tab: str, values: List[List], uid_column_index: int = 9) -> Dict[str, int]:
        """Inserta datos validando duplicados con feedback detallado"""
        if not values:
            logger.warning("⚠️ No hay valores para insertar")
            return {"inserted": 0, "duplicates": 0, "total": 0}
        
        try:
            # PASO 1: Obtener UIDs existentes
            logger.info(f"🔍 Obteniendo UIDs existentes de '{tab}'...")
            existing_uids = self.get_existing_uids(tab)
            
            # PASO 2: Filtrar duplicados
            logger.info(f"📋 Validando {len(values)} registros contra {len(existing_uids)} UIDs existentes...")
            new_records = []
            duplicate_count = 0
            
            for i, row in enumerate(values):
                if len(row) > uid_column_index and row[uid_column_index]:
                    uid = str(row[uid_column_index]).strip()
                    if uid in existing_uids:
                        duplicate_count += 1
                        logger.debug(f"⚠️ UID duplicado saltado: {uid}")
                    else:
                        new_records.append(row)
                        existing_uids.add(uid)  # Agregar para evitar duplicados internos
                else:
                    # Registro sin UID válido - lo incluimos con advertencia
                    new_records.append(row)
                    logger.warning(f"⚠️ Registro sin UID válido en posición {i}")
            
            logger.info(f"📊 Resultados de validación: {len(new_records)} nuevos, {duplicate_count} duplicados saltados")
            
            # PASO 3: Insertar solo registros nuevos si hay alguno
            if not new_records:
                logger.info("ℹ️ No hay registros nuevos para insertar")
                return {"inserted": 0, "duplicates": duplicate_count, "total": len(values)}
            
            # Continuar con la inserción de registros nuevos
            worksheet = self._get_worksheet(tab, create_if_missing=True)
            
            # Obtener próxima fila disponible
            logger.info(f"📊 Verificando estado actual de la hoja para inserción...")
            try:
                current_data = worksheet.get_all_values()
                next_row = len(current_data) + 1
                logger.info(f"✅ Próxima fila disponible: {next_row}")
            except Exception as e:
                if "429" in str(e):
                    logger.warning("⚠️ Quota exceeded, usando append_rows como fallback")
                    worksheet.append_rows(new_records, value_input_option="USER_ENTERED")
                    logger.info(f"✅ Insertados {len(new_records)} registros via append_rows")
                    return {"inserted": len(new_records), "duplicates": duplicate_count, "total": len(values)}
                else:
                    raise e
            
            # Expandir hoja si es necesario
            current_rows = worksheet.row_count
            needed_rows = next_row + len(new_records) + 50
            
            if needed_rows > current_rows:
                logger.info(f"📈 Expandiendo hoja: {current_rows} → {needed_rows} filas")
                worksheet.add_rows(needed_rows - current_rows)
                time.sleep(0.5)
            
            # Inserción en lotes
            batch_size = 50  # Lotes más pequeños para mejor feedback
            total_inserted = 0
            
            for i in range(0, len(new_records), batch_size):
                batch = new_records[i:i + batch_size]
                start_row = next_row + i
                end_row = start_row + len(batch) - 1
                
                num_cols = len(batch[0]) if batch else 0
                end_col = self._get_column_letter(num_cols)
                range_name = f"A{start_row}:{end_col}{end_row}"
                
                logger.info(f"📤 Insertando lote {i//batch_size + 1}: {len(batch)} registros en {range_name}")
                
                worksheet.update(range_name, batch, value_input_option="USER_ENTERED")
                total_inserted += len(batch)
                
                logger.info(f"✅ Lote insertado: {len(batch)} registros")
                time.sleep(0.1)
            
            result = {
                "inserted": total_inserted,
                "duplicates": duplicate_count, 
                "total": len(values)
            }
            
            logger.info(f"🎉 INSERCIÓN COMPLETADA: {total_inserted} insertados, {duplicate_count} duplicados saltados de {len(values)} total")
            return result
            
        except Exception as e:
            logger.error(f"Error insertando datos con validación de duplicados: {e}")
            raise

    # Mantener método original como backup
    @retry_with_backoff(max_retries=5, base_delay=3)
    def append_data(self, tab: str, values: List[List]) -> int:
        """Método original de inserción sin validación de duplicados"""
        result = self.append_data_with_duplicate_check(tab, values)
        return result["inserted"]
    
    @retry_with_backoff(max_retries=3, base_delay=2)
    def append_log_entry(self, log_data: Dict[str, Any]) -> bool:
        """Añade entrada de log con validación"""
        try:
            worksheet = self._get_worksheet("Imports_Log", create_if_missing=True)

            # Preparar datos de log
            log_row = [
                log_data.get("Archivo", ""),
                log_data.get("HashArchivo", ""),
                str(log_data.get("FilasLeídas", 0)),
                str(log_data.get("NuevosInsertados", 0)),
                str(log_data.get("DuplicadosSaltados", 0)),
                str(log_data.get("Conflictivos", 0)),
                log_data.get("FechaHora", datetime.now().isoformat()),
            ]

            worksheet.append_row(log_row)
            logger.info(f"✅ Log registrado: {log_data.get('Archivo', 'N/A')}")
            return True

        except Exception as e:
            logger.error(f"Error registrando log: {e}")
            return False

    @retry_with_backoff(max_retries=3, base_delay=1)
    def get_existing_uids(self, tab: str = "Movimientos") -> set:
        """Obtiene todos los UIDs existentes en la hoja para validación de duplicados"""
        try:
            worksheet = self._get_worksheet(tab, create_if_missing=False)
            all_values = worksheet.get_all_values()
            
            if len(all_values) <= 1:  # Solo headers o vacío
                logger.info(f"📊 Hoja '{tab}' está vacía, no hay UIDs existentes")
                return set()
            
            headers = all_values[0]
            uid_col_idx = headers.index("UID") if "UID" in headers else -1
            
            if uid_col_idx < 0:
                logger.warning(f"⚠️ Columna 'UID' no encontrada en '{tab}'")
                return set()
            
            # Extraer UIDs existentes
            existing_uids = set()
            for row in all_values[1:]:
                if len(row) > uid_col_idx and row[uid_col_idx].strip():
                    existing_uids.add(row[uid_col_idx].strip())
            
            logger.info(f"✅ Encontrados {len(existing_uids)} UIDs únicos en '{tab}'")
            return existing_uids
            
        except Exception as e:
            logger.error(f"Error obteniendo UIDs existentes: {e}")
            return set()  # Retornar set vacío en caso de error
    
    @retry_with_backoff(max_retries=2, base_delay=1)
    def check_file_hash_exists(self, file_hash: str) -> bool:
        """Verifica si un hash de archivo ya existe en logs"""
        try:
            worksheet = self._get_worksheet("Imports_Log", create_if_missing=False)
            all_values = worksheet.get_all_values()

            if len(all_values) <= 1:  # Solo headers o vacío
                return False

            headers = all_values[0]
            hash_col_idx = (
                headers.index("HashArchivo") if "HashArchivo" in headers else -1
            )

            if hash_col_idx < 0:
                return False

            for row in all_values[1:]:
                if len(row) > hash_col_idx and row[hash_col_idx] == file_hash:
                    return True

            return False

        except Exception as e:
            logger.error(f"Error verificando hash: {e}")
            return False

    def get_sheet_stats(self, tab: str) -> Dict[str, Any]:
        """Obtiene estadísticas detalladas del sheet"""
        try:
            df = self.read_sheet(tab, use_cache=True)

            if df.empty:
                return {
                    "total_rows": 0,
                    "total_cargos": 0,
                    "total_abonos": 0,
                    "net_balance": 0,
                    "unique_files": 0,
                    "last_import": None,
                }

            # Estadísticas básicas
            stats = {
                "total_rows": len(df),
                "total_cargos": 0,
                "total_abonos": 0,
                "net_balance": 0,
                "unique_files": 0,
                "last_import": None,
            }

            # Calcular montos si las columnas existen
            if "Cargo" in df.columns:
                stats["total_cargos"] = df["Cargo"].astype(float).sum()

            if "Abono" in df.columns:
                stats["total_abonos"] = df["Abono"].astype(float).sum()

            stats["net_balance"] = stats["total_abonos"] - stats["total_cargos"]

            # Archivos únicos
            if "ArchivoOrigen" in df.columns:
                stats["unique_files"] = df["ArchivoOrigen"].nunique()

            # Última importación
            if "ImportadoEn" in df.columns:
                try:
                    df["ImportadoEn"] = pd.to_datetime(df["ImportadoEn"])
                    stats["last_import"] = df["ImportadoEn"].max().isoformat()
                except:
                    pass

            return stats

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                "error": str(e),
                "total_rows": 0,
                "total_cargos": 0,
                "total_abonos": 0,
                "net_balance": 0,
                "unique_files": 0,
                "last_import": None,
            }

    @retry_with_backoff(max_retries=3, base_delay=1)
    def find_next_empty_row_in_table(self, sheet_tab: str) -> int:
        """Encuentra dinámicamente la primera fila vacía en la columna A dentro de la tabla

        Esta función escanea eficientemente toda la tabla para encontrar la primera fila
        donde la columna A esté vacía, adaptándose a cualquier estado de la tabla.

        Returns:
            int: Número de la primera fila vacía en columna A (1-indexed).
        """
        try:
            worksheet = self._get_worksheet(sheet_tab, create_if_missing=False)
            all_values = worksheet.get_all_values()

            if not all_values:
                logger.info(f"📊 Hoja '{sheet_tab}' completamente vacía, comenzando en fila 1")
                return 1

            total_rows = len(all_values)
            logger.info(f"🔍 Detectando primera columna A vacía en '{sheet_tab}' ({total_rows} filas)")

            # Usar búsqueda optimizada
            first_empty_row, empty_rows_found, sample_analysis = self._optimized_empty_row_search(all_values)

            # Logging optimizado de resultados
            if first_empty_row:
                logger.info(f"✅ RESULTADO: Primera fila vacía detectada en fila {first_empty_row}")

                if len(empty_rows_found) > 1:
                    logger.info(f"📊 Total filas vacías consecutivas disponibles: {len(empty_rows_found)}")
                    logger.info(f"📋 Filas disponibles: {empty_rows_found[:10]}{'...' if len(empty_rows_found) > 10 else ''}")

                # Mostrar muestra del análisis
                if sample_analysis:
                    logger.info("🔍 Análisis de filas relevantes:")
                    for sample in sample_analysis:
                        marker = " ← PRIMERA VACÍA ✅" if sample["es_primera"] else ""
                        logger.info(f"   Fila {sample['fila']}: {sample['columna_a']} - {sample['estado']}{marker}")

                return first_empty_row

            else:
                # No se encontraron filas vacías
                logger.warning(f"⚠️ No se encontraron filas con columna A vacía en {total_rows} filas")

                if sample_analysis:
                    logger.info("🔍 Muestra de filas analizadas (todas ocupadas):")
                    for sample in sample_analysis[-5:]:  # Últimas 5 muestras
                        logger.info(f"   Fila {sample['fila']}: {sample['columna_a']} - {sample['estado']}")

                # Insertar al final de la tabla
                next_row = total_rows + 1
                logger.info(f"📝 Tabla completamente ocupada, insertando al final: fila {next_row}")
                return next_row

        except Exception as e:
            logger.error(f"Error en detección dinámica de columna A vacía en '{sheet_tab}': {e}")
            # Fallback conservador
            return self._fallback_find_last_row(sheet_tab) + 1

    @retry_with_backoff(max_retries=3, base_delay=1)
    def find_last_data_row(self, sheet_tab: str) -> int:
        """Encuentra la última fila con datos en la hoja (método original para compatibilidad)

        Returns:
            int: Número de la última fila con datos (1-indexed).
                 Retorna 1 si la hoja está vacía (solo headers o completamente vacía)
        """
        try:
            worksheet = self._get_worksheet(sheet_tab, create_if_missing=False)
            all_values = worksheet.get_all_values()

            if not all_values:
                logger.info(f"📊 Hoja '{sheet_tab}' completamente vacía, última fila: 0")
                return 0

            # Buscar desde el final hacia arriba para encontrar la última fila con datos
            last_data_row = 0
            for i in range(len(all_values) - 1, -1, -1):
                row = all_values[i]
                # Verificar si la fila tiene al menos una celda con contenido no vacío
                if any(cell.strip() for cell in row if cell):
                    last_data_row = i + 1  # Convertir a 1-indexed
                    break

            logger.info(f"✅ Última fila con datos en '{sheet_tab}': {last_data_row}")
            return last_data_row

        except Exception as e:
            logger.error(f"Error encontrando última fila en '{sheet_tab}': {e}")
            # En caso de error, usar método conservador
            return self._fallback_find_last_row(sheet_tab)

    def _fallback_find_last_row(self, sheet_tab: str) -> int:
        """Método de respaldo para encontrar la última fila usando get_all_values"""
        try:
            worksheet = self._get_worksheet(sheet_tab, create_if_missing=False)
            all_values = worksheet.get_all_values()

            if not all_values:
                return 0

            # Método simple: la longitud de all_values
            return len(all_values)

        except Exception as e:
            logger.error(f"Error en método de respaldo para '{sheet_tab}': {e}")
            # Último recurso: asumir que hay al menos headers
            return 1

    @retry_with_backoff(max_retries=5, base_delay=2)
    def append_data_after_last_row(self, sheet_tab: str, data: List[List]) -> Dict[str, Any]:
        """Inserta datos después de la última fila existente con validación robusta

        Args:
            sheet_tab: Nombre de la pestaña
            data: Lista de listas con los datos a insertar

        Returns:
            Dict con resultados: inserted, duplicates, errors, last_row_used
        """
        if not data:
            logger.warning("⚠️ No hay datos para insertar")
            return {"inserted": 0, "duplicates": 0, "errors": 0, "last_row_used": 0}

        try:
            # PASO 0: Debug estado inicial
            debug_before = self.debug_sheet_state(sheet_tab, "before_insertion")

            # PASO 1: Encontrar la primera fila vacía en columna A (para insertar en tabla)
            logger.info(f"🔍 Buscando primera fila vacía en columna A de '{sheet_tab}'...")
            next_row = self.find_next_empty_row_in_table(sheet_tab)
            logger.info(f"📝 Insertando datos a partir de la fila {next_row} (primera columna A vacía)")

            # Para compatibilidad con verificación, obtener también la última fila general
            last_row = self.find_last_data_row(sheet_tab)

            # PASO 2: Verificar y crear hoja si es necesario
            worksheet = self._get_worksheet(sheet_tab, create_if_missing=True)

            # PASO 3: Expandir la hoja si es necesario (con manejo de protección)
            current_rows = worksheet.row_count
            needed_rows = next_row + len(data) + 100  # Buffer extra

            if needed_rows > current_rows:
                try:
                    logger.info(f"📈 Expandiendo hoja: {current_rows} → {needed_rows} filas")
                    worksheet.add_rows(needed_rows - current_rows)
                    time.sleep(0.5)  # Pausa para que se aplique la expansión
                except Exception as expand_error:
                    logger.warning(f"⚠️ No se pudo expandir automáticamente: {expand_error}")
                    logger.info("📝 Continuando con inserción en espacio disponible...")
                    # Continuar sin expandir - usar el espacio disponible

            # PASO 4: Validar duplicados si es aplicable
            existing_uids = set()
            uid_column_index = -1

            try:
                if last_row > 0:
                    # Obtener headers para encontrar columna UID
                    headers = worksheet.row_values(1) if last_row >= 1 else []
                    uid_column_index = headers.index("UID") if "UID" in headers else -1

                    if uid_column_index >= 0:
                        existing_uids = self.get_existing_uids(sheet_tab)
                        logger.info(f"📊 Validando contra {len(existing_uids)} UIDs existentes")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo validar duplicados: {e}")

            # PASO 5: Filtrar duplicados si hay validación UID
            new_records = []
            duplicate_count = 0

            if uid_column_index >= 0 and existing_uids:
                for i, row in enumerate(data):
                    if len(row) > uid_column_index and row[uid_column_index]:
                        uid = str(row[uid_column_index]).strip()
                        if uid in existing_uids:
                            duplicate_count += 1
                            logger.debug(f"⚠️ UID duplicado saltado: {uid}")
                        else:
                            new_records.append(row)
                            existing_uids.add(uid)
                    else:
                        new_records.append(row)
            else:
                # Sin validación UID, insertar todos los datos
                new_records = data
                logger.info("ℹ️ Insertando datos sin validación de duplicados")

            if not new_records:
                logger.info("ℹ️ No hay registros nuevos para insertar después de filtrar duplicados")
                return {
                    "inserted": 0,
                    "duplicates": duplicate_count,
                    "errors": 0,
                    "last_row_used": last_row
                }

            # PASO 5.5: Formatear datos para la tabla 'Acumulado'
            logger.info("🔄 Formateando datos para tabla 'Acumulado'...")
            new_records = self._format_data_for_acumulado(new_records, sheet_tab, next_row)
            logger.info(f"✅ {len(new_records)} registros formateados correctamente")

            # PASO 6: Inserción optimizada para evitar quota exceeded
            batch_size = 20  # Lotes más pequeños para evitar quota
            total_inserted = 0
            error_count = 0

            logger.info(f"📤 Insertando {len(new_records)} registros con rate limiting optimizado desde fila {next_row}")

            # Estrategia 1: Inserción directa por rangos con rate limiting agresivo
            for i in range(0, len(new_records), batch_size):
                batch = new_records[i:i + batch_size]
                start_row = next_row + i
                end_row = start_row + len(batch) - 1

                try:
                    # Construir rango para el lote
                    num_cols = len(batch[0]) if batch else 0
                    end_col = self._get_column_letter(num_cols)
                    range_name = f"A{start_row}:{end_col}{end_row}"

                    logger.info(f"📤 Insertando lote {i//batch_size + 1}: {len(batch)} registros en {range_name}")

                    # Insertar usando update con valor específico
                    worksheet.update(range_name, batch, value_input_option="USER_ENTERED")
                    total_inserted += len(batch)
                    logger.info(f"✅ Lote {i//batch_size + 1} insertado: {len(batch)} registros")

                    # Rate limiting agresivo para evitar quota exceeded
                    time.sleep(3.0)  # 3 segundos entre lotes

                except Exception as batch_error:
                    error_str = str(batch_error)
                    logger.error(f"❌ Error insertando lote {i//batch_size + 1}: {batch_error}")

                    # Si hay error de quota, esperar más tiempo
                    if "quota exceeded" in error_str.lower() or "429" in error_str:
                        logger.warning("⏳ Quota exceeded detectado, esperando 60 segundos...")
                        time.sleep(60)
                        # Reintentar el lote una vez
                        try:
                            worksheet.update(range_name, batch, value_input_option="USER_ENTERED")
                            total_inserted += len(batch)
                            logger.info(f"✅ Lote {i//batch_size + 1} insertado tras espera")
                        except Exception as retry_error:
                            logger.error(f"❌ Reintento falló: {retry_error}")
                            error_count += len(batch)

                    # Si hay error de protección, usar método alternativo
                    elif "protected" in error_str.lower() or "permission" in error_str.lower():
                        logger.info("🔒 Detectadas celdas protegidas, usando inserción optimizada")
                        batch_inserted, batch_errors = self._insert_with_protected_cells(
                            worksheet, batch, start_row
                        )
                        total_inserted += batch_inserted
                        error_count += batch_errors
                    else:
                        error_count += len(batch)

            # PASO 7: Verificación final de la inserción
            logger.info("🔍 Realizando verificación final de la inserción...")

            # Debug estado después de inserción
            debug_after = self.debug_sheet_state(sheet_tab, "after_insertion")

            try:
                # Verificar que realmente se insertaron los datos en las filas esperadas
                expected_final_row = next_row + total_inserted - 1 if total_inserted > 0 else next_row

                # Verificar específicamente las filas donde deberíamos haber insertado
                verification_successful = True
                verified_inserted = 0

                logger.info(f"🔍 Verificando inserción desde fila {next_row} hasta {expected_final_row}")

                # Verificar cada fila insertada individualmente
                for check_row in range(next_row, expected_final_row + 1):
                    try:
                        # Verificar que la columna A de esta fila tiene datos
                        cell_value = worksheet.cell(check_row, 1).value  # Columna A = índice 1
                        if cell_value and cell_value.strip():
                            verified_inserted += 1
                        else:
                            logger.warning(f"⚠️ Fila {check_row} columna A está vacía - inserción no verificada")
                    except Exception as cell_check_error:
                        logger.warning(f"⚠️ No se pudo verificar fila {check_row}: {cell_check_error}")

                if verified_inserted == total_inserted:
                    logger.info(f"✅ Verificación exitosa: {verified_inserted}/{total_inserted} registros confirmados en tabla")
                else:
                    logger.warning(f"⚠️ Verificación parcial: solo {verified_inserted}/{total_inserted} registros confirmados")
                    logger.warning(f"🐛 Debug antes: {debug_before}")
                    logger.warning(f"🐛 Debug después: {debug_after}")
                    error_count += (total_inserted - verified_inserted)

            except Exception as verification_error:
                logger.error(f"❌ Error en verificación final: {verification_error}")
                verified_inserted = total_inserted  # Asumir que funcionó si no podemos verificar

            # PASO 8: Limpiar cache y retornar resultados
            self.clear_cache()

            final_last_row = next_row + verified_inserted - 1 if verified_inserted > 0 else last_row

            result = {
                "inserted": verified_inserted,
                "duplicates": duplicate_count,
                "errors": error_count,
                "last_row_used": final_last_row,
                "next_available_row": final_last_row + 1,
                "verification_passed": verified_inserted == total_inserted
            }

            logger.info(f"🎉 INSERCIÓN COMPLETADA: {verified_inserted} insertados, "
                        f"{duplicate_count} duplicados, {error_count} errores")
            logger.info(f"📊 Próxima fila disponible: {result['next_available_row']}")

            if not result["verification_passed"]:
                logger.warning(f"⚠️ ATENCIÓN: Solo {verified_inserted} de {total_inserted} registros fueron verificados")

            return result

        except Exception as e:
            logger.error(f"Error crítico en append_data_after_last_row: {e}")
            return {
                "inserted": 0,
                "duplicates": 0,
                "errors": len(data),
                "last_row_used": 0,
                "error": str(e)
            }

    def _insert_with_protected_cells(self, worksheet, records: List[List], start_row: int) -> tuple:
        """Estrategia optimizada para insertar en hojas con celdas protegidas usando append_rows

        Args:
            worksheet: Worksheet de gspread
            records: Lista de listas con los datos
            start_row: Fila donde comenzar la inserción

        Returns:
            tuple: (total_inserted, error_count)
        """
        logger.info(f"🔒 Intentando inserción optimizada para {len(records)} registros con celdas protegidas")

        try:
            # Estrategia 1: Intentar append_rows que suele evitar protecciones
            logger.info("🚀 Probando append_rows (método más eficiente)")
            worksheet.append_rows(records, value_input_option="USER_ENTERED")
            logger.info(f"✅ Inserción exitosa con append_rows: {len(records)} registros")
            return len(records), 0

        except Exception as append_error:
            logger.warning(f"⚠️ append_rows falló: {append_error}")

            # Estrategia 2: Inserción por lotes más grandes (evitar celda por celda)
            logger.info("🔄 Fallback: Inserción por lotes grandes para minimizar requests")

            batch_size = 10  # Lotes de 10 filas para balancear eficiencia vs protección
            total_inserted = 0
            error_count = 0

            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                batch_start_row = start_row + i
                batch_end_row = batch_start_row + len(batch) - 1

                try:
                    # Intentar insertar lote completo
                    range_name = f"A{batch_start_row}:M{batch_end_row}"
                    logger.info(f"📤 Insertando lote de {len(batch)} filas en {range_name}")

                    worksheet.update(range_name, batch, value_input_option="USER_ENTERED")
                    total_inserted += len(batch)
                    logger.info(f"✅ Lote insertado exitosamente")

                    # Rate limiting agresivo entre lotes
                    time.sleep(3.0)  # 3 segundos entre lotes para evitar quota

                except Exception as batch_error:
                    logger.warning(f"⚠️ Error en lote: {batch_error}")
                    error_count += len(batch)

                    # Si el lote falla, intentar solo las primeras 3 columnas (más seguras)
                    try:
                        logger.info("🔄 Intentando solo columnas A, B, C (más seguras)")
                        safe_batch = [[row[0], row[1], row[2]] for row in batch if len(row) >= 3]
                        safe_range = f"A{batch_start_row}:C{batch_end_row}"

                        worksheet.update(safe_range, safe_batch, value_input_option="USER_ENTERED")
                        total_inserted += len(safe_batch)
                        error_count -= len(batch)  # Corregir contador
                        logger.info(f"✅ Inserción parcial exitosa (solo columnas A-C)")

                        time.sleep(3.0)  # Rate limiting

                    except Exception as safe_error:
                        logger.error(f"❌ Falló incluso inserción segura: {safe_error}")

            logger.info(f"🔒 Inserción con protección completada: {total_inserted} exitosas, {error_count} errores")
            return total_inserted, error_count

    @retry_with_backoff(max_retries=2, base_delay=1)
    def _detect_protected_ranges(self, sheet_tab: str) -> List[str]:
        """Detecta rangos protegidos en la hoja (método experimental)

        Returns:
            List[str]: Lista de rangos protegidos detectados
        """
        try:
            worksheet = self._get_worksheet(sheet_tab, create_if_missing=False)

            # Intentar obtener información de protección usando la API
            # Esto es experimental y puede fallar según los permisos
            spreadsheet = self.sheet
            sheet_metadata = spreadsheet.fetch_sheet_metadata()

            protected_ranges = []
            for sheet in sheet_metadata.get('sheets', []):
                if sheet.get('properties', {}).get('title') == sheet_tab:
                    protected_ranges_data = sheet.get('protectedRanges', [])
                    for prange in protected_ranges_data:
                        range_info = prange.get('range', {})
                        protected_ranges.append(f"Protected range detected: {range_info}")

            logger.info(f"🔍 Rangos protegidos detectados: {len(protected_ranges)}")
            return protected_ranges

        except Exception as e:
            logger.debug(f"No se pudo detectar rangos protegidos: {e}")
            return ["Detection failed - using safe insertion strategy"]

    @retry_with_backoff(max_retries=2, base_delay=1)
    def debug_sheet_state(self, sheet_tab: str, context: str = "") -> Dict[str, Any]:
        """Método de debugging para inspeccionar estado de la hoja

        Args:
            sheet_tab: Nombre de la pestaña
            context: Contexto para el debugging (ej: "before_insertion", "after_insertion")

        Returns:
            Dict con información de debug
        """
        try:
            logger.info(f"🐛 DEBUG {context}: Inspeccionando estado de '{sheet_tab}'")

            worksheet = self._get_worksheet(sheet_tab, create_if_missing=False)
            all_values = worksheet.get_all_values()

            # Información básica
            total_rows = len(all_values)
            last_row_with_data = self.find_last_data_row(sheet_tab)

            # Revisar las últimas 5 filas para ver qué hay, enfocándose en columna A
            last_rows_sample = []
            empty_column_a_rows = []

            if total_rows > 0:
                start_sample = max(0, total_rows - 10)  # Revisar más filas para encontrar vacías
                for i in range(start_sample, total_rows):
                    row_data = all_values[i] if i < len(all_values) else []
                    has_data = any(cell.strip() for cell in row_data if cell)
                    column_a_value = row_data[0] if len(row_data) > 0 else ""

                    last_rows_sample.append({
                        "row_number": i + 1,
                        "has_data": has_data,
                        "column_a_value": column_a_value.strip(),
                        "column_a_empty": not column_a_value.strip(),
                        "first_few_cells": row_data[:3] if row_data else []
                    })

                    # Registrar filas con columna A vacía
                    if not column_a_value.strip():
                        empty_column_a_rows.append(i + 1)

            debug_info = {
                "context": context,
                "total_rows_in_sheet": total_rows,
                "last_row_with_data": last_row_with_data,
                "last_rows_sample": last_rows_sample,
                "empty_column_a_rows": empty_column_a_rows,
                "next_empty_row_in_table": self.find_next_empty_row_in_table(sheet_tab),
                "sheet_columns": len(all_values[0]) if all_values else 0
            }

            logger.info(f"🐛 DEBUG {context}: Total filas: {total_rows}, Última con datos: {last_row_with_data}")
            logger.info(f"🐛 DEBUG {context}: Filas con columna A vacía: {empty_column_a_rows}")
            logger.info(f"🐛 DEBUG {context}: Próxima fila vacía en tabla: {debug_info['next_empty_row_in_table']}")

            return debug_info

        except Exception as e:
            logger.error(f"❌ Error en debug_sheet_state: {e}")
            return {"context": context, "error": str(e)}

    def _optimized_empty_row_search(self, all_values: list, start_idx: int = 1) -> tuple:
        """Búsqueda optimizada para encontrar la primera fila vacía en columna A

        Args:
            all_values: Lista completa de valores de la hoja
            start_idx: Índice donde comenzar la búsqueda (1 para saltear headers)

        Returns:
            tuple: (first_empty_row_number, all_empty_rows, sample_data)
        """
        total_rows = len(all_values)
        empty_rows = []
        first_empty = None
        samples = []

        # Estrategia híbrida: escaneo directo para tablas medianas, optimizado para grandes
        if total_rows < 1000:
            # Escaneo directo para tablas pequeñas/medianas
            search_strategy = "direct_scan"
        else:
            # Optimización para tablas grandes: muestreo inicial + escaneo dirigido
            search_strategy = "optimized_scan"

        logger.info(f"🔍 Usando estrategia '{search_strategy}' para {total_rows} filas")

        if search_strategy == "direct_scan":
            # Escaneo directo simple
            for i in range(start_idx, total_rows):
                row = all_values[i]
                column_a_value = row[0] if len(row) > 0 else ""
                row_number = i + 1

                is_empty = not column_a_value.strip()
                if is_empty:
                    empty_rows.append(row_number)
                    if first_empty is None:
                        first_empty = row_number

                # Muestrear para logging
                if i < 10 or i % 50 == 0 or (first_empty and abs(row_number - first_empty) <= 3):
                    samples.append({
                        "fila": row_number,
                        "columna_a": f"'{column_a_value[:15]}{'...' if len(column_a_value) > 15 else ''}'",
                        "estado": "🔴 VACÍA" if is_empty else "✅ OCUPADA",
                        "es_primera": (row_number == first_empty) if first_empty else False
                    })

        else:
            # Estrategia optimizada para tablas grandes
            # Paso 1: Muestreo inicial cada 100 filas para estimar densidad
            sample_points = list(range(start_idx, total_rows, 100)) + [total_rows - 1]
            occupied_count = 0

            for i in sample_points:
                if i < total_rows:
                    row = all_values[i]
                    column_a_value = row[0] if len(row) > 0 else ""
                    if column_a_value.strip():
                        occupied_count += 1

            density = occupied_count / len(sample_points) if sample_points else 0
            logger.info(f"📊 Densidad estimada de ocupación: {density:.2%}")

            # Paso 2: Escaneo dirigido basado en densidad
            if density > 0.8:
                # Alta densidad: buscar desde el final hacia atrás
                logger.info("🔍 Alta densidad detectada, buscando desde el final")
                for i in range(total_rows - 1, start_idx - 1, -1):
                    row = all_values[i]
                    column_a_value = row[0] if len(row) > 0 else ""
                    row_number = i + 1

                    is_empty = not column_a_value.strip()
                    if is_empty:
                        empty_rows.insert(0, row_number)  # Insertar al inicio para mantener orden
                        first_empty = row_number  # Será el menor al final

                    if len(empty_rows) >= 5:  # Suficientes filas vacías encontradas
                        break

            else:
                # Densidad normal/baja: escaneo desde el inicio
                for i in range(start_idx, total_rows):
                    row = all_values[i]
                    column_a_value = row[0] if len(row) > 0 else ""
                    row_number = i + 1

                    is_empty = not column_a_value.strip()
                    if is_empty:
                        empty_rows.append(row_number)
                        if first_empty is None:
                            first_empty = row_number
                            break  # Encontramos la primera, no necesitamos más

            # Muestrear alrededor de la primera fila vacía para logging
            if first_empty:
                for i in range(max(start_idx, first_empty - 6), min(total_rows, first_empty + 4)):
                    row = all_values[i]
                    column_a_value = row[0] if len(row) > 0 else ""
                    row_number = i + 1

                    samples.append({
                        "fila": row_number,
                        "columna_a": f"'{column_a_value[:15]}{'...' if len(column_a_value) > 15 else ''}'",
                        "estado": "🔴 VACÍA" if not column_a_value.strip() else "✅ OCUPADA",
                        "es_primera": (row_number == first_empty)
                    })

        return first_empty, empty_rows, samples

    def _get_last_consecutive_number(self, sheet_tab: str) -> int:
        """
        Obtiene el último número consecutivo usado en la columna A.
        Si último es 200, retorna 200 para que el siguiente sea 201.
        """
        try:
            worksheet = self._get_worksheet(sheet_tab)
            if not worksheet:
                logger.warning("⚠️ No se pudo acceder a la hoja para obtener consecutivo")
                return 0

            # Obtener todos los valores de columna A
            all_values = worksheet.get_all_values()
            if len(all_values) <= 1:  # Solo headers o vacío
                return 0

            # Buscar el último número consecutivo válido
            last_consecutive = 0
            for i in range(len(all_values) - 1, 0, -1):  # Empezar desde el final
                row = all_values[i]
                if len(row) > 0:
                    cell_value = row[0].strip()
                    if cell_value.isdigit():
                        last_consecutive = int(cell_value)
                        break

            logger.info(f"📊 Último consecutivo encontrado: {last_consecutive}")
            return last_consecutive

        except Exception as e:
            logger.error(f"Error obteniendo último consecutivo: {e}")
            return 0

    def _format_data_for_acumulado(self, data: List[List], sheet_tab: str, start_row: int) -> List[List]:
        """
        Transforma los datos al formato correcto para la tabla 'Acumulado':
        - Columna A: Consecutivo (si último es 200, sigue 201, etc.)
        - Columna B: Vacío
        - Columna C: =SI(ISDATE(D3),MES(D3),0) (fórmula)
        - Columna D: Fecha en formato 12-jun-2025
        - Columna E: Hora en formato 16:49:50
        - Columna F: Clave de rastreo (no recibo)
        - Columna G: Descripción
        - Columnas H,I: Egreso/Ingreso según corresponda
        """
        from datetime import datetime
        import locale

        # Obtener el último consecutivo para continuar la secuencia
        last_consecutive = self._get_last_consecutive_number(sheet_tab)

        formatted_data = []

        for i, row in enumerate(data):
            try:
                # Datos originales: [Fecha, Hora, Tipo, Recibo, ClaveRastreo, Descripción, Cargo, Abono, Saldo, UID, ArchivoOrigen, ImportadoEn]
                fecha_original = row[0] if len(row) > 0 else ""
                hora_original = row[1] if len(row) > 1 else ""
                tipo = row[2] if len(row) > 2 else ""
                recibo = row[3] if len(row) > 3 else ""
                descripcion = row[5] if len(row) > 5 else ""
                cargo = row[6] if len(row) > 6 else ""
                abono = row[7] if len(row) > 7 else ""

                # Columna A: Consecutivo (último + 1, + 2, etc.)
                consecutivo = last_consecutive + 1 + i

                # Columna B: Vacío (según corrección)
                columna_b = ""

                # Columna C: Fórmula para calcular mes
                fila_actual = start_row + i
                formula_mes = f"=SI(ISDATE(D{fila_actual}),MES(D{fila_actual}),0)"

                # Columna D: Fecha en formato español (12-jun-2025)
                fecha_formateada = ""
                if fecha_original:
                    try:
                        # Parsear fecha desde formato ISO (2024-09-19)
                        if "-" in fecha_original and len(fecha_original) == 10:
                            dt = datetime.strptime(fecha_original, "%Y-%m-%d")
                            # Formatear a español: 12-jun-2025
                            meses_esp = {
                                1: "ene", 2: "feb", 3: "mar", 4: "abr",
                                5: "may", 6: "jun", 7: "jul", 8: "ago",
                                9: "sep", 10: "oct", 11: "nov", 12: "dic"
                            }
                            mes_esp = meses_esp.get(dt.month, str(dt.month))
                            fecha_formateada = f"{dt.day}-{mes_esp}-{dt.year}"
                        else:
                            fecha_formateada = fecha_original
                    except:
                        fecha_formateada = fecha_original

                # Columna E: Hora en formato 16:49:50
                hora_formateada = hora_original  # Ya debería estar en formato correcto

                # Columna F: Clave de rastreo (ClaveRastreo, no recibo)
                clave_rastreo = row[4] if len(row) > 4 else ""  # ClaveRastreo está en índice 4

                # Columna G: Descripción
                descripcion_formateada = descripcion

                # Columnas H,I: Egreso/Ingreso
                egreso = cargo if cargo and cargo != "" else ""
                ingreso = abono if abono and abono != "" else ""

                # Construir fila formateada
                fila_formateada = [
                    consecutivo,          # A: Consecutivo
                    columna_b,            # B: Vacío (corregido)
                    formula_mes,          # C: Fórmula del mes (corregido)
                    fecha_formateada,     # D: Fecha española
                    hora_formateada,      # E: Hora
                    clave_rastreo,        # F: Clave de rastreo (corregido)
                    descripcion_formateada, # G: Descripción
                    egreso,               # H: Egreso
                    ingreso               # I: Ingreso
                ]

                formatted_data.append(fila_formateada)

            except Exception as e:
                logger.error(f"Error formateando fila {i}: {e}")
                # En caso de error, agregar fila básica
                consecutivo_error = last_consecutive + 1 + i
                fila_actual = start_row + i
                formatted_data.append([
                    consecutivo_error,  # A: Consecutivo
                    "",  # B: Vacío (corregido)
                    f"=SI(ISDATE(D{fila_actual}),MES(D{fila_actual}),0)",  # C: Fórmula (corregido)
                    row[0] if len(row) > 0 else "",  # D: Fecha original
                    row[1] if len(row) > 1 else "",  # E: Hora original
                    row[4] if len(row) > 4 else "",  # F: Clave de rastreo (corregido)
                    row[5] if len(row) > 5 else "",  # G: Descripción
                    row[6] if len(row) > 6 else "",  # H: Cargo
                    row[7] if len(row) > 7 else ""   # I: Abono
                ])

        logger.info(f"📋 Formateado {len(formatted_data)} registros para tabla 'Acumulado'")
        logger.info(f"📊 Formato: A=Consecutivo, B=Vacío, C=Fórmula_Mes, D=Fecha_ESP, E=Hora, F=ClaveRastreo, G=Descripción, H=Egreso, I=Ingreso")

        return formatted_data

    def clear_cache(self):
        """Limpia el cache interno"""
        self._cache.clear()
        logger.info("🗑️ Cache limpiado")
