#!/usr/bin/env python3
"""
Componentes de UI Profesionales - Conciliador Bancario
Componentes reutilizables para la interfaz de usuario
"""

import streamlit as st
import time
import math
from datetime import datetime, timedelta
from typing import List, Tuple, Any, Dict

class UIComponents:
    """Clase principal para componentes de UI profesionales"""
    
    def __init__(self):
        """Inicializar componentes UI"""
        self._setup_custom_css()
    
    def _setup_custom_css(self):
        """Configurar CSS personalizado profesional para SPEI BOT"""
        st.markdown("""
        <style>
            /* Importar fuente moderna */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

            /* Tema general */
            .main > div {
                padding-top: 1rem;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            }

            /* Mejorar sidebar con tema oscuro profesional */
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f1419 100%);
            }

            [data-testid="stSidebar"] .element-container {
                color: rgba(255,255,255,0.9);
            }

            /* Botones personalizados con efecto moderno */
            .stButton > button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 0.85rem 2.5rem;
                font-weight: 700;
                font-size: 1.1rem;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 4px 15px rgba(102,126,234,0.4);
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .stButton > button:hover {
                transform: translateY(-3px) scale(1.02);
                box-shadow: 0 8px 25px rgba(102,126,234,0.6);
                background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
            }

            .stButton > button:active {
                transform: translateY(-1px);
            }

            /* Métricas personalizadas con estilo glassmorphism */
            [data-testid="metric-container"] {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 16px;
                padding: 1.5rem;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                border: 1px solid rgba(255,255,255,0.18);
                backdrop-filter: blur(10px);
                transition: transform 0.3s ease;
            }

            [data-testid="metric-container"]:hover {
                transform: translateY(-2px);
                box-shadow: 0 12px 40px rgba(0,0,0,0.15);
            }

            /* File uploader personalizado */
            .stFileUploader > div > div {
                background: linear-gradient(135deg, rgba(102,126,234,0.05) 0%, rgba(118,75,162,0.05) 100%);
                border: 3px dashed rgba(102,126,234,0.4);
                border-radius: 20px;
                padding: 3rem;
                transition: all 0.3s ease;
            }

            .stFileUploader > div > div:hover {
                border-color: rgba(102,126,234,0.7);
                background: linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.1) 100%);
            }

            /* Tabs mejoradas */
            .stTabs [data-baseweb="tab-list"] {
                gap: 1rem;
                background: linear-gradient(135deg, rgba(102,126,234,0.05) 0%, rgba(118,75,162,0.05) 100%);
                border-radius: 15px;
                padding: 0.5rem;
            }

            .stTabs [data-baseweb="tab"] {
                border-radius: 10px;
                padding: 0.75rem 1.5rem;
                font-weight: 600;
                transition: all 0.3s ease;
            }

            .stTabs [aria-selected="true"] {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }

            /* Expanders mejorados */
            .streamlit-expanderHeader {
                background: linear-gradient(135deg, rgba(102,126,234,0.08) 0%, rgba(118,75,162,0.08) 100%);
                border-radius: 12px;
                font-weight: 600;
                padding: 1rem;
                border: 1px solid rgba(102,126,234,0.2);
            }

            .streamlit-expanderHeader:hover {
                background: linear-gradient(135deg, rgba(102,126,234,0.15) 0%, rgba(118,75,162,0.15) 100%);
            }

            /* Inputs mejorados */
            .stTextInput > div > div > input {
                border-radius: 10px;
                border: 2px solid rgba(102,126,234,0.3);
                padding: 0.75rem 1rem;
                font-size: 1rem;
                transition: all 0.3s ease;
            }

            .stTextInput > div > div > input:focus {
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
            }

            /* Alerts mejoradas */
            .stAlert {
                border-radius: 12px;
                border: none;
                padding: 1.25rem;
                font-weight: 500;
            }

            /* Progress bar mejorada */
            .stProgress > div > div > div {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                border-radius: 10px;
            }

            /* Ocultar elementos innecesarios */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}

            /* Animaciones suaves y profesionales */
            .element-container, .stMarkdown, .stAlert {
                animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            }

            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            /* Scrollbar personalizada */
            ::-webkit-scrollbar {
                width: 10px;
                height: 10px;
            }

            ::-webkit-scrollbar-track {
                background: #f1f1f1;
                border-radius: 10px;
            }

            ::-webkit-scrollbar-thumb {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 10px;
            }

            ::-webkit-scrollbar-thumb:hover {
                background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
            }
        </style>
        """, unsafe_allow_html=True)
    
    def render_main_header(self):
        """Renderizar header principal con branding SPEI BOT"""
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            padding: 3rem 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 15px 40px rgba(0,0,0,0.4);
            border: 1px solid rgba(255,255,255,0.1);
        ">
            <h1 style="color: white; font-size: 3.5rem; margin-bottom: 0.5rem; text-shadow: 3px 3px 6px rgba(0,0,0,0.5); font-weight: 800; letter-spacing: 2px;">
                🤖 SPEI BOT
            </h1>
            <p style="color: #4fc3f7; font-size: 1.1rem; margin-bottom: 0.5rem; font-weight: 600; letter-spacing: 1px;">
                SISTEMA PROFESIONAL DE CONCILIACIÓN BANCARIA
            </p>
            <p style="color: rgba(255,255,255,0.8); font-size: 1rem; margin-bottom: 2rem;">
                Automatiza la conciliación de transacciones SPEI con Google Sheets
            </p>
            <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-top: 2rem;">
                <div style="background: linear-gradient(135deg, rgba(76,175,80,0.3) 0%, rgba(76,175,80,0.1) 100%); padding: 1.5rem; border-radius: 15px; min-width: 170px; border: 2px solid rgba(76,175,80,0.4); backdrop-filter: blur(10px);">
                    <h3 style="color: #81c784; margin: 0; font-size: 1.8rem;">⚡</h3>
                    <h4 style="color: white; margin: 0.5rem 0;">Ultra Rápido</h4>
                    <p style="color: rgba(255,255,255,0.7); margin: 0; font-size: 0.85rem;">Procesamiento automático<br>en tiempo real</p>
                </div>
                <div style="background: linear-gradient(135deg, rgba(33,150,243,0.3) 0%, rgba(33,150,243,0.1) 100%); padding: 1.5rem; border-radius: 15px; min-width: 170px; border: 2px solid rgba(33,150,243,0.4); backdrop-filter: blur(10px);">
                    <h3 style="color: #64b5f6; margin: 0; font-size: 1.8rem;">🔒</h3>
                    <h4 style="color: white; margin: 0.5rem 0;">100% Seguro</h4>
                    <p style="color: rgba(255,255,255,0.7); margin: 0; font-size: 0.85rem;">Validación de duplicados<br>sin errores</p>
                </div>
                <div style="background: linear-gradient(135deg, rgba(255,152,0,0.3) 0%, rgba(255,152,0,0.1) 100%); padding: 1.5rem; border-radius: 15px; min-width: 170px; border: 2px solid rgba(255,152,0,0.4); backdrop-filter: blur(10px);">
                    <h3 style="color: #ffb74d; margin: 0; font-size: 1.8rem;">🎯</h3>
                    <h4 style="color: white; margin: 0.5rem 0;">Inteligente</h4>
                    <p style="color: rgba(255,255,255,0.7); margin: 0; font-size: 0.85rem;">Clasificación automática<br>de transacciones</p>
                </div>
                <div style="background: linear-gradient(135deg, rgba(156,39,176,0.3) 0%, rgba(156,39,176,0.1) 100%); padding: 1.5rem; border-radius: 15px; min-width: 170px; border: 2px solid rgba(156,39,176,0.4); backdrop-filter: blur(10px);">
                    <h3 style="color: #ba68c8; margin: 0; font-size: 1.8rem;">📊</h3>
                    <h4 style="color: white; margin: 0.5rem 0;">Integrado</h4>
                    <p style="color: rgba(255,255,255,0.7); margin: 0; font-size: 0.85rem;">Conexión directa con<br>Google Sheets</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar_header(self):
        """Renderizar header del sidebar con branding SPEI BOT"""
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #0f2027 0%, #2c5364 100%);
            padding: 2rem 1rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        ">
            <h2 style="color: white; margin: 0; font-weight: 700;">⚙️ Configuración</h2>
            <p style="color: #4fc3f7; margin: 0.5rem 0 0 0; font-size: 0.85rem; font-weight: 500;">SPEI BOT v2.0</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_file_upload_zone(self):
        """Renderizar zona de carga de archivos con estilo profesional"""
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.1) 100%);
            padding: 2.5rem;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 2rem;
            border: 3px dashed rgba(102,126,234,0.5);
            box-shadow: 0 8px 20px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📁</div>
            <h3 style="color: #667eea; margin-bottom: 1rem; font-weight: 700;">Zona de Carga de Archivos</h3>
            <p style="color: #764ba2; margin: 0; font-size: 1.1rem; font-weight: 500;">
                Arrastra tus archivos bancarios aquí o haz clic para seleccionarlos
            </p>
            <p style="color: rgba(102,126,234,0.7); margin-top: 0.5rem; font-size: 0.9rem;">
                Soporta archivos TXT y CSV de BanBajío
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_upload_tips(self):
        """Renderizar consejos de carga con diseño moderno"""
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(76,175,80,0.1) 0%, rgba(76,175,80,0.05) 100%);
            padding: 1.5rem;
            border-radius: 15px;
            text-align: left;
            border-left: 5px solid #4caf50;
            box-shadow: 0 4px 15px rgba(0,0,0,0.06);
        ">
            <h4 style="color: #4caf50; margin-bottom: 1rem; font-weight: 700;">💡 Consejos Rápidos</h4>
            <p style="color: #2e7d32; font-size: 0.95rem; margin: 0; line-height: 1.8;">
                ✓ Acepta archivos <strong>TXT y CSV</strong><br>
                ✓ Detecta automáticamente <strong>BanBajío</strong><br>
                ✓ Procesa <strong>múltiples archivos</strong><br>
                ✓ Tamaño máximo: <strong>200MB por archivo</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_insertion_summary(self, total_new: int, total_files: int):
        """Renderizar resumen de inserción con diseño profesional"""
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(76,175,80,0.15) 0%, rgba(76,175,80,0.08) 100%);
            padding: 2.5rem;
            border-radius: 20px;
            text-align: center;
            border: 2px solid rgba(76,175,80,0.3);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <h2 style="color: #2e7d32; margin-bottom: 1.5rem; font-weight: 800; font-size: 1.8rem;">📊 Resumen de Inserción</h2>
            <div style="
                background: linear-gradient(135deg, #4caf50 0%, #66bb6a 100%);
                font-size: 3.5rem;
                color: white;
                margin-bottom: 1.5rem;
                padding: 1rem;
                border-radius: 15px;
                font-weight: 900;
                box-shadow: 0 8px 20px rgba(76,175,80,0.4);
            ">{total_new:,}</div>
            <p style="color: #2e7d32; font-size: 1.3rem; margin: 0; font-weight: 600;">
                Registros nuevos listos para insertar
            </p>
            <p style="color: #4caf50; font-size: 1rem; margin-top: 0.5rem;">
                de {total_files} archivo(s) procesado(s)
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_time_estimation(self, total_new: int):
        """Renderizar estimación de tiempo realista"""
        # Estimación más realista:
        # - 10-15 segundos de overhead (conexión, validación, búsqueda de fila vacía)
        # - ~0.1-0.15 segundos por registro en batch
        base_overhead = 15  # segundos base
        per_record_time = 0.12  # segundos por registro
        estimated_time = base_overhead + (total_new * per_record_time)

        if estimated_time < 60:
            time_text = f"{int(estimated_time)} - {int(estimated_time * 1.3)} segundos"
        else:
            min_minutes = estimated_time / 60
            max_minutes = (estimated_time * 1.3) / 60
            time_text = f"{min_minutes:.1f} - {max_minutes:.1f} minutos"

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(255,193,7,0.15) 0%, rgba(255,193,7,0.08) 100%);
            padding: 2.5rem;
            border-radius: 20px;
            text-align: center;
            border: 2px solid rgba(255,193,7,0.3);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <h3 style="color: #f57c00; margin-bottom: 1.5rem; font-weight: 800; font-size: 1.8rem;">⏱️ Tiempo Estimado</h3>
            <div style="
                background: linear-gradient(135deg, #ffc107 0%, #ffb300 100%);
                font-size: 2.5rem;
                color: white;
                margin-bottom: 1.5rem;
                padding: 1rem;
                border-radius: 15px;
                font-weight: 900;
                box-shadow: 0 8px 20px rgba(255,193,7,0.4);
            ">{time_text}</div>
            <p style="color: #f57c00; margin: 0.5rem 0 1.5rem 0; font-size: 1.2rem; font-weight: 600;">
                Inserción a Google Sheets
            </p>
            <div style="
                background: linear-gradient(135deg, rgba(244,67,54,0.2) 0%, rgba(244,67,54,0.1) 100%);
                padding: 1rem;
                border-radius: 12px;
                margin-top: 1rem;
                border: 2px solid rgba(244,67,54,0.3);
            ">
                <p style="color: #c62828; margin: 0; font-size: 1rem; font-weight: 700;">
                    ⚠️ Mantén esta ventana abierta durante el proceso
                </p>
            </div>
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