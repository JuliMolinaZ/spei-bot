#!/usr/bin/env python3
"""
Aplicación Streamlit Principal - Conciliador Bancario
Interfaz de usuario profesional para conciliación bancaria
"""

import os
import time
import streamlit as st
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Configurar página ANTES de cualquier otra cosa
st.set_page_config(
    page_title="SPEI-BOT",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/JuliMolinaZ/spei-bot',
        'Report a bug': 'https://github.com/JuliMolinaZ/spei-bot/issues',
        'About': "SPEI-BOT - Sistema Profesional de Conciliación Bancaria v2.0"
    }
)

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
        
        self._setup_session_state()
    
    
    def _setup_session_state(self):
        """Configurar el estado de la sesión"""
        if "app_state" not in st.session_state:
            st.session_state.app_state = {
                "current_step": 0,
                "processed_files": [],
                "processing_stats": {},
                "google_sheets_ready": False,
                "upload_completed": False,
                "config_validated": False,
                "data_sorted": False,
                "sort_order": "desc"  # desc = más reciente primero, asc = más antiguo primero
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
        """Renderizar modo demo - DESHABILITADO EN PRODUCCIÓN"""
        # PRODUCCIÓN: Modo demo siempre desactivado
        # Para habilitar modo demo en desarrollo, cambiar return False a return True
        return False

        # CÓDIGO COMENTADO PARA DESARROLLO:
        # st.markdown("---")
        # st.markdown("#### 🧪 Modo Demo")
        #
        # demo_mode = st.toggle(
        #     "🚀 Activar Modo Demo",
        #     help="Saltará verificaciones de duplicados para testing",
        #     key="demo_mode"
        # )
        #
        # if demo_mode:
        #     st.info("🎯 Modo Demo Activo - Sin verificación de duplicados")
        #     os.environ["DEMO_MODE"] = "true"
        # else:
        #     os.environ.pop("DEMO_MODE", None)
        #
        # return demo_mode
    
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
        """Renderizar estadísticas de sesión - DESHABILITADO EN PRODUCCIÓN"""
        # Sección removida para mantener el sidebar limpio y profesional
        # Las estadísticas se muestran en cada pestaña cuando son relevantes
        pass
    
    def _render_file_upload_tab(self, sidebar_config: Dict[str, Any]):
        """Renderizar pestaña de carga de archivos"""
        st.markdown("## 📁 Carga de Archivos Bancarios")

        # Mostrar mensajes de procesamiento previo si existen
        if "processing_summary" in st.session_state:
            summary = st.session_state["processing_summary"]

            if summary["successful_count"] > 0:
                st.success(f"✅ {summary['successful_count']} archivo(s) procesado(s) exitosamente")

            if summary["skipped_count"] > 0:
                st.warning(f"⚠️ {summary['skipped_count']} archivo(s) ya fueron importados anteriormente")
                with st.expander("📋 Ver archivos duplicados", expanded=True):
                    for s in summary["skipped_files"]:
                        st.info(f"📄 **{s['file_name']}**\n\n{s['message']}")

            # Limpiar el mensaje después de mostrarlo
            del st.session_state["processing_summary"]

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
                # LIMPIAR caché de resultados anteriores
                if "processing_results" in st.session_state:
                    del st.session_state["processing_results"]
                if "processing_summary" in st.session_state:
                    del st.session_state["processing_summary"]

                # Contenedor de progreso
                progress_container = st.empty()
                status_container = st.empty()

                try:
                    # Solo usar demo_mode del sidebar (validación SIEMPRE activa)
                    effective_demo_mode = sidebar_config["demo_mode"]

                    # Mostrar inicio del proceso
                    progress_container.info(f"🔄 Iniciando análisis de {len(uploaded_files)} archivo(s)...")

                    # PASO 1: Conectar a Google Sheets SIEMPRE (excepto en demo_mode real)
                    if not effective_demo_mode and sidebar_config["sheet_id"] != "TU_SHEET_ID":
                        status_container.info("📡 Conectando a Google Sheets para verificar duplicados...")

                    results = self.processor.process_files(
                        uploaded_files,
                        sidebar_config["sheet_id"],
                        sidebar_config["sheet_tab"],
                        effective_demo_mode  # Solo demo_mode real, NO force_reimport
                    )

                    if results:
                        # Separar archivos exitosos vs saltados
                        successful = [r for r in results if r.get("status") != "skipped_duplicate"]
                        skipped = [r for r in results if r.get("status") == "skipped_duplicate"]

                        # Mostrar resumen del análisis
                        progress_container.success(f"✅ Análisis completado: {len(successful)} procesado(s), {len(skipped)} duplicado(s)")

                        st.session_state["processing_results"] = results

                        # Guardar mensajes en session_state para mostrar después del rerun
                        st.session_state["processing_summary"] = {
                            "successful_count": len(successful),
                            "skipped_count": len(skipped),
                            "skipped_files": skipped
                        }

                        st.session_state.app_state["current_step"] = 1
                        st.rerun()
                    else:
                        # Todos los archivos fueron duplicados o hubo errores
                        progress_container.warning("⚠️ No se pudieron procesar los archivos")
                        status_container.info("💡 **Posibles razones:**\n"
                               "- Los archivos ya fueron importados anteriormente\n"
                               "- No contienen datos válidos\n"
                               "- Activa el **Modo Demo** en el sidebar o el checkbox '🔄 Permitir reimportar'")
                except Exception as e:
                    progress_container.error(f"❌ Error procesando archivos: {e}")
                    logger.error(f"Error en procesamiento: {e}", exc_info=True)
        
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

        # Todos los archivos se procesan (no hay "skipped" por hash)
        successful = results

        if not successful:
            st.warning("⚠️ No se pudieron procesar los archivos. Verifica que sean archivos válidos.")
            return

        # ============ SECCIÓN DE ORGANIZACIÓN DE DATOS ============
        st.markdown("---")
        st.markdown("### 🔄 Organización de Datos")

        col_sort1, col_sort2 = st.columns([2, 1])

        with col_sort1:
            st.markdown("**Ordenar datos cronológicamente (más reciente → más antiguo):**")
            st.caption("📅 Los datos se insertarán en orden cronológico descendente")

        with col_sort2:
            # Botón para organizar datos (SIEMPRE descendente)
            if st.button("🔄 Organizar Datos", type="secondary", use_container_width=True, key="btn_organizar"):
                progress_placeholder = st.empty()

                try:
                    progress_placeholder.info("🔄 Organizando datos por fecha y hora...")

                    # Organizar cada resultado (SIEMPRE descendente: más reciente primero)
                    for result in successful:
                        if not result["new_data"].empty:
                            # Ordenar datos nuevos (ascending=False = más reciente primero)
                            result["new_data"] = self.processor.sort_data_by_datetime(
                                result["new_data"],
                                ascending=False
                            )

                            # Ordenar datos raw también
                            result["raw_data"] = self.processor.sort_data_by_datetime(
                                result["raw_data"],
                                ascending=False
                            )

                    # Actualizar estado
                    st.session_state["processing_results"] = successful
                    st.session_state.app_state["data_sorted"] = True
                    st.session_state.app_state["sort_order"] = "desc"

                    # Mostrar éxito de forma más suave
                    progress_placeholder.success("✅ Datos organizados correctamente (más reciente → más antiguo)")
                    time.sleep(0.8)  # Pausa breve para mejor UX
                    progress_placeholder.empty()
                    st.rerun()

                except Exception as e:
                    progress_placeholder.error(f"❌ Error organizando datos: {e}")
                    logger.error(f"Error en organización de datos: {e}", exc_info=True)

        # Mostrar estado de organización
        if st.session_state.app_state.get("data_sorted", False):
            st.success("✅ Datos organizados cronológicamente (más reciente → más antiguo)")

            # Mostrar rango de fechas
            try:
                all_dates = []
                for result in successful:
                    if not result["new_data"].empty and "Fecha" in result["new_data"].columns:
                        all_dates.extend(result["new_data"]["Fecha"].dropna().tolist())

                if all_dates:
                    fecha_min = min(all_dates)
                    fecha_max = max(all_dates)
                    st.info(f"📅 Rango de fechas procesadas: **{fecha_max}** (más reciente) → **{fecha_min}** (más antiguo)")
            except Exception as e:
                logger.warning(f"Error mostrando rango de fechas: {e}")
        else:
            st.warning("⚠️ Datos NO organizados. Presiona el botón '🔄 Organizar Datos' para ordenarlos antes de insertar.")

        st.markdown("---")
        # ============ FIN SECCIÓN DE ORGANIZACIÓN ============

        for result in successful:
            num_registros = len(result['new_data']) if not result['new_data'].empty else 0
            num_duplicados = len(result.get('duplicates', []))

            st.markdown(f"### 📄 {result['file_name']}")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Leídos", result["stats"]["FilasLeídas"])
                st.metric("Duplicados", num_duplicados, delta="Saltados", delta_color="inverse")

            with col2:
                st.metric("Nuevos", result["stats"]["NuevosInsertados"], delta="Para insertar", delta_color="normal")
                st.metric("Conflictos", result["stats"]["Conflictivos"])

            # Mostrar duplicados si existen
            if num_duplicados > 0:
                with st.expander(f"⚠️ Ver {num_duplicados} registros duplicados (NO se insertarán)", expanded=False):
                    st.warning(f"Estos {num_duplicados} registros ya existen en Google Sheets y NO serán insertados")

                    for idx, dup in enumerate(result['duplicates'][:20], 1):  # Mostrar máximo 20
                        with st.container():
                            col_a, col_b = st.columns([1, 3])

                            with col_a:
                                st.markdown(f"**#{idx}**")
                                st.caption(f"Recibo: `{dup.get('recibo', 'N/A')}`")

                            with col_b:
                                st.markdown(f"**Descripción:**")
                                st.caption(dup.get('descripcion', 'N/A')[:200])

                            st.markdown("---")

                    if num_duplicados > 20:
                        st.info(f"Mostrando 20 de {num_duplicados} duplicados. Los demás también serán omitidos.")

            # Mostrar vista previa de datos nuevos (ahora ordenados si se aplicó)
            if not result["new_data"].empty:
                preview_title = "✅ Vista previa de datos NUEVOS que se insertarán"
                if st.session_state.app_state.get("data_sorted", False):
                    preview_title += " 🔽 (ordenados cronológicamente)"

                with st.expander(preview_title, expanded=False):
                    st.markdown("**📋 Primeros 10 registros:**")

                    # IMPORTANTE: Explicar qué datos se muestran
                    st.info("**🔑 Clave** = Número de Recibo que se usará para validar duplicados\n\n"
                           "**📅 Fecha + ⏰ Hora** = Datos organizados cronológicamente")

                    # Crear DataFrame de vista previa con formato personalizado
                    preview_data = result["new_data"].head(10).copy()

                    # Seleccionar y ordenar columnas para mejor visualización
                    display_cols = []
                    col_mapping = {}

                    # Detectar columna de FECHA (puede tener nombres raros por el formato Acumulado)
                    fecha_col = None
                    for col in preview_data.columns:
                        if "Fecha" in col or col == "2025-07-17T18:32:23.744Z":
                            fecha_col = col
                            break

                    if fecha_col:
                        display_cols.append(fecha_col)
                        col_mapping[fecha_col] = "📅 Fecha"

                    # HORA
                    if "Hora" in preview_data.columns:
                        display_cols.append("Hora")
                        col_mapping["Hora"] = "⏰ Hora"

                    # CLAVE (identificador único - puede ser Recibo o Clave)
                    clave_col = None
                    if "Clave" in preview_data.columns:
                        clave_col = "Clave"
                    elif "Recibo" in preview_data.columns:
                        clave_col = "Recibo"

                    if clave_col:
                        display_cols.append(clave_col)
                        col_mapping[clave_col] = "🔑 Clave (ID único)"

                    # DESCRIPCIÓN (truncada para legibilidad)
                    if "Descripción" in preview_data.columns:
                        display_cols.append("Descripción")
                        col_mapping["Descripción"] = "📝 Descripción"

                        # Truncar descripciones largas
                        preview_data["Descripción"] = preview_data["Descripción"].apply(
                            lambda x: str(x)[:80] + "..." if pd.notna(x) and len(str(x)) > 80 else str(x)
                        )

                    # MONTOS
                    if "Egreso" in preview_data.columns:
                        display_cols.append("Egreso")
                        col_mapping["Egreso"] = "💸 Egreso"
                    elif "Cargo" in preview_data.columns:
                        display_cols.append("Cargo")
                        col_mapping["Cargo"] = "💸 Cargo"

                    if "Ingreso" in preview_data.columns:
                        display_cols.append("Ingreso")
                        col_mapping["Ingreso"] = "💰 Ingreso"
                    elif "Abono" in preview_data.columns:
                        display_cols.append("Abono")
                        col_mapping["Abono"] = "💰 Abono"

                    # Filtrar solo columnas disponibles
                    display_cols = [col for col in display_cols if col in preview_data.columns]

                    if display_cols:
                        preview_display = preview_data[display_cols].rename(columns=col_mapping)

                        # Configurar opciones de visualización
                        st.dataframe(
                            preview_display,
                            use_container_width=True,
                            hide_index=True,
                            height=450,
                            column_config={
                                "📅 Fecha": st.column_config.TextColumn(
                                    "📅 Fecha",
                                    help="Fecha del movimiento",
                                    width="medium"
                                ),
                                "⏰ Hora": st.column_config.TextColumn(
                                    "⏰ Hora",
                                    help="Hora del movimiento",
                                    width="small"
                                ),
                                "🔑 Clave (ID único)": st.column_config.TextColumn(
                                    "🔑 Clave",
                                    help="Número de recibo usado para validar duplicados",
                                    width="medium"
                                ),
                                "📝 Descripción": st.column_config.TextColumn(
                                    "📝 Descripción",
                                    help="Descripción completa del movimiento (truncada en vista previa)",
                                    width="large"
                                ),
                            }
                        )

                        st.caption(f"📊 Mostrando 10 de {len(result['new_data'])} registros nuevos")
                        st.caption("💡 La descripción está truncada a 80 caracteres. Los datos completos se insertarán en Google Sheets.")
                    else:
                        st.warning("No hay columnas para mostrar")
            else:
                st.info("✅ No hay registros nuevos en este archivo (todos son duplicados)")

            st.markdown("---")

        # Botón para proceder a inserción (solo contar archivos exitosos)
        total_new = sum([len(r["new_data"]) for r in successful if not r["new_data"].empty])
        if total_new > 0:
            st.markdown("---")

            # Validar si los datos están ordenados
            if not st.session_state.app_state.get("data_sorted", False):
                st.warning("⚠️ **Recomendación:** Organiza los datos antes de proceder a la inserción")

            # Información de datos listos
            col_info1, col_info2 = st.columns([2, 1])

            with col_info1:
                st.success(f"✅ **{total_new} registros** listos para insertar en Google Sheets")
                if st.session_state.app_state.get("data_sorted", False):
                    st.info("📋 Datos organizados cronológicamente (más reciente → más antiguo)")

            with col_info2:
                st.markdown("")  # Espaciado
                st.markdown("### ➡️ Siguiente paso:")
                st.info("**Haz clic en la pestaña:**\n\n📊 **Insertar a Sheets**")

            # Botón informativo que prepara el estado
            if st.button(f"✓ Confirmar y Preparar Inserción",
                       type="primary", use_container_width=True, key="btn_preparar_insercion"):
                st.session_state.app_state["ready_for_insertion"] = True
                st.balloons()
                st.success("🎉 ¡Datos confirmados! Ahora ve a la pestaña **'📊 Insertar a Sheets'** para completar la inserción.")
                st.info("👆 Haz clic en la pestaña **'📊 Insertar a Sheets'** arriba para continuar")
    
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

            # Contenedores de progreso
            progress_bar = st.progress(0)
            status_text = st.empty()
            detail_text = st.empty()

            try:
                import time

                if self.sheets_service:
                    # PASO 1: Preparando datos
                    status_text.info("📦 Paso 1/4: Preparando datos para inserción...")
                    detail_text.text(f"Preparando {total_new} registros de {len([r for r in results if r.get('status') != 'skipped_duplicate'])} archivo(s)")
                    progress_bar.progress(25)
                    time.sleep(0.5)

                    # PASO 2: Conectando a Google Sheets
                    status_text.info("📡 Paso 2/4: Conectando a Google Sheets...")
                    detail_text.text(f"Destino: {sidebar_config['sheet_tab']}")
                    progress_bar.progress(40)
                    time.sleep(0.5)

                    # PASO 3: Buscando ubicación correcta
                    status_text.info("🔍 Paso 3/4: Analizando columna A para encontrar primera fila vacía...")
                    detail_text.text("Esto garantiza que no se sobrescriban datos existentes")
                    progress_bar.progress(60)
                    time.sleep(0.5)

                    # PASO 4: Insertando registros
                    status_text.info(f"📝 Paso 4/4: Insertando {total_new} registros...")
                    detail_text.text("⏳ Este proceso puede tardar varios segundos... Por favor espera")
                    progress_bar.progress(80)

                    # Ejecutar inserción
                    insertion_result = self.sheets_service.insert_results(results, sidebar_config["sheet_tab"])

                    # COMPLETADO
                    progress_bar.progress(100)
                    status_text.success("✅ Inserción completada exitosamente")

                    # Mostrar resumen de inserción
                    st.markdown("---")
                    st.markdown("### 📊 Resumen de Inserción:")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("✅ Registros Insertados", insertion_result.get("inserted", 0), delta="Nuevos")
                    with col2:
                        st.metric("⚠️ Duplicados Saltados", insertion_result.get("duplicates", 0), delta="Ya existían")
                    with col3:
                        st.metric("❌ Errores", insertion_result.get("errors", 0))

                    # Mostrar detalles de duplicados si los hay
                    if insertion_result.get("skipped_duplicates"):
                        st.markdown("---")
                        st.warning(f"⚠️ Se saltaron {len(insertion_result['skipped_duplicates'])} registros duplicados")

                        with st.expander("📋 Ver TODOS los datos de registros NO insertados", expanded=True):
                            st.markdown("### 🔍 Registros duplicados - Información completa para verificación")
                            st.info("💡 Puedes buscar estos datos en el TXT y en Google Sheets para confirmar que ya existen")

                            for idx, dup in enumerate(insertion_result["skipped_duplicates"], 1):
                                with st.container():
                                    st.markdown(f"#### ❌ Registro #{idx} - NO INSERTADO")

                                    col1, col2 = st.columns(2)

                                    with col1:
                                        st.markdown("**📄 Información del registro:**")
                                        st.code(f"""
Recibo/Clave: {dup.get('recibo', 'N/A')}

Descripción completa:
{dup.get('descripcion', 'N/A')}
                                        """)

                                    with col2:
                                        st.markdown("**⚠️ Razón:**")
                                        st.error(dup.get('reason', 'Duplicado'))

                                        st.markdown("**🔍 Cómo verificar:**")
                                        st.markdown(f"""
1. **En el TXT:** Busca el recibo `{dup.get('recibo', 'N/A')}`
2. **En Google Sheets:** Busca en columna F (Clave) el valor `{dup.get('recibo', 'N/A')}`
3. Confirma que la descripción coincide
                                        """)

                                    st.markdown("---")

                    # Limpiar session state de resultados procesados
                    st.session_state.pop("processing_results", None)
                    st.session_state.pop("processing_summary", None)

                    st.balloons()

                    # Mostrar link a Google Sheets
                    st.markdown("---")
                    st.markdown(f"### 🔗 Verifica tus datos:")
                    st.markdown(f"[Abrir Google Sheets](https://docs.google.com/spreadsheets/d/{sidebar_config['sheet_id']}/edit)")
                else:
                    status_text.warning("⚠️ Modo demo - No se realizó inserción real")
                    detail_text.info("Configura Google Sheets en el sidebar para inserción real")

            except Exception as e:
                progress_bar.empty()
                status_text.error(f"❌ Error durante la inserción: {e}")
                detail_text.error("Revisa los logs o intenta nuevamente")
                logger.error(f"Error en inserción: {e}", exc_info=True)
    
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

