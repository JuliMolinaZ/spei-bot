# 🔐 Seguridad - SPEI BOT

## Resumen de Seguridad

SPEI BOT implementa un sistema de autenticación robusto y seguro con las siguientes características:

### ✅ Características Implementadas

| Característica | Estado | Descripción |
|---------------|--------|-------------|
| 🔒 JWT Authentication | ✅ | Tokens seguros con expiración de 1 hora |
| 🔑 Password Hashing | ✅ | Bcrypt con 12 rounds de salt |
| 🚫 Rate Limiting | ✅ | Máx 5 intentos en 5 minutos |
| ⏱️ Session Timeout | ✅ | Expiración automática por inactividad |
| 🛡️ Protected Routes | ✅ | Verificación en cada request |
| 📝 Audit Logging | ✅ | Logs de intentos de login |
| 🎨 Modern UI | ✅ | Interface profesional y amigable |

---

## 🚀 Inicio Rápido

### 1. Primera Configuración

```bash
# 1. Copiar archivo de ejemplo
cp users_config.example.py users_config.py

# 2. Generar hash para tu contraseña
python auth.py "TuContraseñaSegura123"

# 3. Editar users_config.py con el hash generado
nano users_config.py
```

### 2. Credenciales por Defecto

**⚠️ CAMBIAR INMEDIATAMENTE EN PRODUCCIÓN**

- **Usuario:** `admin`
- **Contraseña:** `admin123`

---

## 🔒 Arquitectura de Seguridad

### Flujo de Autenticación

```
1. Usuario ingresa credenciales
   ↓
2. Rate Limiter verifica intentos
   ↓
3. Bcrypt verifica password hash
   ↓
4. JWT token es generado (1h expiry)
   ↓
5. Token guardado en session state
   ↓
6. Cada request verifica token válido
   ↓
7. Timeout automático después de 1h inactividad
```

### Capas de Protección

1. **Rate Limiting**
   - Máximo 5 intentos fallidos
   - Bloqueo temporal de 5 minutos
   - Contador independiente por usuario

2. **Password Security**
   - Hashing con bcrypt
   - Salt único por contraseña
   - 12 rounds de hashing (2^12 = 4096 iteraciones)
   - Verificación en tiempo constante

3. **Token Management**
   - JWT con firma HMAC-SHA256
   - Expiración de 1 hora
   - Validación en cada request
   - No almacenado en localStorage

4. **Session Security**
   - Estado en Streamlit session_state
   - Limpieza automática al expirar
   - Actualización de actividad en cada acción

---

## 🛡️ Configuración de Seguridad

### Variables de Entorno Recomendadas

```bash
# .env
JWT_SECRET_KEY=genera-una-clave-aleatoria-muy-larga-y-segura-2025
```

### Generar Secret Key Segura

```python
import secrets
print(secrets.token_urlsafe(64))
```

O con openssl:
```bash
openssl rand -base64 64
```

---

## 📋 Checklist de Seguridad para Producción

### Antes de Desplegar

- [ ] Cambiar credenciales de `admin` por defecto
- [ ] Configurar `JWT_SECRET_KEY` única y aleatoria
- [ ] Verificar que `users_config.py` esté en `.gitignore`
- [ ] Usar contraseñas fuertes (mín 12 caracteres)
- [ ] Habilitar HTTPS en el servidor
- [ ] Configurar firewall y limitar IPs si es posible
- [ ] Revisar y ajustar `SECURITY_CONFIG`
- [ ] Documentar credenciales en gestor de contraseñas
- [ ] Configurar respaldo de `users_config.py`
- [ ] Activar logs de auditoría

### Contraseñas Fuertes

✅ **Buenas Prácticas:**
- Mínimo 12 caracteres
- Combinar: mayúsculas, minúsculas, números, símbolos
- No usar palabras del diccionario
- No reutilizar contraseñas
- Usar gestor de contraseñas

❌ **Evitar:**
- admin123
- password123
- nombre + año
- contraseñas comunes

---

## 🔧 Gestión de Usuarios

### Agregar Usuario

```bash
# 1. Generar hash
python auth.py "ContraseñaDelNuevoUsuario"

# 2. Agregar a users_config.py
"nuevo_usuario": {
    "username": "nuevo_usuario",
    "password_hash": "$2b$12$hash_aqui",
    "role": "user",
    "name": "Nombre Completo",
    "enabled": True
}
```

### Deshabilitar Usuario

```python
# En users_config.py
"usuario": {
    ...
    "enabled": False  # Usuario bloqueado
}
```

### Cambiar Contraseña

```bash
# 1. Generar nuevo hash
python auth.py "NuevaContraseña"

# 2. Actualizar hash en users_config.py
"usuario": {
    ...
    "password_hash": "$2b$12$nuevo_hash_aqui"
}
```

---

## 🚨 Respuesta a Incidentes

### Cuenta Bloqueada

**Síntoma:** "Cuenta bloqueada temporalmente"

**Solución:**
1. Esperar 5 minutos
2. O reiniciar la aplicación para limpiar rate limiter

### Sesión Expirada

**Síntoma:** "Sesión expirada por inactividad"

**Solución:**
1. Volver a iniciar sesión
2. La sesión es válida por 1 hora de actividad

### Sospecha de Compromiso

**Acciones inmediatas:**
1. Cambiar todas las contraseñas
2. Rotar `JWT_SECRET_KEY`
3. Revisar logs de acceso
4. Deshabilitar usuarios comprometidos
5. Verificar accesos a Google Sheets

---

## 📊 Logs y Monitoreo

### Eventos Registrados

```python
# Login exitoso
✅ Login exitoso: admin

# Intentos fallidos
⚠️ Contraseña incorrecta para: admin
⚠️ Usuario no encontrado: usuario_falso

# Bloqueos
⚠️ Usuario bloqueado: admin - 120s restantes

# Sesiones
ℹ️ Sesión expirada por inactividad
ℹ️ Logout: admin
```

### Revisar Logs

```bash
# En la consola donde corre Streamlit
tail -f logs/spei-bot.log

# O revisar en tiempo real
streamlit run app.py 2>&1 | tee logs/app.log
```

---

## 🔍 Auditoría de Seguridad

### Preguntas de Verificación

1. ✅ ¿Todas las contraseñas son fuertes?
2. ✅ ¿JWT_SECRET_KEY es única y aleatoria?
3. ✅ ¿users_config.py no está en Git?
4. ✅ ¿Hay usuarios inactivos que debería deshabilitar?
5. ✅ ¿Los logs muestran actividad sospechosa?
6. ✅ ¿HTTPS está habilitado?
7. ✅ ¿Hay respaldo de la configuración?

---

## 🆘 Soporte y Ayuda

### Documentación Adicional

- `LOGIN_SETUP.md` - Configuración detallada
- `users_config.example.py` - Ejemplo de configuración
- `auth.py` - Código de autenticación
- `login_ui.py` - Interface de usuario

### Problemas Comunes

Ver `LOGIN_SETUP.md` sección "Solución de Problemas"

---

## 📝 Registro de Cambios de Seguridad

### v2.0 (Octubre 2025)
- ✅ Sistema de autenticación JWT implementado
- ✅ Rate limiting contra fuerza bruta
- ✅ Bcrypt para hashing de passwords
- ✅ UI moderna de login
- ✅ Sesiones con timeout automático

---

**Última actualización:** Octubre 2025
**Versión:** 2.0
**Estado:** Producción Ready ✅
