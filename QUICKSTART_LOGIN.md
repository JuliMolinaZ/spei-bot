# 🚀 Inicio Rápido - Sistema de Login

## ⚡ En 3 Pasos

### 1️⃣ Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2️⃣ Configurar Usuario (Opcional - ya hay uno por defecto)

```bash
# Opción A: Usar credenciales por defecto
# Usuario: admin
# Contraseña: admin123

# Opción B: Crear tu propio usuario
cp users_config.example.py users_config.py
python manage_users.py hash "TuContraseña"
# Edita users_config.py con el hash generado
```

### 3️⃣ Ejecutar la Aplicación

```bash
streamlit run app.py
```

¡Listo! El login aparecerá automáticamente.

---

## 🔑 Credenciales por Defecto

```
Usuario: admin
Contraseña: admin123
```

**⚠️ IMPORTANTE:** Cambia estas credenciales en producción!

---

## 🛠️ Herramientas Útiles

### Generar Hash de Contraseña

```bash
# Método 1: Script directo
python auth.py "MiContraseña123"

# Método 2: Gestor de usuarios
python manage_users.py hash "MiContraseña123"
```

### Listar Usuarios

```bash
python manage_users.py list
```

### Crear Nuevo Usuario

```bash
python manage_users.py add
# Sigue las instrucciones interactivas
```

---

## 🔒 Características de Seguridad

✅ **Autenticación JWT** - Token válido por 1 hora
✅ **Bcrypt Hashing** - Contraseñas encriptadas con 12 rounds
✅ **Rate Limiting** - Máx 5 intentos fallidos antes de bloqueo
✅ **Session Timeout** - Cierre automático después de 1 hora inactiva
✅ **Protected Routes** - Verificación en cada acción

---

## 📱 Cómo Usar la App

1. **Abre la aplicación** en tu navegador (usualmente http://localhost:8501)

2. **Aparece el login automáticamente** - pantalla bonita con gradiente morado

3. **Ingresa credenciales:**
   - Usuario: `admin`
   - Contraseña: `admin123`

4. **¡Accede a la app!** - Verás tu información de sesión en el sidebar

5. **Cerrar sesión** - Botón "🚪 Cerrar Sesión" en el sidebar

---

## ⚠️ Solución de Problemas Rápida

### "Cuenta bloqueada temporalmente"
**Solución:** Espera 5 minutos o reinicia la app

### "Sesión expirada"
**Solución:** Vuelve a iniciar sesión (expira después de 1 hora)

### "ModuleNotFoundError: No module named 'jwt'"
**Solución:**
```bash
pip install PyJWT bcrypt
```

### No puedo ver el login
**Solución:** Limpia la sesión de Streamlit:
```bash
# Presiona 'C' en la terminal
# O reinicia con: streamlit run app.py
```

---

## 📚 Documentación Completa

- **LOGIN_SETUP.md** - Configuración detallada paso a paso
- **SECURITY.md** - Guía completa de seguridad
- **users_config.example.py** - Ejemplo de configuración

---

## 🎯 Próximos Pasos Recomendados

1. ✅ Probar el login con credenciales por defecto
2. 🔒 Cambiar la contraseña de admin
3. 📝 Crear usuarios adicionales si es necesario
4. ⚙️ Configurar JWT_SECRET_KEY en .env
5. 📖 Leer SECURITY.md para mejores prácticas

---

## 💡 Tips Rápidos

```bash
# Ver ayuda del gestor de usuarios
python manage_users.py help

# Verificar una contraseña
python manage_users.py verify

# Ver todos los comandos disponibles
python manage_users.py
```

---

**SPEI BOT v2.0** | Sistema Seguro y Listo para Usar 🚀
