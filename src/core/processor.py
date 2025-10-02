#!/usr/bin/env python3
"""
Procesador Principal - Lógica de negocio para conciliación bancaria
"""

import os
import logging
import hashlib
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd

from .parser import BankParser
from .reader import BankReader
from .formatter import DataFormatter
from services.google_sheets import GoogleSheetsService
from utils.helpers import analyze_duplicates_exhaustive, validate_insertion_safety

logger = logging.getLogger(__name__)

class BankProcessor:
    """Procesador principal de archivos bancarios"""

    def __init__(self):
        """Inicializar el procesador"""
        self.parser = BankParser()
        self.reader = BankReader()
        self.formatter = DataFormatter()

    def sort_data_by_datetime(self, df: pd.DataFrame, ascending: bool = False) -> pd.DataFrame:
        """
        Ordenar datos por fecha y hora (más reciente primero por defecto)

        Args:
            df: DataFrame con datos a ordenar
            ascending: Si True, ordena de más antiguo a más reciente.
                      Si False (default), ordena de más reciente a más antiguo.

        Returns:
            DataFrame ordenado con columna temporal removida
        """
        if df.empty:
            return df

        # Verificar que existan las columnas necesarias
        if "Fecha" not in df.columns or "Hora" not in df.columns:
            logger.warning("DataFrame no contiene columnas Fecha y Hora para ordenar")
            return df

        try:
            # Crear columna temporal combinando fecha y hora
            df_sorted = df.copy()

            # Normalizar fechas a datetime
            def parse_datetime(row):
                try:
                    fecha_str = str(row["Fecha"])
                    hora_str = str(row["Hora"]) if pd.notna(row["Hora"]) else "00:00:00"

                    # Manejar diferentes formatos de fecha
                    if "-" in fecha_str and len(fecha_str.split("-")) == 3:
                        # Formato ISO (2025-01-15) o dd-mmm-yyyy
                        if len(fecha_str.split("-")[0]) == 4:  # YYYY-MM-DD
                            fecha_dt = pd.to_datetime(fecha_str, format="%Y-%m-%d")
                        else:  # dd-mmm-yyyy
                            fecha_dt = pd.to_datetime(fecha_str, format="%d-%b-%Y")
                    else:
                        fecha_dt = pd.to_datetime(fecha_str)

                    # Combinar fecha y hora
                    datetime_combined = pd.to_datetime(f"{fecha_dt.date()} {hora_str}")
                    return datetime_combined
                except Exception as e:
                    logger.warning(f"Error parseando fecha/hora: {e}")
                    return pd.NaT

            df_sorted["_datetime_temp"] = df_sorted.apply(parse_datetime, axis=1)

            # Ordenar por la columna temporal
            df_sorted = df_sorted.sort_values("_datetime_temp", ascending=ascending)

            # Remover columna temporal
            df_sorted = df_sorted.drop(columns=["_datetime_temp"])

            # Resetear índices
            df_sorted = df_sorted.reset_index(drop=True)

            logger.info(f"Datos ordenados: {len(df_sorted)} registros ({'ascendente' if ascending else 'descendente'})")

            return df_sorted

        except Exception as e:
            logger.error(f"Error ordenando datos por fecha/hora: {e}")
            return df
        
    def process_files(
        self, 
        uploaded_files: List, 
        sheet_id: str, 
        sheet_tab: str,
        demo_mode: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Procesar múltiples archivos bancarios
        
        Args:
            uploaded_files: Lista de archivos subidos
            sheet_id: ID de la hoja de Google Sheets
            sheet_tab: Nombre de la pestaña
            demo_mode: Si está en modo demo
            
        Returns:
            Lista de resultados procesados
        """
        logger.info(f"Procesando {len(uploaded_files)} archivo(s)")
        
        all_results = []
        
        # Configurar servicio de Google Sheets
        sheets_service = None
        existing_analysis = {"existing_uids": set(), "uid_amount_map": {}, "total_records": 0, "analysis_ready": False}
        
        if not demo_mode and sheet_id and sheet_id != "TU_SHEET_ID":
            try:
                sheets_service = GoogleSheetsService(sheet_id)
                existing_analysis = sheets_service.get_existing_data_analysis(sheet_tab)
                logger.info(f"Conectado a Google Sheets: {existing_analysis.get('total_records', 0)} registros existentes")
            except Exception as e:
                logger.warning(f"No se pudo conectar a Google Sheets: {e}")
                sheets_service = None
        
        # Procesar cada archivo
        for file_idx, uploaded_file in enumerate(uploaded_files):
            logger.info(f"Procesando archivo {file_idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
            
            try:
                result = self._process_single_file(
                    uploaded_file, 
                    sheets_service, 
                    existing_analysis,
                    demo_mode
                )
                
                if result:
                    all_results.append(result)
                    logger.info(f"Archivo {uploaded_file.name} procesado exitosamente")
                
            except Exception as e:
                logger.error(f"Error procesando {uploaded_file.name}: {e}")
                continue
        
        logger.info(f"Procesamiento completado: {len(all_results)} archivos exitosos")
        return all_results
    
    def _process_single_file(
        self, 
        uploaded_file, 
        sheets_service: Optional[GoogleSheetsService],
        existing_analysis: Dict[str, Any],
        demo_mode: bool
    ) -> Optional[Dict[str, Any]]:
        """
        Procesar un archivo individual
        
        Args:
            uploaded_file: Archivo a procesar
            sheets_service: Servicio de Google Sheets
            existing_analysis: Análisis de datos existentes
            demo_mode: Si está en modo demo
            
        Returns:
            Resultado del procesamiento o None si hay error
        """
        # Generar hash del archivo para registro (NO para validación)
        file_hash = hashlib.md5(uploaded_file.read()).hexdigest()
        uploaded_file.seek(0)

        # NOTA: NO validamos hash de archivo - solo Recibo+Descripción
        # Esto permite cargar el mismo archivo con datos actualizados
        logger.info(f"Procesando archivo {uploaded_file.name} (hash: {file_hash[:8]}...)")
        
        # PASO 1: Lectura del archivo
        logger.info(f"Leyendo archivo: {uploaded_file.name}")
        df_raw = self.reader.read_file(uploaded_file)
        
        if df_raw.empty:
            logger.warning(f"Archivo {uploaded_file.name} está vacío")
            return None
        
        # PASO 2: Parseo y análisis
        logger.info(f"Parseando datos de: {uploaded_file.name}")
        df = self.parser.parse_data(df_raw)
        
        if df.empty:
            logger.warning(f"No se encontraron datos válidos en {uploaded_file.name}")
            return None
        
        # PASO 3: Clasificación de tipos
        logger.info(f"Clasificando tipos de transacciones en: {uploaded_file.name}")
        df['Tipo'] = df['Descripción'].map(self.parser.classify_transaction_type)
        
        # PASO 4: Generación de UIDs
        logger.info(f"Generando UIDs únicos para: {uploaded_file.name}")
        df = self.parser.add_unique_ids(df)
        
        # PASO 5: Formatear PRIMERO para tener Recibo correcto
        logger.info(f"Formateando datos de: {uploaded_file.name}")
        df_formatted = self.formatter.format_for_sheets(df)

        # PASO 6: Validar duplicados por Recibo+Descripción en Google Sheets
        logger.info(f"Validando duplicados por Recibo+Descripción en: {uploaded_file.name}")
        duplicates_info = []
        nuevos_indices = []

        if sheets_service and not demo_mode:
            try:
                # Obtener datos existentes de Google Sheets para validar
                existing_recibo_desc = self._get_existing_recibo_desc(sheets_service)
                logger.info(f"📊 Validando contra {len(existing_recibo_desc)} combinaciones Recibo+Descripción en Sheets")

                # Validar cada registro formateado
                for idx, row in df_formatted.iterrows():
                    recibo = str(row.get("Clave", "")).strip() if pd.notna(row.get("Clave")) else ""
                    desc = str(row.get("Descripción", "")).strip() if pd.notna(row.get("Descripción")) else ""
                    combo = f"{recibo}|{desc}"

                    if combo in existing_recibo_desc:
                        duplicates_info.append({
                            "row_index": idx,
                            "recibo": recibo,
                            "descripcion": desc,
                            "reason": "Recibo+Descripción ya existe en Google Sheets"
                        })
                    else:
                        nuevos_indices.append(idx)
                        existing_recibo_desc.add(combo)  # Evitar duplicados dentro del mismo archivo

                logger.info(f"✅ Validación completada: {len(nuevos_indices)} nuevos, {len(duplicates_info)} duplicados")

            except Exception as e:
                logger.warning(f"⚠️ No se pudo validar contra Google Sheets: {e}")
                # Si falla la validación, asumir que todos son nuevos
                nuevos_indices = list(df_formatted.index)
        else:
            # Sin Google Sheets, todos son nuevos
            nuevos_indices = list(df_formatted.index)

        # Filtrar solo los registros nuevos
        nuevos = df_formatted.iloc[nuevos_indices].copy() if nuevos_indices else pd.DataFrame()

        # PASO 7: Análisis de duplicados por UID (análisis legacy)
        logger.info(f"Analizando duplicados por UID en: {uploaded_file.name}")
        analysis = analyze_duplicates_exhaustive(df, existing_analysis)
        validation = validate_insertion_safety(analysis)
        
        # Estadísticas del archivo
        stats = {
            "Archivo": uploaded_file.name,
            "HashArchivo": file_hash,
            "FilasLeídas": len(df),
            "NuevosInsertados": len(nuevos),
            "DuplicadosSaltados": len(duplicates_info),
            "Conflictivos": 0,
            "FechaHora": datetime.now().isoformat(timespec="seconds"),
        }

        result = {
            "file_name": uploaded_file.name,
            "file_hash": file_hash,
            "raw_data": df,
            "new_data": nuevos,
            "duplicates": duplicates_info,  # Lista de duplicados con info completa
            "analysis": analysis,
            "validation": validation,
            "stats": stats,
        }
        
        logger.info(f"Archivo {uploaded_file.name} procesado: {len(nuevos)} registros nuevos, {len(duplicates_info)} duplicados")
        return result

    def _get_existing_recibo_desc(self, sheets_service: GoogleSheetsService) -> set:
        """
        Obtener combinaciones existentes de Recibo+Descripción desde Google Sheets

        Args:
            sheets_service: Servicio de Google Sheets

        Returns:
            Set de combinaciones "recibo|descripcion"
        """
        try:
            # Importar SheetsClient para acceder a los datos
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from sheets_client import SheetsClient

            sheets_client = SheetsClient(sheets_service.sheet_id)
            worksheet = sheets_service.worksheet.worksheet("Acumulado")

            # Obtener todas las filas
            all_values = worksheet.get_all_values()
            headers = all_values[0] if all_values else []

            # Encontrar índices de columnas
            clave_idx = headers.index("Clave") if "Clave" in headers else -1
            desc_idx = headers.index("Descripción") if "Descripción" in headers else -1

            existing_recibo_desc = set()

            if clave_idx >= 0 and desc_idx >= 0:
                for row in all_values[1:]:  # Saltar headers
                    if len(row) > max(clave_idx, desc_idx):
                        recibo = str(row[clave_idx]).strip() if row[clave_idx] else ""
                        desc = str(row[desc_idx]).strip() if row[desc_idx] else ""
                        if recibo and desc:
                            existing_recibo_desc.add(f"{recibo}|{desc}")

            return existing_recibo_desc

        except Exception as e:
            logger.warning(f"Error obteniendo Recibo+Descripción de Sheets: {e}")
            return set()

