# 🚀 Inicio Rápido - Conectar a Google Sheets

## Resumen en 5 Pasos

### 1️⃣ Crear Service Account en Google Cloud
```
1. Ve a: https://console.cloud.google.com
2. Crear proyecto → "spei-bot"
3. APIs y servicios → Biblioteca → Habilitar "Google Sheets API"
4. Credenciales → Crear credenciales → Cuenta de servicio
5. Descargar clave JSON
```

**📋 IMPORTANTE:** Copia el email del service account:
```
spei-bot-service@tu-proyecto-xxxxx.iam.gserviceaccount.com
```

---

### 2️⃣ Compartir tu Hoja de Google Sheets

```
1. Abre tu hoja en Google Sheets
2. Clic en "Compartir"
3. Pegar el email del service account
4. Rol: "Editor"
5. Compartir
```

---

### 3️⃣ Obtener el ID de tu Hoja

**De la URL de tu Google Sheet:**
```
https://docs.google.com/spreadsheets/d/[AQUI_ESTA_EL_ID]/edit
```

**Ejemplo:**
```
URL: https://docs.google.com/spreadsheets/d/1a2b3c4d5e6f7g8h9i0j/edit
ID:  1a2b3c4d5e6f7g8h9i0j
```

---

### 4️⃣ Configurar el Proyecto

**Guarda las credenciales:**
```bash
# Copia el archivo JSON descargado al proyecto
cp ~/Downloads/spei-bot-xxxxx.json /Users/julianmolina/Documents/RUN/conciliador/spei-bot-credentials.json
```

**Crea el archivo .env:**
```bash
cd /Users/julianmolina/Documents/RUN/conciliador
cp env.example .env
nano .env
```

**Edita .env con tus datos:**
```env
# ID de tu hoja (del paso 3)
SHEET_ID=1a2b3c4d5e6f7g8h9i0j

# Nombre de la pestaña
SHEET_TAB=Movimientos_Nuevos

# Ruta a las credenciales (del paso 4)
GOOGLE_APPLICATION_CREDENTIALS=/Users/julianmolina/Documents/RUN/conciliador/spei-bot-credentials.json
```

---

### 5️⃣ Probar la Conexión

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar la aplicación
streamlit run main.py
```

**✅ Deberías ver:**
```
✅ Credenciales cargadas desde ...
✅ Conexión a Google Sheets verificada
✅ Sheet '...' accedido correctamente
```

---

## ❌ Problemas Comunes

| Error | Solución |
|-------|----------|
| "No se puede acceder al sheet" | Verifica que compartiste la hoja con el email del service account |
| "SHEET_ID no configurado" | Verifica que el archivo `.env` existe y tiene `SHEET_ID=...` |
| "Credenciales no encontradas" | Verifica la ruta en `GOOGLE_APPLICATION_CREDENTIALS` |
| "Permission denied" | El service account necesita rol "Editor", no "Viewer" |

---

## 📚 Documentación Completa

Para instrucciones detalladas, consulta:
```
docs/CONFIGURACION_GOOGLE_SHEETS.md
```

---

## 🔐 Seguridad

**⚠️ NUNCA subas a Git:**
- ❌ `.env`
- ❌ `spei-bot-credentials.json`
- ❌ Cualquier archivo con credenciales

**✅ Ya están protegidos en `.gitignore`**

---

## ✅ Checklist

- [ ] Service Account creado en Google Cloud
- [ ] Google Sheets API habilitada
- [ ] Credenciales JSON descargadas
- [ ] Email del service account copiado
- [ ] Hoja de Google Sheets compartida con el bot (rol Editor)
- [ ] SHEET_ID obtenido de la URL
- [ ] Archivo `.env` creado y configurado
- [ ] Credenciales JSON guardadas en el proyecto
- [ ] Conexión probada exitosamente

---

**¡Listo!** 🎉 Tu SPEI BOT está conectado a tu hoja de Google Sheets.

