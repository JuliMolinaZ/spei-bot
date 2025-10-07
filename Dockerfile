# Dockerfile Profesional para Conciliador Bancario
FROM python:3.11-slim

# Metadatos
LABEL maintainer="Equipo de Desarrollo <dev@tu-dominio.com>"
LABEL version="2.0.0"
LABEL description="Sistema profesional de conciliación bancaria con Google Sheets"

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Crear usuario no-root para seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY src/ ./src/
COPY main.py .
COPY sheets_client.py .
COPY users_config.py .
COPY .env .
COPY .env.example .
COPY spei-bot-b202259d87e7.json .
COPY .streamlit/ ./.streamlit/

# Crear directorios necesarios
RUN mkdir -p logs && \
    mkdir -p data && \
    chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Comando por defecto
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]