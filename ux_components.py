#!/usr/bin/env python3
"""
Componentes UX avanzados para la aplicación de conciliación
"""

import streamlit as st
import time
import math
from datetime import datetime, timedelta

def show_hero_section():
    """Sección hero impresionante"""
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
            🏦 Conciliación Bancaria
        </h1>
        <p style="color: rgba(255,255,255,0.9); font-size: 1.3rem; margin-bottom: 2rem;">
            Procesa tus movimientos bancarios de forma automática, inteligente y segura
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

def show_step_indicator(current_step, total_steps, step_names):
    """Indicador de pasos visual"""
    st.markdown("### 📍 Progreso General")
    
    cols = st.columns(total_steps)
    for i, (col, step_name) in enumerate(zip(cols, step_names)):
        with col:
            if i < current_step:
                # Paso completado
                st.markdown(f"""
                <div style="
                    background: #28a745;
                    color: white;
                    padding: 1rem;
                    border-radius: 10px;
                    text-align: center;
                    margin-bottom: 0.5rem;
                    box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3);
                ">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">✅</div>
                    <div style="font-weight: bold;">{step_name}</div>
                    <div style="font-size: 0.8rem; opacity: 0.9;">Completado</div>
                </div>
                """, unsafe_allow_html=True)
            elif i == current_step:
                # Paso actual
                st.markdown(f"""
                <div style="
                    background: linear-gradient(45deg, #007bff, #0056b3);
                    color: white;
                    padding: 1rem;
                    border-radius: 10px;
                    text-align: center;
                    margin-bottom: 0.5rem;
                    box-shadow: 0 4px 8px rgba(0, 123, 255, 0.4);
                    animation: pulse 2s infinite;
                ">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">⚡</div>
                    <div style="font-weight: bold;">{step_name}</div>
                    <div style="font-size: 0.8rem; opacity: 0.9;">En progreso...</div>
                </div>
                <style>
                @keyframes pulse {{
                    0% {{ transform: scale(1); }}
                    50% {{ transform: scale(1.05); }}
                    100% {{ transform: scale(1); }}
                }}
                </style>
                """, unsafe_allow_html=True)
            else:
                # Paso pendiente
                st.markdown(f"""
                <div style="
                    background: #f8f9fa;
                    color: #6c757d;
                    padding: 1rem;
                    border-radius: 10px;
                    text-align: center;
                    margin-bottom: 0.5rem;
                    border: 2px dashed #dee2e6;
                ">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">⏳</div>
                    <div style="font-weight: bold;">{step_name}</div>
                    <div style="font-size: 0.8rem;">Pendiente</div>
                </div>
                """, unsafe_allow_html=True)

def show_advanced_progress(current_value, max_value, title, subtitle="", estimated_time=None):
    """Barra de progreso avanzada con estimaciones de tiempo"""
    percentage = (current_value / max_value) * 100 if max_value > 0 else 0
    
    # Calcular tiempo restante
    time_info = ""
    if estimated_time:
        remaining_time = estimated_time * (1 - percentage / 100)
        if remaining_time > 60:
            time_info = f"⏱️ Tiempo estimado restante: {remaining_time/60:.1f} minutos"
        elif remaining_time > 1:
            time_info = f"⏱️ Tiempo estimado restante: {remaining_time:.0f} segundos"
        else:
            time_info = "⏱️ Casi terminado..."
    
    st.markdown(f"""
    <div style="
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 1rem 0;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h4 style="margin: 0; color: #333;">{title}</h4>
            <span style="font-weight: bold; color: #007bff; font-size: 1.2rem;">{percentage:.1f}%</span>
        </div>
        
        <div style="
            background: #e9ecef;
            height: 12px;
            border-radius: 6px;
            margin-bottom: 1rem;
            overflow: hidden;
        ">
            <div style="
                background: linear-gradient(90deg, #007bff, #0056b3);
                height: 100%;
                width: {percentage}%;
                border-radius: 6px;
                transition: width 0.5s ease;
                box-shadow: 0 2px 4px rgba(0,123,255,0.3);
            "></div>
        </div>
        
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">
            {subtitle}
        </div>
        <div style="font-size: 0.9rem; color: #28a745; font-weight: 500;">
            {time_info}
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_loading_spinner(message, estimated_seconds=None):
    """Spinner de carga con mensaje y tiempo estimado"""
    time_text = ""
    if estimated_seconds:
        if estimated_seconds > 60:
            time_text = f" (≈ {estimated_seconds/60:.0f} minutos)"
        else:
            time_text = f" (≈ {estimated_seconds:.0f} segundos)"
    
    st.markdown(f"""
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 2rem;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        margin: 1rem 0;
    ">
        <div style="
            width: 60px;
            height: 60px;
            border: 4px solid #e3e3e3;
            border-top: 4px solid #007bff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 1rem;
        "></div>
        <h3 style="color: #333; margin-bottom: 0.5rem;">{message}</h3>
        <p style="color: #666; font-size: 1rem; margin: 0;">{time_text}</p>
    </div>
    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)

