#!/usr/bin/env python3
"""
Servicio de Google Sheets - Manejo profesional de integración con Google Sheets
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Set
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from google.auth.exceptions import GoogleAuthError

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    """Servicio profesional para integración con Google Sheets"""
    
    def __init__(self, sheet_id: str):
        """
        Inicializar el servicio de Google Sheets
        
        Args:
            sheet_id: ID de la hoja de Google Sheets
        """
        self.sheet_id = sheet_id
        self.client = None
        self.worksheet = None
        self._setup_credentials()
        self._connect_to_sheet()
    
    def _setup_credentials(self):
        """Configurar credenciales de Google"""
        try:
            # Intentar cargar desde variable de entorno JSON
            sa_json = os.getenv("GOOGLE_SA_JSON")
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            
            if sa_json:
                # Parsear JSON desde variable de entorno
                credentials_info = json.loads(sa_json)
                credentials = Credentials.from_service_account_info(
                    credentials_info,
                    scopes=['https://www.googleapis.com/auth/spreadsheets',
                           'https://www.googleapis.com/auth/drive']
                )
                logger.info("✅ Credenciales cargadas desde GOOGLE_SA_JSON")
                
            elif credentials_path and os.path.exists(credentials_path):
                # Cargar desde archivo
                credentials = Credentials.from_service_account_file(
                    credentials_path,
                    scopes=['https://www.googleapis.com/auth/spreadsheets',
                           'https://www.googleapis.com/auth/drive']
                )
                logger.info(f"✅ Credenciales cargadas desde {credentials_path}")
                
            else:
                # Buscar archivo local
                local_credentials = "spei-bot-b202259d87e7.json"
                if os.path.exists(local_credentials):
                    credentials = Credentials.from_service_account_file(
                        local_credentials,
                        scopes=['https://www.googleapis.com/auth/spreadsheets',
                               'https://www.googleapis.com/auth/drive']
                    )
                    logger.info(f"✅ Credenciales cargadas desde {local_credentials}")
                else:
                    raise ValueError("No se encontraron credenciales de Google")
            
            self.client = gspread.authorize(credentials)
            
        except Exception as e:
            logger.error(f"Error configurando credenciales: {e}")
            raise
    
    def _connect_to_sheet(self):
        """Conectar a la hoja de Google Sheets"""
        try:
            self.worksheet = self.client.open_by_key(self.sheet_id)
            logger.info(f"✅ Sheet '{self.worksheet.title}' accedido correctamente")
        except Exception as e:
            logger.error(f"Error conectando a la hoja: {e}")
            raise
    
    def get_existing_data_analysis(self, sheet_tab: str) -> Dict[str, Any]:
        """
        Obtener análisis de datos existentes en la hoja
        
        Args:
            sheet_tab: Nombre de la pestaña
            
        Returns:
            Diccionario con análisis de datos existentes
        """
        try:
            # Obtener la pestaña específica
            tab = self.worksheet.worksheet(sheet_tab)
            
            # Obtener todos los datos
            all_data = tab.get_all_records()
            
            if not all_data:
                logger.info("No hay datos existentes en la hoja")
                return {
                    "existing_uids": set(),
                    "uid_amount_map": {},
                    "total_records": 0,
                    "analysis_ready": True
                }
            
            # Convertir a DataFrame para análisis
            df = pd.DataFrame(all_data)
            
            # Extraer UIDs existentes
            existing_uids = set()
            uid_amount_map = {}
            
            if 'UID' in df.columns:
                existing_uids = set(df['UID'].dropna().tolist())
                
                # Crear mapa de UID -> monto para detectar conflictos
                if 'Cargo' in df.columns and 'Abono' in df.columns:
                    for _, row in df.iterrows():
                        uid = row.get('UID')
                        if uid:
                            # Calcular monto neto
                            cargo = float(row.get('Cargo', 0) or 0)
                            abono = float(row.get('Abono', 0) or 0)
                            monto_neto = abono - cargo
                            uid_amount_map[uid] = monto_neto
            
            logger.info(f"Análisis completado: {len(existing_uids)} UIDs únicos encontrados")
            
            return {
                "existing_uids": existing_uids,
                "uid_amount_map": uid_amount_map,
                "total_records": len(all_data),
                "analysis_ready": True
            }
            
        except Exception as e:
            logger.warning(f"Error en análisis de datos existentes: {e}")
            return {
                "existing_uids": set(),
                "uid_amount_map": {},
                "total_records": 0,
                "analysis_ready": False
            }
    
    def check_file_hash_exists(self, file_hash: str) -> bool:
        """
        Verificar si un archivo ya fue importado basado en su hash
        
        Args:
            file_hash: Hash MD5 del archivo
            
        Returns:
            True si el archivo ya fue importado
        """
        try:
            # Buscar en la pestaña de logs
            log_tab = self.worksheet.worksheet("Imports_Log")
            log_data = log_tab.get_all_records()
            
            for record in log_data:
                if record.get('HashArchivo') == file_hash:
                    logger.info(f"Archivo con hash {file_hash[:8]}... ya fue importado")
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error verificando hash de archivo: {e}")
            return False
    
    def insert_results(self, results: List[Dict[str, Any]], sheet_tab: str):
        """
        Insertar resultados procesados en Google Sheets
        
        Args:
            results: Lista de resultados procesados
            sheet_tab: Nombre de la pestaña de destino
        """
        try:
            # Obtener la pestaña de destino
            tab = self.worksheet.worksheet(sheet_tab)
            
            # Preparar datos para inserción
            all_new_data = []
            all_log_entries = []
            
            for result in results:
                if not result["new_data"].empty:
                    # Convertir DataFrame a lista de listas
                    data_to_insert = result["new_data"].values.tolist()
                    all_new_data.extend(data_to_insert)
                
                # Preparar entrada de log
                log_entry = [
                    result["stats"]["Archivo"],
                    result["stats"]["HashArchivo"],
                    result["stats"]["FilasLeídas"],
                    result["stats"]["NuevosInsertados"],
                    result["stats"]["DuplicadosSaltados"],
                    result["stats"]["Conflictivos"],
                    result["stats"]["FechaHora"]
                ]
                all_log_entries.append(log_entry)
            
            # Insertar datos nuevos
            if all_new_data:
                logger.info(f"Insertando {len(all_new_data)} registros nuevos")
                tab.append_rows(all_new_data)
                logger.info("✅ Datos insertados exitosamente")
            
            # Registrar en log de importaciones
            if all_log_entries:
                self._log_import_entries(all_log_entries)
            
            logger.info(f"Proceso de inserción completado: {len(results)} archivos procesados")
            
        except Exception as e:
            logger.error(f"Error insertando resultados: {e}")
            raise
    
    def _log_import_entries(self, log_entries: List[List[str]]):
        """
        Registrar entradas en el log de importaciones
        
        Args:
            log_entries: Lista de entradas de log
        """
        try:
            # Obtener o crear pestaña de logs
            try:
                log_tab = self.worksheet.worksheet("Imports_Log")
            except gspread.WorksheetNotFound:
                # Crear pestaña de logs si no existe
                log_tab = self.worksheet.add_worksheet(
                    title="Imports_Log", 
                    rows=1000, 
                    cols=7
                )
                
                # Agregar headers
                headers = [
                    "Archivo", "HashArchivo", "FilasLeídas", 
                    "NuevosInsertados", "DuplicadosSaltados", 
                    "Conflictivos", "FechaHora"
                ]
                log_tab.append_row(headers)
                logger.info("✅ Pestaña Imports_Log creada")
            
            # Insertar entradas de log
            log_tab.append_rows(log_entries)
            logger.info(f"✅ {len(log_entries)} entradas de log registradas")
            
        except Exception as e:
            logger.warning(f"Error registrando logs: {e}")
    
    def get_sheet_info(self) -> Dict[str, Any]:
        """
        Obtener información de la hoja
        
        Returns:
            Diccionario con información de la hoja
        """
        try:
            return {
                "title": self.worksheet.title,
                "id": self.worksheet.id,
                "url": self.worksheet.url,
                "sheets": [sheet.title for sheet in self.worksheet.worksheets()]
            }
        except Exception as e:
            logger.error(f"Error obteniendo información de la hoja: {e}")
            return {}