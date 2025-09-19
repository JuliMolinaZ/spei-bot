# 🏦 Conciliador Bancario - Versión de Producción

Sistema profesional de conciliación bancaria con validación de duplicados e interfaz optimizada.

## 🌟 Características

- ✅ **Validación de Duplicados**: Previene inserción de registros duplicados
- 🔄 **Procesamiento Inteligente**: Maneja archivos BanBajío automáticamente  
- 📊 **Integración Google Sheets**: Inserción directa con rate limiting
- 🎯 **UX Optimizada**: Feedback en tiempo real y progress bars detallados
- 🛡️ **Manejo de Errores**: Retry automático con exponential backoff
- 📈 **Métricas Detalladas**: Contador de insertados vs duplicados

## 🚀 Inicio Rápido

### 1. Configuración

Crea archivo `.env` con tu configuración:

```env
# Google Sheets Configuration
SHEET_ID=tu_google_sheet_id_aqui
SHEET_TAB=Movimientos

# Google Credentials (elige una opción)
GOOGLE_SA_JSON={"type":"service_account",...}
# O
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
```

### 2. Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecución

**Opción 1: Script de Producción (Recomendado)**
```bash
python run_production.py
```

**Opción 2: Streamlit Directo**
```bash
streamlit run app_production_final.py --server.port=8501
```

## 📋 Funcionalidades Principales

### Procesamiento de Archivos
- **Lectura**: Soporte para archivos TXT/CSV de BanBajío
- **Análisis**: Extracción y normalización automática de datos
- **Clasificación**: Identificación automática de tipos de transacciones
- **UIDs**: Generación de identificadores únicos por transacción

### Validación de Duplicados
- **Detección Inteligente**: Compara UIDs contra registros existentes
- **Feedback Visual**: Muestra contadores de insertados vs duplicados
- **Optimización**: Una sola consulta inicial para máximo rendimiento

### Inserción a Google Sheets
- **Rate Limiting**: Previene errores de quota (429)
- **Retry Logic**: Reintento automático con delays exponenciales
- **Progress Tracking**: Seguimiento detallado del progreso
- **Error Handling**: Manejo robusto de errores de conexión

## 🔧 Arquitectura

```
📁 Estructura del Proyecto
├── app_production_final.py     # Aplicación principal
├── run_production.py          # Script de lanzamiento
├── sheets_client.py           # Cliente optimizado Google Sheets
├── bank_parser.py             # Parser de datos bancarios
├── banbajio_reader.py         # Lector específico BanBajío
├── format_adapter.py          # Adaptador de formatos
├── ux_components.py           # Componentes de interfaz
├── config.py                  # Gestión de configuración
├── requirements.txt           # Dependencias
└── .env                       # Variables de entorno
```

## 📊 Flujo de Procesamiento

1. **Upload** → Usuario sube archivos TXT/CSV
2. **Parsing** → Sistema extrae y normaliza datos
3. **Validation** → Genera UIDs y clasifica transacciones  
4. **Duplicate Check** → Compara contra registros existentes
5. **Insertion** → Inserta solo registros nuevos
6. **Feedback** → Muestra métricas detalladas de la operación

## ⚙️ Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Requerido |
|----------|-------------|-----------|
| `SHEET_ID` | ID de Google Sheet destino | ✅ |
| `SHEET_TAB` | Nombre de la pestaña | ❌ (default: Movimientos) |
| `GOOGLE_SA_JSON` | Credenciales JSON inline | ✅* |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path al archivo de credenciales | ✅* |

*Requerido uno de los dos métodos de credenciales

### Permisos de Google Sheets

El service account debe tener permisos:
- `https://www.googleapis.com/auth/spreadsheets`
- `https://www.googleapis.com/auth/drive.file`

## 🛠️ Troubleshooting

### Error 429 (Quota Exceeded)
```
✅ El sistema incluye rate limiting automático
✅ Retry con exponential backoff implementado
```

### Credenciales Inválidas
```
❌ Verifica tu archivo .env
❌ Confirma permisos del service account
❌ Revisa el SHEET_ID
```

### Duplicados No Detectados
```
❌ Verifica que la columna UID esté en posición 9 (índice)
❌ Confirma que el formato de la hoja sea correcto
```

## 📈 Métricas y Monitoreo

La aplicación proporciona métricas detalladas:

- **Por Archivo**: Registros totales, insertados, duplicados, velocidad
- **Globales**: Totales acumulados de toda la sesión
- **Tiempo Real**: Progress bars y tiempos de procesamiento
- **Errores**: Log detallado de cualquier problema

## 🔒 Seguridad

- ✅ Credenciales manejadas via variables de entorno
- ✅ No almacenamiento local de datos sensibles
- ✅ Conexiones HTTPS/TLS únicamente
- ✅ Rate limiting para prevenir abuse

## 📞 Soporte

Para problemas o dudas:
1. Revisa este README
2. Verifica tu configuración `.env`
3. Consulta los logs de error en la aplicación
4. Verifica permisos de Google Sheets

---

**🎉 ¡Listo para Producción!** Este sistema está optimizado para uso profesional con todas las mejores prácticas implementadas.