def show_success_animation(title, subtitle, details=None):
    """Animación de éxito impresionante"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 10px 25px rgba(40, 167, 69, 0.3);
        animation: successPulse 0.6s ease-out;
    ">
        <div style="font-size: 4rem; margin-bottom: 1rem; animation: bounce 1s ease-out;">✅</div>
        <h2 style="margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">{title}</h2>
        <p style="font-size: 1.2rem; margin-bottom: 1rem; opacity: 0.9;">{subtitle}</p>
        {f'<div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 10px; font-size: 0.9rem;">{details}</div>' if details else ''}
    </div>
    <style>
    @keyframes successPulse {{
        0% {{ transform: scale(0.8); opacity: 0; }}
        100% {{ transform: scale(1); opacity: 1; }}
    }}
    @keyframes bounce {{
        0%, 20%, 60%, 100% {{ transform: translateY(0); }}
        40% {{ transform: translateY(-10px); }}
        80% {{ transform: translateY(-5px); }}
    }}
    </style>
    """, unsafe_allow_html=True)

def show_warning_card(title, message, action_needed=None):
    """Tarjeta de advertencia elegante"""
    action_text = f"<div style='margin-top: 1rem; font-weight: bold; color: #856404;'>👉 {action_needed}</div>" if action_needed else ""
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 5px solid #ffc107;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(255, 193, 7, 0.2);
    ">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <div style="font-size: 1.5rem; margin-right: 0.5rem;">⚠️</div>
            <h4 style="margin: 0; color: #856404;">{title}</h4>
        </div>
        <p style="color: #856404; margin: 0; line-height: 1.6;">{message}</p>
        {action_text}
    </div>
    """, unsafe_allow_html=True)

def show_info_card(title, message, icon="ℹ️"):
    """Tarjeta informativa elegante"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border-left: 5px solid #17a2b8;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(23, 162, 184, 0.2);
    ">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <div style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</div>
            <h4 style="margin: 0; color: #0c5460;">{title}</h4>
        </div>
        <p style="color: #0c5460; margin: 0; line-height: 1.6;">{message}</p>
    </div>
    """, unsafe_allow_html=True)

def show_stats_dashboard(stats_data):
    """Dashboard de estadísticas impresionante"""
    st.markdown("### 📊 Resumen de Procesamiento")
    
    cols = st.columns(len(stats_data))
    for col, (title, value, icon, color) in zip(cols, stats_data):
        with col:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {color} 0%, {color}dd 100%);
                color: white;
                padding: 1.5rem;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 8px 16px {color}40;
                transform: translateY(0);
                transition: transform 0.3s ease;
            ">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
                <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">{value}</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">{title}</div>
            </div>
            """, unsafe_allow_html=True)

def show_file_upload_zone():
    """Zona de carga de archivos mejorada"""
    st.markdown("""
    <style>
    .upload-container {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 3px dashed #dee2e6;
        border-radius: 20px;
        padding: 3rem 2rem;
        text-align: center;
        margin: 2rem 0;
        transition: all 0.3s ease;
    }
    .upload-container:hover {
        border-color: #007bff;
        background: linear-gradient(135deg, #e7f3ff 0%, #d4edda 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,123,255,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="upload-container">
        <div style="font-size: 4rem; margin-bottom: 1rem;">📁</div>
        <h3 style="color: #495057; margin-bottom: 1rem;">Sube tus archivos bancarios</h3>
        <p style="color: #6c757d; font-size: 1.1rem; margin-bottom: 2rem;">
            Arrastra y suelta aquí tus archivos TXT o CSV de BanBajío<br>
            <small>Formatos soportados: .txt, .csv | Tamaño máximo: 200MB</small>
        </p>
    </div>
    """, unsafe_allow_html=True)

def estimate_processing_time(num_records):
    """Estima tiempo de procesamiento basado en número de registros"""
    # Estimaciones basadas en rendimiento típico
    base_time = 2  # segundos base
    record_time = 0.01  # segundos por registro
    
    estimated = base_time + (num_records * record_time)
    
    # Añadir factores adicionales
    if num_records > 1000:
        estimated *= 1.2  # Factor para archivos grandes
    
    return max(estimated, 3)  # Mínimo 3 segundos

def show_time_estimation(operation, num_items):
    """Muestra estimación de tiempo para una operación"""
    time_estimates = {
        "reading": 0.5,
        "parsing": 0.01,
        "classifying": 0.005,
        "uid_generation": 0.008,
        "duplicate_analysis": 0.02,
        "formatting": 0.003,
        "sheets_insertion": 0.05
    }
    
    estimated_seconds = time_estimates.get(operation, 0.01) * num_items + 1
    
    if estimated_seconds < 3:
        time_text = "Unos segundos"
    elif estimated_seconds < 60:
        time_text = f"{estimated_seconds:.0f} segundos"
    elif estimated_seconds < 300:
        time_text = f"{estimated_seconds/60:.1f} minutos"
    else:
        time_text = f"{estimated_seconds/60:.0f} minutos"
    
    return estimated_seconds, time_text