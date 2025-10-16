# 📊 Guía Completa: Conectar SPEI BOT a tu Hoja de Google Sheets

Esta guía te llevará paso a paso para conectar permanentemente el SPEI BOT a tu hoja de Google Sheets real.

---

## 📋 Índice

1. [Preparar tu Hoja de Google Sheets](#1-preparar-tu-hoja-de-google-sheets)
2. [Crear Proyecto en Google Cloud](#2-crear-proyecto-en-google-cloud)
3. [Habilitar APIs Necesarias](#3-habilitar-apis-necesarias)
4. [Crear Service Account (Cuenta de Servicio)](#4-crear-service-account)
5. [Descargar Credenciales](#5-descargar-credenciales)
6. [Compartir la Hoja con el Bot](#6-compartir-la-hoja-con-el-bot)
7. [Configurar la Aplicación](#7-configurar-la-aplicación)
8. [Verificar la Conexión](#8-verificar-la-conexión)
9. [Solución de Problemas](#9-solución-de-problemas)

---

## 1. Preparar tu Hoja de Google Sheets

### Paso 1.1: Crear o Preparar tu Hoja

1. **Ve a [Google Sheets](https://sheets.google.com)**
2. **Crea una nueva hoja** o abre la hoja existente que quieres usar
3. **Anota el ID de tu hoja** (lo encontrarás en la URL):

```
https://docs.google.com/spreadsheets/d/[ESTE_ES_TU_SHEET_ID]/edit
```

**Ejemplo:**
```
URL: https://docs.google.com/spreadsheets/d/1a2b3c4d5e6f7g8h9i0j/edit
SHEET_ID: 1a2b3c4d5e6f7g8h9i0j
```

### Paso 1.2: Configurar las Pestañas Necesarias

Tu hoja debe tener una pestaña llamada **`Movimientos_Nuevos`** (o el nombre que prefieras) con los siguientes headers en la fila 1:

| A | B | C | D | E | F | G | H | I | J | K | L | M |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Prueba | de | escritura | 2025-07-17T18:32:23.744Z | Hora | Clave | Descripción | Egreso | Ingreso | Autorizado | Capturado | Notas | __PowerAppsId__ |

**⚠️ Importante:** Los headers deben estar exactamente en la fila 1.

---

## 2. Crear Proyecto en Google Cloud

### Paso 2.1: Acceder a Google Cloud Console

1. **Ve a [Google Cloud Console](https://console.cloud.google.com)**
2. **Inicia sesión** con tu cuenta de Google

### Paso 2.2: Crear un Nuevo Proyecto

1. **Haz clic** en el selector de proyectos (parte superior)
2. **Haz clic** en "Nuevo proyecto"
3. **Nombre del proyecto:** `spei-bot` (o el que prefieras)
4. **Ubicación:** Dejar por defecto
5. **Haz clic** en "Crear"

**✅ Espera** unos segundos mientras se crea el proyecto

---

## 3. Habilitar APIs Necesarias

### Paso 3.1: Habilitar Google Sheets API

1. **Ve al menú** ☰ → "APIs y servicios" → "Biblioteca"
2. **Busca:** "Google Sheets API"
3. **Haz clic** en "Google Sheets API"
4. **Haz clic** en "Habilitar"

### Paso 3.2: Habilitar Google Drive API (Opcional pero recomendado)

1. **Regresa a la Biblioteca**
2. **Busca:** "Google Drive API"
3. **Haz clic** en "Google Drive API"
4. **Haz clic** en "Habilitar"

**✅ Ambas APIs** deben estar habilitadas

---

## 4. Crear Service Account (Cuenta de Servicio)

### Paso 4.1: Ir a Cuentas de Servicio

1. **Ve al menú** ☰ → "APIs y servicios" → "Credenciales"
2. **Haz clic** en "+ CREAR CREDENCIALES"
3. **Selecciona:** "Cuenta de servicio"

### Paso 4.2: Configurar la Cuenta de Servicio

**Paso 1 - Detalles de la cuenta de servicio:**
- **Nombre:** `spei-bot-service`
- **ID:** Se generará automáticamente
- **Descripción:** `Service account para SPEI BOT`
- **Haz clic** en "CREAR Y CONTINUAR"

**Paso 2 - Conceder acceso (Opcional):**
- **Puedes omitir** este paso
- **Haz clic** en "CONTINUAR"

**Paso 3 - Conceder acceso a usuarios (Opcional):**
- **Puedes omitir** este paso
- **Haz clic** en "LISTO"

**✅ La cuenta de servicio** está creada

---

## 5. Descargar Credenciales

### Paso 5.1: Crear Clave JSON

1. **En la lista de cuentas de servicio**, encuentra la que acabas de crear
2. **Haz clic** en el nombre de la cuenta (`spei-bot-service@...`)
3. **Ve a la pestaña** "CLAVES"
4. **Haz clic** en "AGREGAR CLAVE" → "Crear clave nueva"
5. **Selecciona** tipo "JSON"
6. **Haz clic** en "CREAR"

**✅ Se descargará** un archivo JSON con las credenciales

**Ejemplo del nombre:** `spei-bot-xxxxx.json`

### Paso 5.2: Copiar el Email del Service Account

**⚠️ MUY IMPORTANTE:** Antes de cerrar, copia el email del service account:

```
spei-bot-service@tu-proyecto-123456.iam.gserviceaccount.com
```

**Lo necesitarás en el siguiente paso**

---

## 6. Compartir la Hoja con el Bot

### Paso 6.1: Compartir tu Google Sheet

1. **Abre tu hoja** de Google Sheets
2. **Haz clic** en el botón "Compartir" (esquina superior derecha)
3. **Pega el email** del service account que copiaste:
   ```
   spei-bot-service@tu-proyecto-123456.iam.gserviceaccount.com
   ```
4. **Rol:** Selecciona "Editor" (el bot necesita poder escribir)
5. **Desmarca** "Notificar a las personas" (es un bot, no necesita notificación)
6. **Haz clic** en "Compartir"

**✅ Tu hoja ahora** es accesible para el bot

---

## 7. Configurar la Aplicación

### Paso 7.1: Guardar el Archivo de Credenciales

1. **Copia el archivo JSON** descargado al directorio del proyecto:
   ```bash
   cp ~/Downloads/spei-bot-xxxxx.json /Users/julianmolina/Documents/RUN/conciliador/
   ```

2. **Renómbralo** (opcional, para mayor claridad):
   ```bash
   mv spei-bot-xxxxx.json spei-bot-credentials.json
   ```

### Paso 7.2: Crear Archivo .env

1. **Copia el archivo de ejemplo:**
   ```bash
   cd /Users/julianmolina/Documents/RUN/conciliador
   cp env.example .env
   ```

2. **Edita el archivo .env:**
   ```bash
   nano .env
   ```

### Paso 7.3: Configurar las Variables

**Edita el archivo .env** con tus valores reales:

```env
# ===========================================
# CONFIGURACIÓN BÁSICA
# ===========================================

# ID de tu hoja de Google Sheets (copiado del paso 1)
SHEET_ID=1a2b3c4d5e6f7g8h9i0j

# Nombre de la pestaña donde se insertarán los datos
SHEET_TAB=Movimientos_Nuevos

# ===========================================
# CREDENCIALES DE GOOGLE
# ===========================================

# Opción recomendada: Ruta al archivo de credenciales
GOOGLE_APPLICATION_CREDENTIALS=/Users/julianmolina/Documents/RUN/conciliador/spei-bot-credentials.json

# ===========================================
# CONFIGURACIÓN AVANZADA (Opcional)
# ===========================================

BATCH_SIZE=1000
ENABLE_CACHE=true
LOG_IMPORTS=true
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
DEMO_MODE=false
MAX_FILE_SIZE=200
CACHE_TTL=300
RATE_LIMIT=100
```

**Guarda** el archivo (Ctrl + O, Enter, Ctrl + X en nano)

### Paso 7.4: Proteger tus Credenciales

**⚠️ SEGURIDAD:** Verifica que el `.gitignore` esté configurado correctamente:

```bash
cat .gitignore | grep -E '\.env|\.json'
```

**Deberías ver:**
```
.env
*.json
```

**✅ Tus credenciales** NO se subirán a Git

---

## 8. Verificar la Conexión

### Paso 8.1: Probar la Conexión

**Ejecuta la aplicación:**

```bash
source venv/bin/activate
streamlit run main.py
```

### Paso 8.2: Verificar en los Logs

**Deberías ver mensajes como:**

```
✅ Credenciales cargadas desde /path/to/spei-bot-credentials.json
✅ Conexión a Google Sheets verificada
✅ Sheet 'Tu Nombre de Hoja' accedido correctamente
✅ Tab 'Movimientos_Nuevos' encontrado
```

### Paso 8.3: Realizar una Prueba

1. **Sube un archivo** de movimientos bancarios
2. **Procesa los datos**
3. **Inserta en la hoja**
4. **Verifica** en tu Google Sheet que los datos aparecen correctamente

**✅ Si los datos aparecen,** la conexión es exitosa

---

## 9. Solución de Problemas

### ❌ Error: "SHEET_ID no está configurado"

**Solución:**
- Verifica que el archivo `.env` existe en la raíz del proyecto
- Verifica que `SHEET_ID=...` está configurado correctamente

### ❌ Error: "No se puede acceder al sheet"

**Solución:**
- Verifica que el SHEET_ID es correcto
- Verifica que compartiste la hoja con el email del service account
- Verifica que el rol es "Editor"

### ❌ Error: "Credenciales no encontradas"

**Solución:**
- Verifica la ruta en `GOOGLE_APPLICATION_CREDENTIALS`
- Verifica que el archivo JSON existe en esa ubicación
- Usa rutas absolutas, no relativas

### ❌ Error: "Drive API disabled"

**Solución:**
- Este es un warning, no un error crítico
- La aplicación funcionará correctamente
- Si quieres eliminarlo, habilita Google Drive API (Paso 3.2)

### ❌ Error: "Quota exceeded"

**Solución:**
- La aplicación tiene rate limiting automático
- Espera unos minutos y reintenta
- Reduce el `BATCH_SIZE` en .env si persiste

### ❌ Error: "Permission denied" o "Protected cell"

**Solución:**
- Verifica que el service account tiene rol "Editor"
- Verifica que no hay celdas/rangos protegidos en tu hoja
- Si hay protecciones, quítalas o ajusta los permisos

---

## 📝 Resumen de Archivos Importantes

```
conciliador/
├── .env                              ← Configuración (NO subir a Git)
├── spei-bot-credentials.json         ← Credenciales (NO subir a Git)
├── env.example                       ← Plantilla de configuración
├── main.py                           ← Punto de entrada
└── src/
    ├── config/settings.py            ← Lee .env
    └── services/google_sheets.py     ← Cliente de Sheets
```

---

## 🔐 Checklist de Seguridad

- ✅ Archivo `.env` en `.gitignore`
- ✅ Archivo `*.json` en `.gitignore`
- ✅ Credenciales JSON no subidas a Git
- ✅ Service account con permisos mínimos necesarios
- ✅ Hoja compartida solo con el service account

---

## 🎉 ¡Listo!

Tu SPEI BOT ahora está permanentemente conectado a tu hoja de Google Sheets real.

**Cada vez que ejecutes la aplicación:**
1. Se conectará automáticamente a tu hoja
2. Validará duplicados contra los datos existentes
3. Insertará solo registros nuevos
4. Mantendrá un log de todas las operaciones

---

## 📚 Referencias Útiles

- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Service Accounts Overview](https://cloud.google.com/iam/docs/service-accounts)
- [gspread Documentation](https://docs.gspread.org/)

---

**¿Tienes problemas?** Revisa la sección de [Solución de Problemas](#9-solución-de-problemas) o consulta los logs en `logs/app.log`

