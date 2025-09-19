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
        # Generar hash del archivo
        file_hash = hashlib.md5(uploaded_file.read()).hexdigest()
        uploaded_file.seek(0)
        
        # Verificar si ya fue importado (saltear en modo demo)
        if not demo_mode and sheets_service:
            if sheets_service.check_file_hash_exists(file_hash):
                logger.warning(f"Archivo {uploaded_file.name} ya fue importado anteriormente")
                return None
        
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
        
        # PASO 5: Análisis de duplicados
        logger.info(f"Analizando duplicados en: {uploaded_file.name}")
        analysis = analyze_duplicates_exhaustive(df, existing_analysis)
        validation = validate_insertion_safety(analysis)
        
        # Preparar datos nuevos
        nuevos = pd.DataFrame()
        if analysis["safe_to_insert"]:
            safe_indices = [item["row_index"] for item in analysis["safe_to_insert"]]
            nuevos = df.iloc[safe_indices].copy()
            
            # Formatear para Google Sheets
            nuevos = self.formatter.format_for_sheets(nuevos)
        
        # Estadísticas del archivo
        stats = {
            "Archivo": uploaded_file.name,
            "HashArchivo": file_hash,
            "FilasLeídas": len(df),
            "NuevosInsertados": len(nuevos),
            "DuplicadosSaltados": analysis.get('summary', {}).get('duplicates', 0),
            "Conflictivos": analysis.get('summary', {}).get('conflicts', 0),
            "FechaHora": datetime.now().isoformat(timespec="seconds"),
        }
        
        result = {
            "file_name": uploaded_file.name,
            "file_hash": file_hash,
            "raw_data": df,
            "new_data": nuevos,
            "analysis": analysis,
            "validation": validation,
            "stats": stats,
        }
        
        logger.info(f"Archivo {uploaded_file.name} procesado: {len(nuevos)} registros nuevos")
        return result

