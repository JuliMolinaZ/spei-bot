#!/usr/bin/env python3
"""
Interfaz de Usuario para Login - SPEI BOT
Diseño ultra profesional y masculino
"""

import streamlit as st
from core.auth import AuthManager
import logging

logger = logging.getLogger(__name__)


class LoginUI:
    """Componente de interfaz de login con diseño premium"""

    def __init__(self):
        """Inicializar componente de login"""
        self.auth_manager = AuthManager()

    def render_login_page(self):
        """
        Renderizar página completa de login con diseño masculino
        """
        # CSS Premium con colores masculinos
        st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

            /* ==================== FONDO ANIMADO MASCULINO ==================== */
            .stApp {
                background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #1a2a6c);
                background-size: 400% 400%;
                animation: gradient-shift 15s ease infinite;
                font-family: 'Inter', sans-serif !important;
            }

            @keyframes gradient-shift {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            @keyframes float {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-15px); }
            }

            @keyframes fade-in {
                from { opacity: 0; transform: scale(0.95); }
                to { opacity: 1; transform: scale(1); }
            }

            @keyframes glow {
                0%, 100% {
                    box-shadow: 0 0 5px rgba(41, 128, 185, 0.5),
                                0 0 10px rgba(41, 128, 185, 0.3),
                                0 0 15px rgba(41, 128, 185, 0.2);
                }
                50% {
                    box-shadow: 0 0 10px rgba(41, 128, 185, 0.7),
                                0 0 20px rgba(41, 128, 185, 0.5),
                                0 0 30px rgba(41, 128, 185, 0.3);
                }
            }

            /* Ocultar elementos de Streamlit */
            #MainMenu { visibility: hidden; }
            header { visibility: hidden; }
            footer { visibility: hidden; }
            .stDeployButton { display: none; }

            /* ==================== CONTENEDOR PRINCIPAL ==================== */
            [data-testid="stAppViewContainer"] > .main {
                display: flex !important;
                justify-content: center !important;
                align-items: center !important;
                min-height: 100vh !important;
                padding: 20px !important;
            }

            [data-testid="stVerticalBlock"] {
                gap: 0 !important;
            }

            /* ==================== FORMULARIO PREMIUM ==================== */
            .stForm {
                background: linear-gradient(145deg, rgba(30, 40, 50, 0.95), rgba(20, 30, 40, 0.98)) !important;
                backdrop-filter: blur(30px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(30px) saturate(180%) !important;
                border-radius: 20px !important;
                border: 1px solid rgba(41, 128, 185, 0.3) !important;
                padding: 60px 50px !important;
                box-shadow: 0 30px 80px rgba(0, 0, 0, 0.5),
                            0 15px 40px rgba(0, 0, 0, 0.3),
                            inset 0 1px 0 rgba(255, 255, 255, 0.1),
                            0 0 60px rgba(41, 128, 185, 0.15) !important;
                max-width: 480px !important;
                margin: 0 auto !important;
                animation: fade-in 0.6s ease-out !important;
                position: relative !important;
            }

            .stForm::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, transparent, #2980b9, #3498db, #2980b9, transparent);
                border-radius: 20px 20px 0 0;
            }

            /* ==================== INPUTS MEJORADOS ==================== */
            .stTextInput {
                margin-bottom: 25px !important;
            }

            .stTextInput > label {
                color: #ecf0f1 !important;
                font-weight: 700 !important;
                font-size: 0.85rem !important;
                text-transform: uppercase !important;
                letter-spacing: 1.5px !important;
                margin-bottom: 12px !important;
                display: block !important;
            }

            .stTextInput > div {
                position: relative !important;
            }

            .stTextInput > div > div {
                position: relative !important;
            }

            .stTextInput > div > div > input {
                background: rgba(52, 73, 94, 0.4) !important;
                backdrop-filter: blur(10px) !important;
                border: 2px solid rgba(41, 128, 185, 0.3) !important;
                border-radius: 12px !important;
                padding: 18px 20px !important;
                padding-left: 50px !important;
                font-size: 1.05rem !important;
                color: #ecf0f1 !important;
                font-weight: 500 !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.3) !important;
            }

            .stTextInput > div > div > input::placeholder {
                color: rgba(236, 240, 241, 0.4) !important;
                font-weight: 400 !important;
            }

            .stTextInput > div > div > input:focus {
                border-color: #3498db !important;
                background: rgba(52, 73, 94, 0.6) !important;
                box-shadow: 0 0 0 4px rgba(52, 152, 219, 0.1),
                            inset 0 2px 8px rgba(0, 0, 0, 0.3),
                            0 0 20px rgba(52, 152, 219, 0.2) !important;
                transform: translateY(-2px) !important;
            }

            /* Iconos de inputs */
            .stTextInput > div > div::before {
                content: attr(data-icon);
                position: absolute;
                left: 18px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 1.3rem;
                color: #3498db;
                z-index: 1;
                pointer-events: none;
            }

            /* ==================== BOTÓN PREMIUM ==================== */
            .stFormSubmitButton > button {
                width: 100% !important;
                background: linear-gradient(135deg, #2980b9 0%, #3498db 50%, #2980b9 100%) !important;
                background-size: 200% 100% !important;
                color: #ffffff !important;
                font-weight: 800 !important;
                font-size: 1.15rem !important;
                text-transform: uppercase !important;
                letter-spacing: 2px !important;
                padding: 20px 40px !important;
                border-radius: 12px !important;
                border: none !important;
                margin-top: 30px !important;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
                box-shadow: 0 10px 30px rgba(41, 128, 185, 0.4),
                            0 5px 15px rgba(0, 0, 0, 0.3),
                            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
                position: relative !important;
                overflow: hidden !important;
            }

            .stFormSubmitButton > button::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(
                    90deg,
                    transparent,
                    rgba(255, 255, 255, 0.2),
                    transparent
                );
                transition: left 0.6s;
            }

            .stFormSubmitButton > button:hover {
                background-position: 100% 0 !important;
                transform: translateY(-3px) !important;
                box-shadow: 0 15px 40px rgba(41, 128, 185, 0.6),
                            0 8px 20px rgba(0, 0, 0, 0.4),
                            inset 0 1px 0 rgba(255, 255, 255, 0.3),
                            0 0 40px rgba(52, 152, 219, 0.3) !important;
                animation: glow 2s ease-in-out infinite !important;
            }

            .stFormSubmitButton > button:hover::before {
                left: 100%;
            }

            .stFormSubmitButton > button:active {
                transform: translateY(-1px) !important;
            }

            /* ==================== ALERTAS ==================== */
            .stAlert {
                border-radius: 12px !important;
                border: none !important;
                backdrop-filter: blur(10px) !important;
                font-weight: 600 !important;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3) !important;
                margin-top: 20px !important;
            }

            .stSuccess {
                background: rgba(39, 174, 96, 0.2) !important;
                border-left: 4px solid #27ae60 !important;
                color: #ecf0f1 !important;
            }

            .stError {
                background: rgba(231, 76, 60, 0.2) !important;
                border-left: 4px solid #e74c3c !important;
                color: #ecf0f1 !important;
            }

            .stWarning {
                background: rgba(243, 156, 18, 0.2) !important;
                border-left: 4px solid #f39c12 !important;
                color: #ecf0f1 !important;
            }

            .stInfo {
                background: rgba(52, 152, 219, 0.2) !important;
                border-left: 4px solid #3498db !important;
                color: #ecf0f1 !important;
            }

            /* ==================== EXPANDER ==================== */
            .streamlit-expanderHeader {
                background: rgba(52, 73, 94, 0.4) !important;
                border-radius: 10px !important;
                border: 1px solid rgba(41, 128, 185, 0.3) !important;
                color: #ecf0f1 !important;
                font-weight: 600 !important;
                padding: 14px 18px !important;
                margin-top: 30px !important;
                transition: all 0.3s ease !important;
            }

            .streamlit-expanderHeader:hover {
                background: rgba(52, 73, 94, 0.6) !important;
                border-color: rgba(52, 152, 219, 0.5) !important;
                box-shadow: 0 4px 15px rgba(41, 128, 185, 0.2) !important;
            }

            .streamlit-expanderContent {
                background: rgba(30, 40, 50, 0.6) !important;
                border: 1px solid rgba(41, 128, 185, 0.2) !important;
                border-radius: 0 0 10px 10px !important;
                padding: 25px !important;
                color: #bdc3c7 !important;
            }

            /* ==================== MARKDOWN ==================== */
            .stMarkdown {
                color: #ecf0f1 !important;
            }

            .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
                color: #ecf0f1 !important;
            }

            .stMarkdown code {
                background: rgba(52, 152, 219, 0.2) !important;
                padding: 3px 8px !important;
                border-radius: 5px !important;
                color: #3498db !important;
                border: 1px solid rgba(52, 152, 219, 0.3) !important;
                font-weight: 600 !important;
            }

            .stMarkdown strong {
                color: #3498db !important;
            }

            /* ==================== RESPONSIVE ==================== */
            @media (max-width: 768px) {
                .stForm {
                    padding: 40px 30px !important;
                }
            }
        </style>
        """, unsafe_allow_html=True)

        # Espaciado superior
        st.markdown("<br>", unsafe_allow_html=True)

        # Header centrado
        st.markdown("""
        <div style='text-align: center; margin-bottom: 50px;'>
            <div style='font-size: 5rem; margin-bottom: 20px; animation: float 3s ease-in-out infinite; filter: drop-shadow(0 10px 30px rgba(41, 128, 185, 0.5));'>
                🤖
            </div>
            <h1 style='font-size: 3.2rem; font-weight: 900; color: #ecf0f1; margin-bottom: 10px; letter-spacing: -1px; text-shadow: 0 4px 20px rgba(0, 0, 0, 0.5), 0 0 40px rgba(52, 152, 219, 0.3);'>
                SPEI BOT
            </h1>
            <p style='color: #bdc3c7; font-size: 1.15rem; font-weight: 500; letter-spacing: 1px; text-transform: uppercase;'>
                Conciliador Bancario Automático
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Formulario de login
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "👤 Usuario",
                placeholder="Ingresa tu usuario",
                key="login_username"
            )

            password = st.text_input(
                "🔒 Contraseña",
                type="password",
                placeholder="Ingresa tu contraseña",
                key="login_password"
            )

            submit = st.form_submit_button("🔐 Iniciar Sesión")

            if submit:
                if not username or not password:
                    st.error("⚠️ Por favor ingresa usuario y contraseña")
                else:
                    # Mostrar estado de carga
                    with st.spinner("🔐 Autenticando..."):
                        # Intentar autenticar
                        success, message = self.auth_manager.authenticate(username, password)

                        if success:
                            st.success("✅ " + message)
                            # Recargar inmediatamente para mostrar app principal
                            st.rerun()
                        else:
                            st.error(message)

        # Footer
        st.markdown("""
        <div style='text-align: center; margin-top: 50px; padding-top: 30px; border-top: 1px solid rgba(41, 128, 185, 0.3); color: #7f8c8d; font-size: 0.9rem;'>
            <div style='margin-bottom: 8px;'>
                🔒 <strong style='color: #3498db;'>Sistema Seguro</strong> con Autenticación JWT
            </div>
            <div style='color: #95a5a6;'>
                © 2025 SPEI BOT - Todos los derechos reservados
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Espaciado inferior
        st.markdown("<br><br>", unsafe_allow_html=True)

    def render_session_info(self):
        """
        Renderizar información de sesión en sidebar
        """
        session_info = self.auth_manager.get_session_info()

        if not session_info:
            return

        st.markdown("---")
        st.markdown("#### 👤 Sesión Activa")

        # Información del usuario
        st.markdown(f"""
        **Usuario:** {session_info.get('name', 'N/A')}
        **Rol:** {session_info.get('role', 'N/A').upper()}
        """)

        # Tiempo de sesión
        remaining_min = session_info.get('remaining_minutes', 0)
        remaining_sec = session_info.get('remaining_seconds', 0)

        if remaining_min > 0:
            st.info(f"⏱️ Sesión expira en: {remaining_min}m {remaining_sec}s")
        else:
            st.warning(f"⏱️ Sesión expira en: {remaining_sec}s")

        # Botón de logout
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            self.auth_manager.logout()
            st.rerun()

    def render_session_status_compact(self):
        """
        Renderizar estado de sesión compacto para header
        """
        session_info = self.auth_manager.get_session_info()

        if not session_info:
            return

        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"""
            <div style='padding: 8px 12px; background: rgba(102, 126, 234, 0.1);
                        border-radius: 8px; font-size: 0.85rem;'>
                👤 <strong>{session_info.get('name', 'Usuario')}</strong>
                <span style='color: #666;'>({session_info.get('role', 'user')})</span>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            if st.button("🚪", key="logout_compact", help="Cerrar sesión"):
                self.auth_manager.logout()
                st.rerun()

    def check_authentication(self) -> bool:
        """
        Verificar autenticación y mostrar login si es necesario

        Returns:
            True si está autenticado, False si no
        """
        if not self.auth_manager.check_session():
            self.render_login_page()
            return False

        return True


# Función auxiliar para uso directo
def require_login() -> bool:
    """
    Función auxiliar para requerir login en cualquier página

    Returns:
        True si está autenticado, False si no
    """
    login_ui = LoginUI()
    return login_ui.check_authentication()
