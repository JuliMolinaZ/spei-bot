#!/usr/bin/env python3
"""
UI de Login Moderna y Segura para SPEI BOT
"""

import streamlit as st
from datetime import datetime, timedelta
import time
import auth

def show_login_page():
    """Muestra la página de login con diseño moderno"""

    # CSS personalizado para login
    st.markdown("""
    <style>
        /* Ocultar elementos de Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Fondo degradado */
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        /* Container principal de login */
        .login-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            padding: 3rem 2.5rem;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 450px;
            margin: 0 auto;
            animation: slideIn 0.5s ease-out;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Logo y título */
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }

        .login-logo {
            font-size: 4rem;
            margin-bottom: 0.5rem;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }

        .login-title {
            color: #2c3e50;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .login-subtitle {
            color: #7f8c8d;
            font-size: 0.95rem;
            margin-bottom: 0;
        }

        /* Inputs personalizados */
        .stTextInput > div > div > input {
            border-radius: 12px;
            border: 2px solid #e1e8ed;
            padding: 0.75rem 1rem;
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        /* Botón de login */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.85rem 2rem;
            font-weight: 600;
            font-size: 1.05rem;
            width: 100%;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            margin-top: 1rem;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }

        .stButton > button:active {
            transform: translateY(0);
        }

        /* Alerts personalizados */
        .stAlert {
            border-radius: 12px;
            border: none;
            padding: 1rem;
            margin-top: 1rem;
        }

        /* Footer del login */
        .login-footer {
            text-align: center;
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 1px solid #e1e8ed;
            color: #95a5a6;
            font-size: 0.85rem;
        }

        /* Animación de loading */
        .login-loading {
            text-align: center;
            color: #667eea;
            font-weight: 600;
            margin-top: 1rem;
        }

        /* Security badge */
        .security-badge {
            display: inline-flex;
            align-items: center;
            background: #f0f4f8;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.85rem;
            color: #2c3e50;
            margin-top: 1rem;
        }

        .security-badge::before {
            content: "🔒";
            margin-right: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # Espaciado superior
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Container de login
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div class="login-container">
            <div class="login-header">
                <div class="login-logo">🏦</div>
                <h1 class="login-title">SPEI BOT</h1>
                <p class="login-subtitle">Sistema de Conciliación Bancaria</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Formulario de login
        with st.form("login_form", clear_on_submit=False):
            st.markdown("### 🔐 Iniciar Sesión")

            username = st.text_input(
                "Usuario",
                placeholder="Ingresa tu usuario",
                key="username_input",
                help="Usuario proporcionado por el administrador"
            )

            password = st.text_input(
                "Contraseña",
                type="password",
                placeholder="Ingresa tu contraseña",
                key="password_input",
                help="Contraseña segura"
            )

            st.markdown("<br>", unsafe_allow_html=True)

            submit_button = st.form_submit_button("🚀 Iniciar Sesión", use_container_width=True)

            if submit_button:
                if not username or not password:
                    st.error("⚠️ Por favor ingresa usuario y contraseña")
                else:
                    # Mostrar loading
                    with st.spinner("🔄 Verificando credenciales..."):
                        time.sleep(0.5)  # Simulación de procesamiento

                        # Autenticar
                        result = auth.authenticate_user(username, password)

                        if result.get("success"):
                            # Login exitoso
                            st.success("✅ ¡Login exitoso! Redirigiendo...")

                            # Guardar datos en session state
                            st.session_state.authenticated = True
                            st.session_state.user_data = {
                                "username": result["username"],
                                "role": result["role"],
                                "name": result["name"]
                            }
                            st.session_state.token = auth.create_access_token(
                                result["username"],
                                result["role"]
                            )
                            st.session_state.last_activity = datetime.now()

                            time.sleep(1)
                            st.rerun()

                        elif result.get("error") == "blocked":
                            # Usuario bloqueado
                            remaining_time = result.get("remaining_time", 0)
                            minutes = remaining_time // 60
                            seconds = remaining_time % 60

                            st.error(
                                f"🚫 **Cuenta bloqueada temporalmente**\n\n"
                                f"Demasiados intentos fallidos. Por favor espera {minutes}m {seconds}s"
                            )

                        else:
                            # Credenciales inválidas
                            remaining = result.get("remaining_attempts", 0)

                            if remaining > 0:
                                st.error(
                                    f"❌ **Credenciales inválidas**\n\n"
                                    f"Te quedan {remaining} intento(s) antes de ser bloqueado."
                                )
                            else:
                                st.error(
                                    "❌ **Usuario o contraseña incorrectos**\n\n"
                                    "Verifica tus credenciales e intenta nuevamente."
                                )

        # Footer de seguridad
        st.markdown("""
        <div class="login-footer">
            <div class="security-badge">Conexión segura con encriptación JWT</div>
            <p style="margin-top: 1rem;">
                <strong>SPEI BOT</strong> v2.0 | 2025<br>
                Sistema protegido con autenticación avanzada
            </p>
        </div>
        """, unsafe_allow_html=True)

def show_session_info_sidebar():
    """Muestra información de sesión en el sidebar"""
    if not auth.is_authenticated():
        return

    session_info = auth.get_session_info()

    with st.sidebar:
        st.markdown("---")
        st.markdown("### 👤 Sesión Activa")

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            padding: 1rem;
            border-radius: 12px;
            margin-bottom: 1rem;
        ">
            <div style="color: #2e7d32; font-weight: 600; margin-bottom: 0.5rem;">
                👤 {session_info.get('name', 'Usuario')}
            </div>
            <div style="color: #558b2f; font-size: 0.85rem;">
                @{session_info.get('username', 'N/A')}
            </div>
            <div style="color: #689f38; font-size: 0.8rem; margin-top: 0.5rem;">
                🔑 {session_info.get('role', 'user').upper()}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Tiempo restante de sesión
        time_remaining = session_info.get('time_remaining_seconds', 0)
        minutes_remaining = int(time_remaining // 60)

        if minutes_remaining < 10:
            color = "#ff9800"
            icon = "⚠️"
        else:
            color = "#4caf50"
            icon = "⏱️"

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
            padding: 0.75rem;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 1rem;
        ">
            <div style="color: {color}; font-size: 0.85rem;">
                {icon} Sesión expira en
            </div>
            <div style="color: #e65100; font-weight: 700; font-size: 1.2rem;">
                {minutes_remaining} min
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Botón de logout
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            auth.logout()
            st.rerun()

def show_access_denied():
    """Muestra mensaje de acceso denegado"""
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<br><br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style="
            background: white;
            padding: 3rem 2rem;
            border-radius: 24px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        ">
            <div style="font-size: 5rem; margin-bottom: 1rem;">🔒</div>
            <h1 style="color: #2c3e50; margin-bottom: 1rem;">Acceso Denegado</h1>
            <p style="color: #7f8c8d; font-size: 1.1rem; margin-bottom: 2rem;">
                Tu sesión ha expirado o no tienes permisos para acceder a esta página.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🔐 Volver a Iniciar Sesión", use_container_width=True):
            auth.logout()
            st.rerun()
