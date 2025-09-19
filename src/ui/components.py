#!/usr/bin/env python3
"""
Componentes de UI Profesionales - Conciliador Bancario
Componentes reutilizables para la interfaz de usuario
"""

import streamlit as st
import time
import math
from datetime import datetime, timedelta
from typing import List, Tuple, Any

class UIComponents:
    """Clase principal para componentes de UI profesionales"""
    
    def __init__(self):
        """Inicializar componentes UI"""
        self._setup_custom_css()
    
    def _setup_custom_css(self):
        """Configurar CSS personalizado"""
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
            
            /* Métricas personalizadas */
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
    
    def render_main_header(self):
        """Renderizar header principal"""
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        ">
            <h1 style="color: white; font-size: 3rem; margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                🏦 Conciliador Bancario Pro
            </h1>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.3rem; margin-bottom: 2rem;">
                Sistema profesional de conciliación bancaria con Google Sheets
            </p>
            <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
                <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 10px; min-width: 150px;">
                    <h3 style="color: white; margin: 0;">⚡ Rápido</h3>
                    <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">Procesamiento en segundos</p>
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 10px; min-width: 150px;">
                    <h3 style="color: white; margin: 0;">🔒 Seguro</h3>
                    <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">Sin duplicados ni errores</p>
                </div>
                <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 10px; min-width: 150px;">
                    <h3 style="color: white; margin: 0;">🎯 Preciso</h3>
                    <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">Clasificación automática</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar_header(self):
        """Renderizar header del sidebar"""
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
    
    def render_file_upload_zone(self):
        """Renderizar zona de carga de archivos"""
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            border: 2px dashed #1976d2;
        ">
            <h3 style="color: #1976d2; margin-bottom: 1rem;">📁 Zona de Carga de Archivos</h3>
            <p style="color: #1565c0; margin: 0;">
                Arrastra tus archivos bancarios aquí o haz clic para seleccionarlos
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_upload_tips(self):
        """Renderizar consejos de carga"""
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
    
    def render_insertion_summary(self, total_new: int, total_files: int):
        """Renderizar resumen de inserción"""
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
    
    def render_time_estimation(self, total_new: int):
        """Renderizar estimación de tiempo"""
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
    
    def show_info_card(self, title: str, message: str, icon: str = "ℹ️"):
        """Mostrar tarjeta de información"""
        st.info(f"{icon} **{title}**: {message}")
    
    def show_warning_card(self, title: str, message: str, action: str = ""):
        """Mostrar tarjeta de advertencia"""
        st.warning(f"⚠️ **{title}**: {message}")
        if action:
            st.info(f"💡 {action}")
    
    def show_success_card(self, title: str, message: str, details: str = ""):
        """Mostrar tarjeta de éxito"""
        st.success(f"✅ **{title}**: {message}")
        if details:
            st.info(f"📋 {details}")
    
    def show_error_card(self, title: str, message: str, solution: str = ""):
        """Mostrar tarjeta de error"""
        st.error(f"❌ **{title}**: {message}")
        if solution:
            st.info(f"🔧 **Solución**: {solution}")
    
    def render_loading_spinner(self, message: str, duration: int = 3):
        """Renderizar spinner de carga"""
        with st.spinner(message):
            time.sleep(duration)
    
    def render_progress_bar(self, current: int, total: int, message: str = ""):
        """Renderizar barra de progreso"""
        progress = current / total if total > 0 else 0
        st.progress(progress)
        if message:
            st.text(message)
    
    def render_stats_dashboard(self, stats_data: List[Tuple[str, int, str, str]]):
        """Renderizar dashboard de estadísticas"""
        if not stats_data:
            return
        
        cols = st.columns(len(stats_data))
        
        for i, (title, value, icon, color) in enumerate(stats_data):
            with cols[i]:
                st.markdown(f"""
                <div style="
                    background: white;
                    padding: 1.5rem;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    border-left: 5px solid {color};
                ">
                    <h3 style="color: {color}; margin-bottom: 0.5rem;">{icon} {title}</h3>
                    <div style="font-size: 2rem; color: {color}; font-weight: bold;">{value}</div>
                </div>
                """, unsafe_allow_html=True)
    
    def render_step_indicator(self, current_step: int, total_steps: int, step_names: List[str]):
        """Renderizar indicador de pasos"""
        st.markdown("### 📍 Progreso General")
        
        cols = st.columns(total_steps)
        for i, (col, step_name) in enumerate(zip(cols, step_names)):
            with col:
                if i <= current_step:
                    status = "✅" if i < current_step else "🔄"
                    color = "#28a745" if i < current_step else "#ffc107"
                else:
                    status = "⏳"
                    color = "#6c757d"
                
                st.markdown(f"""
                <div style="
                    background: white;
                    padding: 1rem;
                    border-radius: 10px;
                    text-align: center;
                    border-left: 4px solid {color};
                ">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{status}</div>
                    <div style="font-size: 0.9rem; color: {color}; font-weight: bold;">{step_name}</div>
                </div>
                """, unsafe_allow_html=True)
    
    def render_metrics_grid(self, metrics: Dict[str, Any]):
        """Renderizar grid de métricas"""
        if not metrics:
            return
        
        cols = st.columns(len(metrics))
        
        for i, (key, value) in enumerate(metrics.items()):
            with cols[i]:
                st.metric(key, value)
    
    def render_data_preview(self, data: Any, title: str = "Vista Previa"):
        """Renderizar vista previa de datos"""
        if data is None or (hasattr(data, 'empty') and data.empty):
            st.info("No hay datos para mostrar")
            return
        
        st.markdown(f"### {title}")
        
        if hasattr(data, 'head'):
            st.dataframe(data.head(10), use_container_width=True)
        else:
            st.write(data)
    
    def render_confirmation_dialog(self, title: str, message: str, confirm_text: str = "Confirmar") -> bool:
        """Renderizar diálogo de confirmación"""
        st.markdown(f"### {title}")
        st.markdown(message)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Sí, continuar", type="primary"):
                return True
        
        with col2:
            if st.button("❌ Cancelar"):
                return False
        
        return False