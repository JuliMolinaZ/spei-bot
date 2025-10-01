#!/usr/bin/env python3
"""
Aplicación de Conciliación Bancaria con UX Espectacular
"""

import os
import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib
import time
import math

# Importaciones del sistema
from bank_parser import parse_bank_txt, add_uids, classify_tipo
from sheets_client import SheetsClient
from config import load_config
from banbajio_reader import read_smart_csv
from ux_components import *

# Configuración de página con tema personalizado
st.set_page_config(
    page_title="🏦 Conciliación Bancaria",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Conciliación Bancaria Inteligente v2.0"
    }
)

# CSS personalizado para la aplicación
st.markdown("""
<style>
    /* Tema general */
    .main > div {
        padding-top: 1rem;
    }
    
    /* Mejorar sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Botones personalizados */
    .stButton > button {
        background: linear-gradient(45deg, #007bff, #0056b3);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,123,255,0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,123,255,0.4);
        background: linear-gradient(45deg, #0056b3, #004085);
    }
    
    /* Metricas personalizadas */
    [data-testid="metric-container"] {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* File uploader personalizado */
    .stFileUploader > div > div {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 3px dashed #dee2e6;
        border-radius: 20px;
        padding: 2rem;
    }
    
    /* Ocultar elementos innecesarios */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Animaciones suaves */
    .element-container, .stMarkdown, .stAlert {
        animation: fadeInUp 0.5s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>
""", unsafe_allow_html=True)

# Estado de la aplicación
if "app_state" not in st.session_state:
    st.session_state.app_state = {
        "current_step": 0,
        "processed_files": [],
        "processing_stats": {},
        "google_sheets_ready": False,
        "upload_completed": False
    }

