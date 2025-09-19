# 🏦 Conciliador Bancario Pro

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36.0-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](Dockerfile)

Sistema profesional de conciliación de movimientos bancarios con integración automática a Google Sheets. Diseñado para ser rápido, seguro y escalable.

## ✨ Características Principales

- 🚀 **Procesamiento Rápido**: Maneja miles de registros en segundos
- 🔒 **Seguridad Avanzada**: Validación exhaustiva y manejo seguro de credenciales
- 📊 **Integración Google Sheets**: Inserción automática y sincronización
- 🎯 **Detección Inteligente**: Identifica automáticamente formatos bancarios
- 🔄 **Deduplicación**: Evita duplicados usando UIDs únicos
- 📝 **Auditoría Completa**: Logs detallados de todas las operaciones
- 🧪 **Modo Demo**: Prueba sin configuración de Google Sheets

## 🏗️ Arquitectura Profesional

```
conciliador/
├── src/                    # Código fuente modular
│   ├── core/              # Lógica de negocio
│   ├── services/          # Servicios externos
│   ├── ui/               # Interfaz de usuario
│   ├── utils/             # Utilidades
│   └── config/            # Configuración
├── tests/                 # Suite de pruebas
├── docs/                  # Documentación completa
├── scripts/               # Scripts de automatización
├── logs/                  # Archivos de log
└── main.py               # Punto de entrada
```

## 🚀 Inicio Rápido

### Opción 1: Script Automatizado (Recomendado)

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/conciliador-bancario.git
cd conciliador-bancario

# Ejecutar script de inicio
./scripts/start.sh
```

### Opción 2: Instalación Manual

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp env.example .env
# Editar .env con tus configuraciones

# Ejecutar aplicación
python main.py
```

### Opción 3: Docker

```bash
# Construir y ejecutar
docker-compose up --build

# O solo desarrollo
docker-compose --profile dev up
```

## ⚙️ Configuración

### Variables de Entorno Principales

```bash
# Configuración básica
SHEET_ID=tu_sheet_id_aqui
SHEET_TAB=Movimientos_Nuevos

# Credenciales Google (una de las dos opciones)
GOOGLE_SA_JSON={"type":"service_account",...}
# O
GOOGLE_APPLICATION_CREDENTIALS=/ruta/a/credenciales.json

# Configuración avanzada
BATCH_SIZE=1000
ENABLE_CACHE=true
LOG_IMPORTS=true
DEMO_MODE=false
```

### Configuración de Google Sheets

1. **Crear Service Account** en [Google Cloud Console](https://console.cloud.google.com/)
2. **Habilitar Google Sheets API**
3. **Descargar JSON de credenciales**
4. **Compartir tu hoja** con el email del Service Account
5. **Configurar variables** en `.env`

## 📖 Uso

### Interfaz Web

1. Ejecutar: `python main.py`
2. Abrir: `http://localhost:8501`
3. Seguir el flujo de 3 pasos:
   - 📁 **Cargar Archivos**: Seleccionar archivos bancarios
   - 🔍 **Procesar Datos**: Revisar análisis y resultados
   - 📊 **Insertar a Sheets**: Confirmar inserción a Google Sheets

### Modo Demo

```bash
# Activar modo demo
export DEMO_MODE=true
python main.py
```

### Línea de Comandos

```bash
# Verificar configuración
./scripts/start.sh check

# Solo instalar dependencias
./scripts/start.sh install

# Limpiar procesos
./scripts/start.sh clean
```

## 🔒 Seguridad

### Mejores Prácticas Implementadas

- ✅ **Credenciales Seguras**: Variables de entorno, no hardcoding
- ✅ **Validación de Datos**: Sanitización y límites de archivos
- ✅ **Logging Detallado**: Auditoría completa de operaciones
- ✅ **Rate Limiting**: Respeta límites de API de Google
- ✅ **Usuario No-Root**: Ejecución segura en Docker
- ✅ **Health Checks**: Monitoreo de estado de aplicación

### Configuración de Seguridad

```bash
# Configuraciones recomendadas para producción
MAX_FILE_SIZE=200          # MB
RATE_LIMIT=100             # requests/minuto
LOG_LEVEL=INFO            # Para producción
DEMO_MODE=false           # Para producción
```

## 🧪 Desarrollo

### Estructura de Pruebas

```bash
# Ejecutar todas las pruebas
pytest

# Pruebas con cobertura
pytest --cov=src --cov-report=html

# Pruebas específicas
pytest tests/unit/
pytest tests/integration/
```

### Estándares de Código

```bash
# Formatear código
black src/

# Linting
flake8 src/

# Type checking
mypy src/
```

### Docker para Desarrollo

```bash
# Desarrollo con hot-reload
docker-compose --profile dev up

# Construir imagen
docker build -t conciliador .

# Ejecutar contenedor
docker run -p 8501:8501 --env-file .env conciliador
```

## 📊 Monitoreo y Logs

### Ver Logs en Tiempo Real

```bash
# Logs de aplicación
tail -f logs/app.log

# Logs de Docker
docker-compose logs -f conciliador
```

### Health Checks

```bash
# Verificar estado de aplicación
curl http://localhost:8501/_stcore/health

# Verificar contenedor Docker
docker-compose ps
```

## 🔧 Troubleshooting

### Problemas Comunes

| Problema | Solución |
|----------|----------|
| Error de credenciales | Verificar `GOOGLE_SA_JSON` o `GOOGLE_APPLICATION_CREDENTIALS` |
| API no habilitada | Habilitar Google Sheets API en Google Cloud Console |
| Puerto ocupado | Usar `./scripts/start.sh clean` o cambiar puerto |
| Archivo ya importado | Sistema detecta duplicados automáticamente |
| Rendimiento lento | Reducir `BATCH_SIZE` o deshabilitar `ENABLE_CACHE` |

### Debug Mode

```bash
# Activar debug
export LOG_LEVEL=DEBUG
python main.py
```

## 📚 Documentación Completa

- 📖 [Documentación Detallada](docs/README.md)
- 🐳 [Guía Docker](docs/DOCKER.md)
- 🔒 [Guía de Seguridad](docs/SECURITY.md)
- 🧪 [Guía de Testing](docs/TESTING.md)
- 🚀 [Guía de Despliegue](docs/DEPLOYMENT.md)

## 🤝 Contribuir

1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Estándares de Contribución

- Seguir PEP 8 para Python
- Escribir tests para nuevas funcionalidades
- Documentar cambios importantes
- Usar commits semánticos

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- Equipo de desarrollo por las contribuciones
- Comunidad de Streamlit por el framework
- Google por las APIs de Sheets
- Comunidad Python por las librerías

## 📞 Soporte

- 🐛 **Issues**: [GitHub Issues](https://github.com/tu-usuario/conciliador-bancario/issues)
- 💬 **Discusiones**: [GitHub Discussions](https://github.com/tu-usuario/conciliador-bancario/discussions)
- 📖 **Documentación**: [Docs Completa](docs/INDEX.md)

---

<div align="center">

**Hecho con ❤️ para procesos bancarios profesionales, seguros y escalables.**

[![Star](https://img.shields.io/github/stars/tu-usuario/conciliador-bancario?style=social)](https://github.com/tu-usuario/conciliador-bancario)
[![Fork](https://img.shields.io/github/forks/tu-usuario/conciliador-bancario?style=social)](https://github.com/tu-usuario/conciliador-bancario/fork)

</div>