#!/bin/bash
# Script de inicio profesional para Conciliador Bancario

set -e  # Salir en caso de error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Banner de inicio
show_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🏦 CONCILIADOR BANCARIO PRO              ║"
    echo "║                    Sistema Profesional v2.0                ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Verificar dependencias
check_dependencies() {
    log "Verificando dependencias..."
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 no está instalado"
        exit 1
    fi
    
    # Verificar versión de Python
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if [[ $(echo "$python_version < 3.10" | bc -l) -eq 1 ]]; then
        error "Se requiere Python 3.10 o superior. Versión actual: $python_version"
        exit 1
    fi
    
    success "Python $python_version detectado"
    
    # Verificar pip
    if ! command -v pip &> /dev/null; then
        error "pip no está instalado"
        exit 1
    fi
    
    success "pip detectado"
}

# Configurar entorno virtual
setup_venv() {
    log "Configurando entorno virtual..."
    
    if [ ! -d "venv" ]; then
        log "Creando entorno virtual..."
        python3 -m venv venv
        success "Entorno virtual creado"
    else
        log "Entorno virtual ya existe"
    fi
    
    # Activar entorno virtual
    source venv/bin/activate
    success "Entorno virtual activado"
}

# Instalar dependencias
install_dependencies() {
    log "Instalando dependencias..."
    
    if [ -f "requirements.txt" ]; then
        pip install --upgrade pip
        pip install -r requirements.txt
        success "Dependencias instaladas"
    else
        error "Archivo requirements.txt no encontrado"
        exit 1
    fi
}

# Verificar configuración
check_config() {
    log "Verificando configuración..."
    
    if [ ! -f ".env" ]; then
        warning "Archivo .env no encontrado"
        if [ -f "env.example" ]; then
            log "Copiando archivo de ejemplo..."
            cp env.example .env
            warning "Archivo .env creado desde ejemplo. Por favor, configura tus valores."
        else
            error "Archivo env.example no encontrado"
            exit 1
        fi
    else
        success "Archivo .env encontrado"
    fi
    
    # Verificar directorio de logs
    if [ ! -d "logs" ]; then
        log "Creando directorio de logs..."
        mkdir -p logs
        success "Directorio de logs creado"
    fi
}

# Verificar credenciales de Google
check_google_credentials() {
    log "Verificando credenciales de Google..."
    
    # Verificar si está en modo demo
    if grep -q "DEMO_MODE=true" .env 2>/dev/null; then
        warning "Modo demo activado - saltando verificación de credenciales"
        return 0
    fi
    
    # Verificar variables de entorno
    if grep -q "GOOGLE_SA_JSON=" .env 2>/dev/null && ! grep -q "GOOGLE_SA_JSON=$" .env 2>/dev/null; then
        success "GOOGLE_SA_JSON configurado"
    elif grep -q "GOOGLE_APPLICATION_CREDENTIALS=" .env 2>/dev/null && ! grep -q "GOOGLE_APPLICATION_CREDENTIALS=$" .env 2>/dev/null; then
        success "GOOGLE_APPLICATION_CREDENTIALS configurado"
    elif [ -f "spei-bot-b202259d87e7.json" ]; then
        success "Archivo de credenciales local encontrado"
    else
        warning "Credenciales de Google no configuradas - ejecutando en modo demo"
    fi
}

# Iniciar aplicación
start_app() {
    log "Iniciando Conciliador Bancario..."
    
    # Verificar si el puerto está en uso
    if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null ; then
        warning "Puerto 8501 ya está en uso"
        log "Intentando detener proceso existente..."
        pkill -f "streamlit run" || true
        sleep 2
    fi
    
    # Iniciar aplicación
    log "Ejecutando: python main.py"
    python main.py
}

# Función de limpieza
cleanup() {
    log "Limpiando procesos..."
    pkill -f "streamlit run" || true
    success "Limpieza completada"
}

# Manejar señales de terminación
trap cleanup SIGINT SIGTERM

# Función principal
main() {
    show_banner
    
    # Verificar argumentos
    case "${1:-start}" in
        "start")
            check_dependencies
            setup_venv
            install_dependencies
            check_config
            check_google_credentials
            start_app
            ;;
        "install")
            check_dependencies
            setup_venv
            install_dependencies
            success "Instalación completada"
            ;;
        "check")
            check_dependencies
            check_config
            check_google_credentials
            success "Verificación completada"
            ;;
        "clean")
            cleanup
            ;;
        "help"|"-h"|"--help")
            echo "Uso: $0 [comando]"
            echo ""
            echo "Comandos:"
            echo "  start    Iniciar aplicación (por defecto)"
            echo "  install  Solo instalar dependencias"
            echo "  check    Verificar configuración"
            echo "  clean    Limpiar procesos"
            echo "  help     Mostrar esta ayuda"
            ;;
        *)
            error "Comando desconocido: $1"
            echo "Usa '$0 help' para ver comandos disponibles"
            exit 1
            ;;
    esac
}

# Ejecutar función principal
main "$@"
