#!/bin/bash

# Script de Despliegue Automatizado para SPEI Bot
# Dominio: spei.runsolutions-services.com
# Puerto: 8501

set -e  # Salir si cualquier comando falla

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
PROJECT_NAME="spei-bot"
PROJECT_DIR="/opt/spei-bot"
DOMAIN="spei.runsolutions-services.com"
PORT="8501"
CONTAINER_NAME="spei-bot-container"

# Función para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

# Función para verificar si el puerto está en uso
check_port() {
    if netstat -tlnp | grep -q ":$PORT "; then
        warning "Puerto $PORT está en uso. Verificando procesos..."
        netstat -tlnp | grep ":$PORT "
        return 1
    fi
    return 0
}

# Función para verificar si el contenedor existe
check_container() {
    if docker ps -a --format "table {{.Names}}" | grep -q "^$CONTAINER_NAME$"; then
        return 0
    fi
    return 1
}

# Función para detener contenedor existente
stop_container() {
    if check_container; then
        log "Deteniendo contenedor existente: $CONTAINER_NAME"
        docker stop $CONTAINER_NAME || true
        docker rm $CONTAINER_NAME || true
        success "Contenedor detenido y eliminado"
    fi
}

# Función para construir la imagen Docker
build_image() {
    log "Construyendo imagen Docker para $PROJECT_NAME..."
    cd $PROJECT_DIR
    
    # Verificar que existe Dockerfile
    if [ ! -f "Dockerfile" ]; then
        error "No se encontró Dockerfile en $PROJECT_DIR"
        exit 1
    fi
    
    # Construir imagen
    docker build -t $PROJECT_NAME:latest .
    success "Imagen Docker construida exitosamente"
}

# Función para ejecutar el contenedor
run_container() {
    log "Ejecutando contenedor $CONTAINER_NAME..."
    
    # Verificar que el puerto esté libre
    if ! check_port; then
        error "Puerto $PORT está en uso. No se puede desplegar."
        exit 1
    fi
    
    # Crear directorios necesarios
    mkdir -p $PROJECT_DIR/logs
    mkdir -p $PROJECT_DIR/data
    
    # Ejecutar contenedor
    docker run -d \
        --name $CONTAINER_NAME \
        --restart unless-stopped \
        -p $PORT:8501 \
        -v $PROJECT_DIR/logs:/app/logs \
        -v $PROJECT_DIR/data:/app/data \
        -e STREAMLIT_SERVER_PORT=8501 \
        -e STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
        -e STREAMLIT_SERVER_HEADLESS=true \
        $PROJECT_NAME:latest
    
    success "Contenedor ejecutado exitosamente"
}

# Función para verificar el estado del contenedor
check_container_health() {
    log "Verificando salud del contenedor..."
    
    # Esperar a que el contenedor esté listo
    sleep 10
    
    # Verificar que el contenedor esté corriendo
    if ! docker ps --format "table {{.Names}}" | grep -q "^$CONTAINER_NAME$"; then
        error "El contenedor no está corriendo"
        docker logs $CONTAINER_NAME
        exit 1
    fi
    
    # Verificar que el puerto esté disponible
    if ! netstat -tlnp | grep -q ":$PORT "; then
        error "El puerto $PORT no está disponible"
        docker logs $CONTAINER_NAME
        exit 1
    fi
    
    # Verificar health check
    if curl -f http://localhost:$PORT/_stcore/health > /dev/null 2>&1; then
        success "Health check exitoso"
    else
        warning "Health check falló, pero el contenedor está corriendo"
    fi
}

# Función para configurar SSL
setup_ssl() {
    log "Configurando certificado SSL para $DOMAIN..."
    
    # Verificar que certbot esté instalado
    if ! command -v certbot &> /dev/null; then
        error "Certbot no está instalado. Instalando..."
        sudo apt update
        sudo apt install -y certbot python3-certbot-nginx
    fi
    
    # Obtener certificado SSL
    sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@runsolutions-services.com
    
    if [ $? -eq 0 ]; then
        success "Certificado SSL configurado exitosamente"
    else
        error "Error al configurar certificado SSL"
        exit 1
    fi
}