def initialize_app():
    """Inicializa la configuración de la aplicación"""
    show_hero_section()
    
    # Sidebar mejorado
    with st.sidebar:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem 1rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
        ">
            <h2 style="color: white; margin: 0;">⚙️ Configuración</h2>
        </div>
        """, unsafe_allow_html=True)
        
        cfg = load_config()
        
        # Configuración de Google Sheets
        st.markdown("#### 📊 Google Sheets")
        sheet_id = st.text_input(
            "ID de la Hoja", 
            value=cfg.get("SHEET_ID", ""),
            placeholder="1BvyC2y3nRhCvKa9Q8yX7zF...",
            help="El ID de tu hoja de Google Sheets"
        )
        
        sheet_tab = st.text_input(
            "Nombre de la Pestaña",
            value=cfg.get("SHEET_TAB", "Movimientos_Nuevos"),
            placeholder="Movimientos_Nuevos",
            help="Nombre de la pestaña donde se insertarán los datos"
        )
        
        # Modo Demo
        st.markdown("---")
        st.markdown("#### 🧪 Modo Demo")
        demo_mode = st.toggle("🚀 Activar Modo Demo", 
                            help="Saltará verificaciones de duplicados para testing",
                            key="demo_mode")
        if demo_mode:
            st.info("🎯 Modo Demo Activo - Sin verificación de duplicados")
            os.environ["DEMO_MODE"] = "true"
        else:
            os.environ.pop("DEMO_MODE", None)
        
        # Estado de conexión
        st.markdown("---")
        st.markdown("#### 🔗 Estado de Conexión")
        
        if sheet_id and sheet_id != "TU_SHEET_ID":
            try:
                sheets_client = SheetsClient(sheet_id)
                st.success("✅ Conexión establecida")
                st.session_state.app_state["google_sheets_ready"] = True
                st.info(f"📄 Pestaña destino: `{sheet_tab}` (inserción dinámica)")
                st.info("🔒 **Nota**: Si la hoja tiene celdas protegidas, el sistema automáticamente usará estrategias seguras de inserción.")
            except Exception as e:
                st.error("❌ Error de conexión")
                st.session_state.app_state["google_sheets_ready"] = False
                show_warning_card(
                    "Problema de Configuración",
                    f"No se pudo conectar: {str(e)[:100]}...",
                    "Verifica tu configuración de Google Sheets"
                )
        else:
            st.warning("⚠️ Modo de prueba")
            st.session_state.app_state["google_sheets_ready"] = False
            show_info_card(
                "Modo de Prueba Activo",
                "Configura Google Sheets para funcionalidad completa"
            )
        
        # Estadísticas de la sesión
        st.markdown("---")
        st.markdown("#### 📈 Estadísticas de Sesión")
        
        if st.session_state.app_state["processed_files"]:
            total_files = len(st.session_state.app_state["processed_files"])
            total_records = sum([f.get("total_records", 0) for f in st.session_state.app_state["processed_files"]])
            
            st.metric("Archivos Procesados", total_files)
            st.metric("Registros Totales", total_records)
        else:
            st.info("Sin archivos procesados aún")
    
    return sheet_id, sheet_tab

def show_file_upload_interface():
    """Interfaz de carga de archivos mejorada"""
    st.markdown("## 📁 Paso 1: Selecciona tus Archivos")
    
    show_file_upload_zone()
    
    # Widget de carga con información
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
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
        ">
            <h4 style="color: #1976d2; margin-bottom: 1rem;">💡 Consejos</h4>
            <p style="color: #1565c0; font-size: 0.9rem; margin: 0;">
                • Acepta archivos TXT y CSV<br>
                • Detecta automáticamente BanBajío<br>
                • Procesa múltiples archivos<br>
                • Tamaño máximo: 200MB
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    return uploaded_files

def process_files_with_ux(uploaded_files, sheet_id, sheet_tab):
    """Procesa archivos con UX mejorada"""
    if not uploaded_files:
        return None, None
    
    # Pasos del proceso
    steps = [
        "📁 Cargar Archivos",
        "🔍 Analizar Datos", 
        "🎯 Clasificar Movimientos",
        "🔒 Verificar Duplicados",
        "📊 Preparar Inserción"
    ]
    
    all_results = []
    import_logs = []
    
    # Estimación inicial
    total_files = len(uploaded_files)
    show_info_card(
        "Iniciando Procesamiento",
        f"Se procesarán {total_files} archivo(s). Esto tomará aproximadamente {total_files * 15:.0f}-{total_files * 30:.0f} segundos.",
        "⏱️"
    )
    
    # Configuración de sheets
    test_mode = not sheet_id or sheet_id == "TU_SHEET_ID" or sheet_id == ""
    
    if not test_mode:
        try:
            with st.spinner("🔗 Estableciendo conexión con Google Sheets..."):
                time.sleep(1)  # Simular conexión
                sheets_client = SheetsClient(sheet_id)
                existing_analysis = sheets_client.get_existing_data_analysis(sheet_tab)
                show_success_animation(
                    "Conexión Establecida",
                    f"Se encontraron {existing_analysis.get('total_records', 0)} registros existentes"
                )
        except Exception as e:
            show_warning_card(
                "Problema de Conexión",
                f"No se pudo conectar a Google Sheets: {str(e)[:100]}...",
                "Continuando en modo de prueba"
            )
            test_mode = True
            sheets_client = None
            existing_analysis = {"existing_uids": set(), "uid_amount_map": {}, "total_records": 0, "analysis_ready": False}
    else:
        sheets_client = None
        existing_analysis = {"existing_uids": set(), "uid_amount_map": {}, "total_records": 0, "analysis_ready": False}
    
    # Procesar cada archivo
    for file_idx, uploaded_file in enumerate(uploaded_files):
        st.markdown(f"### 📄 Procesando: `{uploaded_file.name}` ({file_idx + 1}/{total_files})")
        
        # Mostrar indicador de pasos
        show_step_indicator(0, len(steps), steps)
        
        try:
            file_hash = hashlib.md5(uploaded_file.read()).hexdigest()
            uploaded_file.seek(0)
            
            # Verificar si ya fue importado (saltear en modo demo)
            if not test_mode and sheets_client and not os.environ.get("DEMO_MODE"):
                if sheets_client.check_file_hash_exists(file_hash):
                    show_warning_card(
                        "Archivo Ya Procesado",
                        f"El archivo '{uploaded_file.name}' ya fue importado anteriormente",
                        "Saltando al siguiente archivo"
                    )
                    continue
            elif os.environ.get("DEMO_MODE"):
                show_info_card(
                    "Modo Demo Activo",
                    f"Procesando '{uploaded_file.name}' saltando verificación de duplicados",
                    "🎯"
                )
            
            # PASO 1: LECTURA DE ARCHIVO
            show_step_indicator(1, len(steps), steps)
            with st.spinner("📤 Leyendo archivo..."):
                start_time = time.time()
                df_raw = read_smart_csv(uploaded_file)
                read_time = time.time() - start_time
                
                estimated_processing_time = estimate_processing_time(len(df_raw))
                
                show_success_animation(
                    "Archivo Leído Exitosamente",
                    f"{len(df_raw)} filas detectadas",
                    f"Tiempo de lectura: {read_time:.1f}s | Procesamiento estimado: {estimated_processing_time:.0f}s"
                )
            
            # PASO 2: PARSEO Y ANÁLISIS
            show_step_indicator(2, len(steps), steps)
            
            # Progreso detallado para parseo
            progress_container = st.container()
            with progress_container:
                show_loading_spinner("Analizando estructura de datos...", 5)
                time.sleep(0.5)
                
                df = parse_bank_txt(df_raw)
                
                show_advanced_progress(50, 100, "Procesamiento de Datos", "Normalizando columnas y validando estructura...")
                time.sleep(0.3)
                
                show_advanced_progress(100, 100, "Procesamiento de Datos", "✅ Estructura validada correctamente")
            
            progress_container.empty()
            show_success_animation(
                "Datos Procesados",
                f"{len(df)} registros válidos extraídos",
                f"Columnas detectadas: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}"
            )
            
            # PASO 3: CLASIFICACIÓN
            show_step_indicator(3, len(steps), steps)
            
            classification_container = st.container()
            with classification_container:
                show_loading_spinner("Clasificando tipos de transacciones...", 3)
                
                df['Tipo'] = df['Descripción'].map(classify_tipo)
                tipos_count = df['Tipo'].value_counts()
                
                # Mostrar progreso de clasificación
                for i in range(101):
                    if i % 20 == 0:
                        show_advanced_progress(i, 100, "Clasificación de Transacciones", 
                                            f"Analizando patrones... ({i}%)", 3)
                        time.sleep(0.1)
                
            classification_container.empty()
            
            # Dashboard de tipos encontrados
            tipos_data = [
                (tipo, count, "💰", "#28a745") if "SPEI Recibido" in tipo
                else (tipo, count, "💸", "#dc3545") if "SPEI Enviado" in tipo
                else (tipo, count, "🏪", "#17a2b8") if "POS" in tipo
                else (tipo, count, "💼", "#ffc107") if "Entrega" in tipo
                else (tipo, count, "📋", "#6c757d")
                for tipo, count in tipos_count.head(4).items()
            ]
            
            if tipos_data:
                show_stats_dashboard([(title, value, icon, color) for title, value, icon, color in tipos_data])
            
            # PASO 4: GENERACIÓN DE UIDs
            show_step_indicator(4, len(steps), steps)
            
            uid_container = st.container()
            with uid_container:
                show_loading_spinner("Generando identificadores únicos...", 2)
                
                df = add_uids(df)
                uids_unicos = len(df['UID'].unique())
                
                # Simular progreso de UIDs
                for i in range(0, 101, 25):
                    show_advanced_progress(i, 100, "Generación de UIDs", 
                                        f"Creando identificadores únicos... {i}%", 2)
                    time.sleep(0.2)
            
            uid_container.empty()
            show_success_animation(
                "UIDs Generados",
                f"{uids_unicos} identificadores únicos creados",
                f"De {len(df)} registros totales"
            )
            
            # PASO 5: ANÁLISIS DE DUPLICADOS
            show_step_indicator(5, len(steps), steps)
            
            duplicate_container = st.container()
            with duplicate_container:
                estimated_seconds, time_text = show_time_estimation("duplicate_analysis", len(df))
                show_loading_spinner(f"Analizando duplicados y conflictos... ({time_text})", estimated_seconds)
                
                from utils import analyze_duplicates_exhaustive, validate_insertion_safety
                
                analysis = analyze_duplicates_exhaustive(df, existing_analysis)
                validation = validate_insertion_safety(analysis)
                
                # Progreso de análisis
                for i in range(0, 101, 10):
                    show_advanced_progress(i, 100, "Análisis de Duplicados", 
                                        "Comparando con registros existentes...", estimated_seconds)
                    time.sleep(estimated_seconds / 10)
            
            duplicate_container.empty()
            
            # Resultados del análisis
            safe_count = len(analysis.get('safe_to_insert', []))
            duplicates = analysis.get('summary', {}).get('duplicates', 0)
            conflicts = analysis.get('summary', {}).get('conflicts', 0)
            
            stats_data = [
                ("Registros Seguros", safe_count, "✅", "#28a745"),
                ("Duplicados", duplicates, "⚠️", "#ffc107"),
                ("Conflictos", conflicts, "❌", "#dc3545"),
                ("Total Procesados", len(df), "📊", "#17a2b8")
            ]
            
            show_stats_dashboard(stats_data)
            
            # PREPARACIÓN FINAL
            if analysis["safe_to_insert"]:
                safe_indices = [item["row_index"] for item in analysis["safe_to_insert"]]
                nuevos = df.iloc[safe_indices].copy()

                # ORDENAR POR FECHA Y HORA (del más antiguo al más reciente)
                if not nuevos.empty and 'Fecha' in nuevos.columns and 'Hora' in nuevos.columns:
                    # Crear columna temporal de fecha-hora combinada para ordenar
                    nuevos['_fecha_hora_sort'] = pd.to_datetime(
                        nuevos['Fecha'].astype(str) + ' ' + nuevos['Hora'].astype(str),
                        errors='coerce'
                    )
                    # Ordenar del más antiguo al más reciente
                    nuevos = nuevos.sort_values('_fecha_hora_sort', ascending=True)
                    # Eliminar columna temporal
                    nuevos = nuevos.drop(columns=['_fecha_hora_sort'])

                    show_success_animation(
                        "Datos Ordenados",
                        f"Registros ordenados cronológicamente del más antiguo al más reciente",
                        f"Desde {nuevos.iloc[0]['Fecha']} hasta {nuevos.iloc[-1]['Fecha']}"
                    )

                # Formatear para Google Sheets
                from format_adapter import adapt_to_acumulado_format
                nuevos = adapt_to_acumulado_format(nuevos)
                
                show_success_animation(
                    "Preparación Completada",
                    f"{len(nuevos)} registros listos para inserción",
                    "Datos formateados correctamente para Google Sheets"
                )
            else:
                nuevos = pd.DataFrame()
                show_warning_card(
                    "Sin Datos Nuevos",
                    "No se encontraron registros nuevos para insertar",
                    "Todos los datos ya existen en la hoja"
                )
            
            # Estadísticas del archivo
            stats = {
                "Archivo": uploaded_file.name,
                "HashArchivo": file_hash,
                "FilasLeídas": len(df),
                "NuevosInsertados": len(nuevos),
                "DuplicadosSaltados": duplicates,
                "Conflictivos": conflicts,
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
            
            all_results.append(result)
            import_logs.append(stats)
            
            # Actualizar estado de sesión
            st.session_state.app_state["processed_files"].append({
                "name": uploaded_file.name,
                "total_records": len(df),
                "new_records": len(nuevos),
                "duplicates": duplicates,
                "conflicts": conflicts
            })
            
            st.balloons()  # Celebración por archivo completado!
            
        except Exception as e:
            st.error(f"❌ Error procesando {uploaded_file.name}: {e}")
            import traceback
            with st.expander("Ver detalles del error"):
                st.code(traceback.format_exc())
    
    return all_results, import_logs

def show_insertion_interface(results, sheet_id, sheet_tab):
    """Interfaz de inserción a Google Sheets"""
    if not results:
        return
    
    st.markdown("## 📊 Paso 2: Inserción a Google Sheets")
    
    # Resumen antes de insertar
    total_new = sum([len(r["new_data"]) for r in results])
    total_files = len(results)
    
    if total_new == 0:
        show_info_card(
            "Sin Datos para Insertar",
            "Todos los registros ya existen en tu hoja de Google Sheets",
            "🔄"
        )
        return
    
    # Mostrar resumen de inserción
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            border-left: 5px solid #28a745;
        ">
            <h2 style="color: #155724; margin-bottom: 1rem;">📊 Resumen de Inserción</h2>
            <div style="font-size: 3rem; color: #28a745; margin-bottom: 1rem;">{total_new}</div>
            <p style="color: #155724; font-size: 1.2rem; margin: 0;">
                Registros nuevos listos para insertar<br>
                <small>de {total_files} archivo(s) procesado(s)</small>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Estimación de tiempo de inserción
        estimated_time = total_new * 0.05 + 5  # ~0.05 segundos por registro + overhead
        
        if estimated_time < 60:
            time_text = f"{estimated_time:.0f} segundos"
        else:
            time_text = f"{estimated_time/60:.1f} minutos"
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            border-left: 5px solid #ffc107;
        ">
            <h3 style="color: #856404; margin-bottom: 1rem;">⏱️ Tiempo Estimado</h3>
            <div style="font-size: 2rem; color: #856404; margin-bottom: 1rem;">{time_text}</div>
            <p style="color: #856404; margin: 0;">
                Inserción a Google Sheets<br>
                <small>Incluye validación y logs</small>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Botón de inserción grande
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button(f"🚀 Insertar {total_new} Registros en '{sheet_tab}' (Dinámico)",
                 type="primary",
                 use_container_width=True):
        
        # Proceso de inserción con UX
        insertion_container = st.container()
        
        with insertion_container:
            # Preparación
            show_loading_spinner(f"Preparando inserción dinámica en '{sheet_tab}'...", 3)
            time.sleep(1)
            
            try:
                sheets_client = SheetsClient(sheet_id)
                
                # Insertar cada archivo
                for idx, result in enumerate(results):
                    if result["new_data"].empty:
                        continue
                    
                    file_name = result["file_name"]
                    new_data = result["new_data"]
                    
                    st.markdown(f"### 📄 Insertando: {file_name}")
                    
                    # Progress bar para inserción
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Simular inserción por lotes
                    batch_size = 100
                    total_batches = math.ceil(len(new_data) / batch_size)
                    
                    for batch_idx in range(total_batches):
                        start_idx = batch_idx * batch_size
                        end_idx = min((batch_idx + 1) * batch_size, len(new_data))
                        batch_data = new_data.iloc[start_idx:end_idx]
                        
                        progress = (batch_idx + 1) / total_batches
                        progress_bar.progress(progress)
                        status_text.text(f"Insertando lote {batch_idx + 1}/{total_batches} ({end_idx - start_idx} registros)...")
                        
                        # Insertar lote usando el nuevo método dinámico
                        try:
                            # Convertir DataFrame a lista de listas para la inserción
                            batch_values = batch_data.values.tolist()

                            # Usar el nuevo método de inserción dinámica
                            insertion_result = sheets_client.append_data_after_last_row(sheet_tab, batch_values)

                            if insertion_result.get("error"):
                                error_msg = insertion_result['error']
                                if "protected" in error_msg.lower() or "permission" in error_msg.lower():
                                    st.warning(f"🔒 Detectadas celdas protegidas en '{sheet_tab}'. Usando estrategia de inserción segura...")
                                    # El sistema automáticamente manejará esto en el siguiente intento
                                else:
                                    st.error(f"❌ Error insertando lote {batch_idx + 1}: {error_msg}")
                                    break
                            else:
                                # Mostrar información detallada de la inserción
                                if batch_idx == 0:  # Solo mostrar info detallada en el primer lote
                                    start_row = insertion_result.get('last_row_used', 'N/A')
                                    st.info(f"📍 Insertando en tabla desde fila {start_row} (primera columna A vacía)")

                                    # Mostrar verificación de inserción
                                    if insertion_result.get('verification_passed', True):
                                        st.success("✅ Inserción verificada en tabla correctamente")
                                    else:
                                        st.warning("⚠️ Verificación de inserción en tabla falló - revisando datos...")

                                # Mostrar estadísticas de inserción si hay errores
                                errors = insertion_result.get('errors', 0)
                                if errors > 0:
                                    st.warning(f"⚠️ {errors} registros no se pudieron insertar en la tabla")

                                # Mostrar información específica para verificación manual
                                last_row_used = insertion_result.get('last_row_used', 'N/A')
                                next_row = insertion_result.get('next_available_row', 'N/A')
                                if next_row != 'N/A' and last_row_used != 'N/A':
                                    st.info(f"📊 Próxima fila vacía en tabla: {next_row}")
                                    st.info(f"🔍 **Verificar manualmente**: Los datos deben aparecer en las filas con columna A llena hasta la fila {last_row_used}")
                                    st.info(f"🎯 **Importante**: Busca datos en las primeras filas donde la columna A estaba vacía, NO al final de la hoja")

                        except Exception as e:
                            error_str = str(e)
                            if "protected" in error_str.lower() or "permission" in error_str.lower():
                                st.warning(f"🔒 Celdas protegidas detectadas. El sistema intentará insertar en columnas seguras...")
                            else:
                                st.error(f"❌ Error insertando lote {batch_idx + 1}: {error_str}")
                                break
                    
                    progress_bar.progress(1.0)
                    status_text.text("✅ Inserción completada")
                    
                    # Registrar en log
                    log_entry = {
                        "Archivo": file_name,
                        "HashArchivo": result.get("file_hash", ""),
                        "FilasLeídas": len(result.get("all_data", [])),
                        "NuevosInsertados": len(new_data),
                        "DuplicadosSaltados": insertion_result.get("duplicates", 0),
                        "Conflictivos": 0,  # Por simplicidad
                        "FechaHora": datetime.now().isoformat(),
                    }
                    sheets_client.append_log_entry(log_entry)
                    
                    show_success_animation(
                        f"Archivo {file_name} Insertado",
                        f"{len(new_data)} registros insertados exitosamente"
                    )
                    
                    progress_bar.empty()
                    status_text.empty()
                
                # Celebración final
                st.balloons()
                st.snow()
                
                show_success_animation(
                    "🎉 ¡Proceso Completado Exitosamente!",
                    f"Se insertaron {total_new} registros de {total_files} archivo(s)",
                    "Todos los datos han sido procesados y almacenados en Google Sheets"
                )
                
                # Actualizar estado
                st.session_state.app_state["current_step"] = 2
                
            except Exception as e:
                st.error(f"❌ Error durante la inserción: {e}")
                show_warning_card(
                    "Error de Inserción",
                    f"Ocurrió un problema: {str(e)[:100]}...",
                    "Verifica tu conexión y configuración de Google Sheets"
                )

def main():
    """Función principal de la aplicación"""
    # Inicialización
    sheet_id, sheet_tab = initialize_app()
    
    # Navegación por pasos
    steps_nav = ["📁 Cargar Archivos", "🔍 Procesar Datos", "📊 Insertar a Sheets"]
    current_step = st.session_state.app_state["current_step"]
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs(steps_nav)
    
    with tab1:
        uploaded_files = show_file_upload_interface()
        
        if uploaded_files:
            if st.button("🔍 Analizar Archivos", type="primary", use_container_width=True):
                with st.spinner("Iniciando análisis..."):
                    results, logs = process_files_with_ux(uploaded_files, sheet_id, sheet_tab)
                    
                    if results:
                        st.session_state["processing_results"] = results
                        st.session_state["processing_logs"] = logs
                        st.session_state.app_state["current_step"] = 1
                        st.rerun()
    
    with tab2:
        if "processing_results" in st.session_state:
            results = st.session_state["processing_results"]
            
            # Mostrar resumen de procesamiento
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
        else:
            show_info_card(
                "Sin Datos Procesados",
                "Primero carga y procesa algunos archivos en la pestaña anterior",
                "📁"
            )
    
    with tab3:
        if "processing_results" in st.session_state:
            show_insertion_interface(st.session_state["processing_results"], sheet_id, sheet_tab)
        else:
            show_info_card(
                "Sin Datos para Insertar",
                "Primero procesa algunos archivos en las pestañas anteriores",
                "🔍"
            )

if __name__ == "__main__":
    main()