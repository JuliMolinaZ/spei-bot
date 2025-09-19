#!/usr/bin/env python3
"""
Aplicación Streamlit Principal - Conciliador Bancario
Interfaz de usuario profesional para conciliación bancaria
"""

import streamlit as st
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Importaciones internas
from config.settings import load_config, validate_config
from services.google_sheets import GoogleSheetsService
from core.processor import BankProcessor
from ui.components import UIComponents
from utils.helpers import setup_logging

logger = logging.getLogger(__name__)

class ConciliadorApp:
    """Aplicación principal del Conciliador Bancario"""
    
    def __init__(self):
        """Inicializar la aplicación"""
        self.config = load_config()
        self.ui_components = UIComponents()
        self.processor = BankProcessor()
        self.sheets_service: Optional[GoogleSheetsService] = None
        
        # Validar configuración
        config_errors = validate_config(self.config)
        if config_errors:
            logger.warning(f"Errores de configuración: {config_errors}")
        
        self._setup_page_config()
        self._setup_session_state()
    
    def _setup_page_config(self):
        """Configurar la página de Streamlit"""
        st.set_page_config(
            page_title="🏦 Conciliador Bancario Pro",
            page_icon="🏦",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': 'https://github.com/tu-repo/conciliador',
                'Report a bug': 'https://github.com/tu-repo/conciliador/issues',
                'About': "Conciliador Bancario Profesional v2.0"
            }
        )
    
    def _setup_session_state(self):
        """Configurar el estado de la sesión"""
        if "app_state" not in st.session_state:
            st.session_state.app_state = {
                "current_step": 0,
                "processed_files": [],
                "processing_stats": {},
                "google_sheets_ready": False,
                "upload_completed": False,
                "config_validated": False
            }
    
    def _setup_sidebar(self) -> Dict[str, Any]:
        """Configurar el sidebar con opciones"""
        with st.sidebar:
            self.ui_components.render_sidebar_header()
            
            # Configuración de Google Sheets
            sheet_config = self._render_sheets_config()
            
            # Modo Demo
            demo_mode = self._render_demo_mode()
            
            # Estado de conexión
            connection_status = self._render_connection_status(sheet_config)
            
            # Estadísticas de sesión
            self._render_session_stats()
            
            return {
                "sheet_id": sheet_config["sheet_id"],
                "sheet_tab": sheet_config["sheet_tab"],
                "demo_mode": demo_mode,
                "connection_status": connection_status
            }
    
    def _render_sheets_config(self) -> Dict[str, str]:
        """Renderizar configuración de Google Sheets"""
        st.markdown("#### 📊 Google Sheets")
        
        sheet_id = st.text_input(
            "ID de la Hoja", 
            value=self.config.get("SHEET_ID", ""),
            placeholder="1BvyC2y3nRhCvKa9Q8yX7zF...",
            help="El ID de tu hoja de Google Sheets"
        )
        
        sheet_tab = st.text_input(
            "Nombre de la Pestaña",
            value=self.config.get("SHEET_TAB", "Movimientos_Nuevos"),
            placeholder="Movimientos_Nuevos",
            help="Nombre de la pestaña donde se insertarán los datos"
        )
        
        return {"sheet_id": sheet_id, "sheet_tab": sheet_tab}
    
    def _render_demo_mode(self) -> bool:
        """Renderizar modo demo"""
        st.markdown("---")
        st.markdown("#### 🧪 Modo Demo")
        
        demo_mode = st.toggle(
            "🚀 Activar Modo Demo", 
            help="Saltará verificaciones de duplicados para testing",
            key="demo_mode"
        )
        
        if demo_mode:
            st.info("🎯 Modo Demo Activo - Sin verificación de duplicados")
            os.environ["DEMO_MODE"] = "true"
        else:
            os.environ.pop("DEMO_MODE", None)
        
        return demo_mode
    
    def _render_connection_status(self, sheet_config: Dict[str, str]) -> bool:
        """Renderizar estado de conexión"""
        st.markdown("---")
        st.markdown("#### 🔗 Estado de Conexión")
        
        sheet_id = sheet_config["sheet_id"]
        
        if sheet_id and sheet_id != "TU_SHEET_ID":
            try:
                self.sheets_service = GoogleSheetsService(sheet_id)
                st.success("✅ Conexión establecida")
                st.session_state.app_state["google_sheets_ready"] = True
                st.info(f"📄 Pestaña: `{sheet_config['sheet_tab']}`")
                return True
            except Exception as e:
                st.error("❌ Error de conexión")
                st.session_state.app_state["google_sheets_ready"] = False
                self.ui_components.show_warning_card(
                    "Problema de Configuración",
                    f"No se pudo conectar: {str(e)[:100]}...",
                    "Verifica tu configuración de Google Sheets"
                )
                return False
        else:
            st.warning("⚠️ Modo de prueba")
            st.session_state.app_state["google_sheets_ready"] = False
            self.ui_components.show_info_card(
                "Modo de Prueba Activo",
                "Configura Google Sheets para funcionalidad completa"
            )
            return False
    
    def _render_session_stats(self):
        """Renderizar estadísticas de sesión"""
        st.markdown("---")
        st.markdown("#### 📈 Estadísticas de Sesión")
        
        if st.session_state.app_state["processed_files"]:
            total_files = len(st.session_state.app_state["processed_files"])
            total_records = sum([
                f.get("total_records", 0) 
                for f in st.session_state.app_state["processed_files"]
            ])
            
            st.metric("Archivos Procesados", total_files)
            st.metric("Registros Totales", total_records)
        else:
            st.info("Sin archivos procesados aún")
    
    def _render_file_upload_tab(self, sidebar_config: Dict[str, Any]):
        """Renderizar pestaña de carga de archivos"""
        st.markdown("## 📁 Carga de Archivos Bancarios")
        
        self.ui_components.render_file_upload_zone()
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            uploaded_files = st.file_uploader(
                "Selecciona archivos bancarios",
                accept_multiple_files=True,
                type=['txt', 'csv'],
                help="Puedes cargar múltiples archivos a la vez",
                label_visibility="collapsed"
            )
        
        with col2:
            self.ui_components.render_upload_tips()
        
        if uploaded_files:
            if st.button("🔍 Analizar Archivos", type="primary", use_container_width=True):
                with st.spinner("Iniciando análisis..."):
                    try:
                        results = self.processor.process_files(
                            uploaded_files, 
                            sidebar_config["sheet_id"], 
                            sidebar_config["sheet_tab"],
                            sidebar_config["demo_mode"]
                        )
                        
                        if results:
                            st.session_state["processing_results"] = results
                            st.session_state.app_state["current_step"] = 1
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error procesando archivos: {e}")
                        logger.error(f"Error en procesamiento: {e}")
        
        return uploaded_files
    
    def _render_processing_tab(self):
        """Renderizar pestaña de procesamiento"""
        if "processing_results" not in st.session_state:
            self.ui_components.show_info_card(
                "Sin Datos Procesados",
                "Primero carga y procesa algunos archivos en la pestaña anterior",
                "📁"
            )
            return
        
        results = st.session_state["processing_results"]
        
        st.markdown("## 📋 Resultados del Procesamiento")
        
        for result in results:
            with st.expander(f"📄 {result['file_name']} - {len(result['new_data'])} registros nuevos"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Total Leídos", result["stats"]["FilasLeídas"])
                    st.metric("Duplicados", result["stats"]["DuplicadosSaltados"])
                
                with col2:
                    st.metric("Nuevos", result["stats"]["NuevosInsertados"])
                    st.metric("Conflictos", result["stats"]["Conflictivos"])
                
                if not result["new_data"].empty:
                    st.markdown("**Vista previa de datos nuevos:**")
                    st.dataframe(result["new_data"].head(), use_container_width=True)
        
        # Botón para proceder a inserción
        total_new = sum([len(r["new_data"]) for r in results])
        if total_new > 0:
            if st.button(f"➡️ Proceder a Inserción ({total_new} registros)", 
                       type="primary", use_container_width=True):
                st.session_state.app_state["current_step"] = 2
                st.rerun()
    
    def _render_insertion_tab(self, sidebar_config: Dict[str, Any]):
        """Renderizar pestaña de inserción"""
        if "processing_results" not in st.session_state:
            self.ui_components.show_info_card(
                "Sin Datos para Insertar",
                "Primero procesa algunos archivos en las pestañas anteriores",
                "🔍"
            )
            return
        
        results = st.session_state["processing_results"]
        total_new = sum([len(r["new_data"]) for r in results])
        
        if total_new == 0:
            self.ui_components.show_info_card(
                "Sin Datos para Insertar",
                "Todos los registros ya existen en tu hoja de Google Sheets",
                "🔄"
            )
            return
        
        st.markdown("## 📊 Inserción a Google Sheets")
        
        # Resumen de inserción
        col1, col2 = st.columns(2)
        
        with col1:
            self.ui_components.render_insertion_summary(total_new, len(results))
        
        with col2:
            self.ui_components.render_time_estimation(total_new)
        
        # Botón de inserción
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button(f"🚀 Insertar {total_new} Registros a Google Sheets", 
                     type="primary", use_container_width=True):
            
            try:
                if self.sheets_service:
                    self.sheets_service.insert_results(results, sidebar_config["sheet_tab"])
                    st.success("✅ Inserción completada exitosamente")
                    st.balloons()
                else:
                    st.warning("⚠️ Modo demo - No se realizó inserción real")
                    
            except Exception as e:
                st.error(f"❌ Error durante la inserción: {e}")
                logger.error(f"Error en inserción: {e}")
    
    def run(self):
        """Ejecutar la aplicación principal"""
        try:
            # Configurar sidebar
            sidebar_config = self._setup_sidebar()
            
            # Renderizar header principal
            self.ui_components.render_main_header()
            
            # Navegación por pestañas
            tabs = ["📁 Cargar Archivos", "🔍 Procesar Datos", "📊 Insertar a Sheets"]
            tab1, tab2, tab3 = st.tabs(tabs)
            
            with tab1:
                self._render_file_upload_tab(sidebar_config)
            
            with tab2:
                self._render_processing_tab()
            
            with tab3:
                self._render_insertion_tab(sidebar_config)
                
        except Exception as e:
            logger.error(f"Error en la aplicación: {e}")
            st.error(f"Error fatal: {e}")

def run_app():
    """Función principal para ejecutar la aplicación"""
    # Crear directorio de logs si no existe
    Path("logs").mkdir(exist_ok=True)
    
    # Configurar logging
    setup_logging()
    
    # Crear y ejecutar la aplicación
    app = ConciliadorApp()
    app.run()

if __name__ == "__main__":
    run_app()

