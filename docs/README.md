# 🏦 Conciliador Bancario Pro

Sistema profesional de conciliación de movimientos bancarios con integración a Google Sheets.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [API](#api)
- [Seguridad](#seguridad)
- [Desarrollo](#desarrollo)
- [Troubleshooting](#troubleshooting)

## ✨ Características

### 🎯 Funcionalidades Principales
- **Procesamiento Multi-formato**: Soporta TXT y CSV de diferentes bancos
- **Detección Automática**: Identifica automáticamente el formato BanBajío
- **Deduplicación Inteligente**: Evita duplicados usando UIDs únicos
- **Integración Google Sheets**: Inserción automática y segura
- **Logging Completo**: Auditoría completa de todas las operaciones

### 🚀 Características Avanzadas
- **Modo Demo**: Prueba sin configuración de Google Sheets
- **Procesamiento en Lotes**: Manejo eficiente de grandes volúmenes
- **Cache Inteligente**: Optimización de rendimiento
- **Rate Limiting**: Respeta límites de API de Google
- **Validación de Conflictos**: Detecta inconsistencias en datos

## 🏗️ Arquitectura

```
conciliador/
├── src/                    # Código fuente principal
│   ├── core/              # Lógica de negocio
│   │   ├── parser.py     # Parser de archivos bancarios
│   │   ├── reader.py     # Lector inteligente de archivos
│   │   ├── processor.py  # Procesador principal
│   │   └── formatter.py  # Formateador de datos
│   ├── services/         # Servicios externos
│   │   └── google_sheets.py  # Integración con Google Sheets
│   ├── ui/               # Interfaz de usuario
│   │   ├── app.py        # Aplicación Streamlit principal
│   │   └── components.py # Componentes UI reutilizables
│   ├── utils/            # Utilidades
│   │   └── helpers.py    # Funciones helper
│   └── config/           # Configuración
│       └── settings.py   # Manejo de configuración
├── tests/                 # Pruebas
│   ├── unit/             # Pruebas unitarias
│   └── integration/       # Pruebas de integración
├── docs/                 # Documentación
├── logs/                 # Archivos de log
├── main.py              # Punto de entrada principal
├── requirements.txt     # Dependencias
└── Dockerfile          # Configuración Docker
```

### 🔧 Componentes Principales

#### Core (Lógica de Negocio)
- **BankParser**: Normaliza y parsea archivos bancarios
- **BankReader**: Lee archivos de diferentes formatos
- **BankProcessor**: Orquesta el procesamiento completo
- **DataFormatter**: Formatea datos para Google Sheets

#### Services (Servicios Externos)
- **GoogleSheetsService**: Maneja toda la integración con Google Sheets

#### UI (Interfaz de Usuario)
- **ConciliadorApp**: Aplicación principal de Streamlit
- **UIComponents**: Componentes reutilizables

## 🚀 Instalación

### Requisitos Previos
- Python 3.10+
- Cuenta de Google con acceso a Google Sheets
- Service Account de Google con permisos de Sheets

### Instalación Rápida

```bash
# Clonar el repositorio
git clone <tu-repo>
cd conciliador

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

### Instalación con Docker

```bash
# Construir imagen
docker build -t conciliador .

# Ejecutar contenedor
docker run -p 8501:8501 --env-file .env conciliador
```

## ⚙️ Configuración

### Variables de Entorno Principales

```bash
# Configuración básica
SHEET_ID=tu_sheet_id_aqui
SHEET_TAB=Movimientos_Nuevos

# Credenciales Google
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

1. **Crear Service Account**:
   - Ir a [Google Cloud Console](https://console.cloud.google.com/)
   - Crear nuevo proyecto o seleccionar existente
   - Habilitar Google Sheets API
   - Crear Service Account
   - Descargar JSON de credenciales

2. **Compartir Hoja**:
   - Abrir tu hoja de Google Sheets
   - Compartir con el email del Service Account
   - Dar permisos de Editor

3. **Configurar Variables**:
   - Copiar JSON de credenciales a `GOOGLE_SA_JSON`
   - O guardar archivo y configurar `GOOGLE_APPLICATION_CREDENTIALS`

## 📖 Uso

### Interfaz Web

1. **Iniciar Aplicación**:
   ```bash
   python main.py
   ```

2. **Acceder a la Interfaz**:
   - Abrir navegador en `http://localhost:8501`

3. **Procesar Archivos**:
   - Ir a pestaña "📁 Cargar Archivos"
   - Seleccionar archivos bancarios
   - Hacer clic en "🔍 Analizar Archivos"
   - Revisar resultados en "🔍 Procesar Datos"
   - Insertar en "📊 Insertar a Sheets"

### Modo Demo

Para probar sin configurar Google Sheets:

```bash
# Activar modo demo
export DEMO_MODE=true
python main.py
```

### Línea de Comandos

```bash
# Procesar archivo específico
python -m src.core.processor archivo.txt

# Verificar configuración
python -m src.config.settings
```

## 🔒 Seguridad

### Mejores Prácticas Implementadas

1. **Manejo Seguro de Credenciales**:
   - Variables de entorno para credenciales
   - No hardcoding de passwords
   - Rotación de credenciales

2. **Validación de Datos**:
   - Sanitización de inputs
   - Validación de tipos de archivo
   - Límites de tamaño de archivo

3. **Logging y Auditoría**:
   - Logs detallados de todas las operaciones
   - Trazabilidad completa
   - Detección de anomalías

4. **Rate Limiting**:
   - Respeta límites de API de Google
   - Prevención de abuso
   - Manejo de errores graceful

### Configuración de Seguridad

```bash
# Configuraciones de seguridad recomendadas
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

# Pruebas unitarias
pytest tests/unit/

# Pruebas de integración
pytest tests/integration/

# Con cobertura
pytest --cov=src --cov-report=html
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

### Contribuir

1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 🔧 Troubleshooting

### Problemas Comunes

#### Error de Credenciales
```
Error: No se encontraron credenciales de Google
```
**Solución**: Verificar que `GOOGLE_SA_JSON` o `GOOGLE_APPLICATION_CREDENTIALS` estén configurados correctamente.

#### Error de Permisos
```
Error: [403] Google Drive API has not been used
```
**Solución**: Habilitar Google Sheets API en Google Cloud Console.

#### Archivo Ya Importado
```
Warning: Archivo ya fue importado anteriormente
```
**Solución**: El sistema detecta automáticamente archivos duplicados. Revisar logs de importación.

#### Problemas de Rendimiento
```
Warning: Procesamiento lento
```
**Solución**: 
- Reducir `BATCH_SIZE` en configuración
- Deshabilitar `ENABLE_CACHE` si hay problemas de memoria
- Verificar conexión a internet

### Logs y Debugging

```bash
# Ver logs en tiempo real
tail -f logs/app.log

# Debug mode
export LOG_LEVEL=DEBUG
python main.py
```

### Soporte

- 📧 Email: soporte@tu-dominio.com
- 🐛 Issues: [GitHub Issues](https://github.com/tu-repo/issues)
- 📖 Wiki: [Documentación Completa](https://github.com/tu-repo/wiki)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- Equipo de desarrollo por las contribuciones
- Comunidad de Streamlit por el framework
- Google por las APIs de Sheets

---

**Hecho con ❤️ para procesos bancarios profesionales, seguros y escalables.**