# Función para recargar Nginx
reload_nginx() {
    log "Recargando configuración de Nginx..."
    sudo nginx -t
    if [ $? -eq 0 ]; then
        sudo systemctl reload nginx
        success "Nginx recargado exitosamente"
    else
        error "Error en la configuración de Nginx"
        exit 1
    fi
}

# Función para mostrar estado del despliegue
show_status() {
    log "Estado del despliegue:"
    echo "=================================="
    echo "Proyecto: $PROJECT_NAME"
    echo "Dominio: $DOMAIN"
    echo "Puerto: $PORT"
    echo "Contenedor: $CONTAINER_NAME"
    echo "=================================="
    
    # Estado del contenedor
    if check_container; then
        echo -e "Contenedor: ${GREEN}✅ Corriendo${NC}"
        docker ps --filter name=$CONTAINER_NAME --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        echo -e "Contenedor: ${RED}❌ No encontrado${NC}"
    fi
    
    # Estado del puerto
    if netstat -tlnp | grep -q ":$PORT "; then
        echo -e "Puerto $PORT: ${GREEN}✅ En uso${NC}"
    else
        echo -e "Puerto $PORT: ${RED}❌ Libre${NC}"
    fi
    
    # Estado de Nginx
    if sudo systemctl is-active --quiet nginx; then
        echo -e "Nginx: ${GREEN}✅ Activo${NC}"
    else
        echo -e "Nginx: ${RED}❌ Inactivo${NC}"
    fi
    
    # Estado del SSL
    if sudo certbot certificates | grep -q $DOMAIN; then
        echo -e "SSL: ${GREEN}✅ Configurado${NC}"
    else
        echo -e "SSL: ${YELLOW}⚠️ No configurado${NC}"
    fi
    
    echo "=================================="
    echo "URL: http://$DOMAIN"
    echo "Health Check: http://$DOMAIN/health"
}

# Función principal
main() {
    log "Iniciando despliegue de $PROJECT_NAME..."
    
    # Verificar que estamos en el directorio correcto
    if [ ! -d "$PROJECT_DIR" ]; then
        error "Directorio del proyecto no encontrado: $PROJECT_DIR"
        exit 1
    fi
    
    # Detener contenedor existente si existe
    stop_container
    
    # Construir imagen
    build_image
    
    # Ejecutar contenedor
    run_container
    
    # Verificar salud
    check_container_health
    
    # Recargar Nginx
    reload_nginx
    
    # Mostrar estado
    show_status
    
    success "Despliegue completado exitosamente!"
    log "El servicio estará disponible en: http://$DOMAIN"
    log "Para configurar SSL, ejecuta: sudo certbot --nginx -d $DOMAIN"
}

# Función de ayuda
show_help() {
    echo "Script de Despliegue Automatizado para SPEI Bot"
    echo ""
    echo "Uso: $0 [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  deploy     Desplegar la aplicación (por defecto)"
    echo "  stop       Detener el contenedor"
    echo "  restart    Reiniciar el contenedor"
    echo "  status     Mostrar estado del despliegue"
    echo "  ssl        Configurar certificado SSL"
    echo "  logs       Mostrar logs del contenedor"
    echo "  help       Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 deploy"
    echo "  $0 status"
    echo "  $0 ssl"
}

# Manejo de argumentos
case "${1:-deploy}" in
    deploy)
        main
        ;;
    stop)
        log "Deteniendo $PROJECT_NAME..."
        stop_container
        success "Aplicación detenida"
        ;;
    restart)
        log "Reiniciando $PROJECT_NAME..."
        stop_container
        main
        ;;
    status)
        show_status
        ;;
    ssl)
        setup_ssl
        ;;
    logs)
        docker logs -f $CONTAINER_NAME
        ;;
    help)
        show_help
        ;;
    *)
        error "Opción desconocida: $1"
        show_help
        exit 1
        ;;
esac
