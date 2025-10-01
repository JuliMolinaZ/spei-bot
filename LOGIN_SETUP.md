# 🔐 Sistema de Login - SPEI BOT

## Características de Seguridad

✅ **Autenticación JWT** - Tokens seguros con expiración de 1 hora
✅ **Encriptación bcrypt** - Contraseñas hasheadas con 12 rounds
✅ **Rate Limiting** - Protección contra ataques de fuerza bruta (5 intentos en 5 minutos)
✅ **Sesiones seguras** - Expiración automática por inactividad
✅ **UI moderna** - Diseño profesional y amigable

---

## 🚀 Inicio Rápido

### Credenciales por Defecto

**Usuario:** `admin`
**Contraseña:** `admin123`

⚠️ **IMPORTANTE:** Cambia estas credenciales inmediatamente en producción.

---

## 📝 Configuración de Usuarios

### Método 1: Generar Hash de Contraseña

1. Ejecuta el script para generar un hash:
```bash
python auth.py "MiContraseñaSegura123"
```

2. Copia el hash generado

3. Edita el archivo `users_config.py`:
```python
USERS_CONFIG = {
    "mi_usuario": {
        "username": "mi_usuario",
        "password_hash": "$2b$12$...",  # Pega aquí el hash generado
        "role": "user",  # o "admin"
        "name": "Nombre del Usuario",
        "enabled": True
    }
}
```

### Método 2: Usar la Función de Configuración

```python
from auth import configure_user

configure_user(
    username="nuevo_usuario",
    password="ContraseñaSegura123",
    role="user",
    name="Nombre Completo"
)
```

---

## 🔒 Roles de Usuario

### Admin
- Acceso completo a todas las funcionalidades
- Puede gestionar configuraciones
- Ver todos los logs y estadísticas

### User (Futuro)
- Acceso a funcionalidades básicas
- Solo lectura de estadísticas

---

## ⚙️ Configuración de Seguridad

Edita `users_config.py` para ajustar parámetros:

```python
SECURITY_CONFIG = {
    "max_login_attempts": 5,          # Intentos antes de bloqueo
    "block_duration_minutes": 5,      # Duración del bloqueo
    "session_timeout_hours": 1,       # Timeout de sesión
    "require_strong_password": True,  # Requiere contraseñas fuertes
    "password_min_length": 8,         # Longitud mínima
}
```

---

## 🛡️ Mejores Prácticas de Seguridad

### 1. Contraseñas Fuertes
- Mínimo 8 caracteres
- Combinar mayúsculas, minúsculas, números y símbolos
- No usar contraseñas comunes o predecibles

### 2. Variable de Entorno para Secret Key
Configura una clave secreta única en producción:

```bash
export JWT_SECRET_KEY="tu-clave-super-secreta-aleatoria-2025"
```

O en tu archivo `.env`:
```
JWT_SECRET_KEY=tu-clave-super-secreta-aleatoria-2025
```

### 3. No Subir Credenciales al Repositorio
- ⚠️ Agrega `users_config.py` a `.gitignore`
- Nunca subas contraseñas o hashes a Git
- Usa variables de entorno en producción

### 4. Rotación de Credenciales
- Cambia las contraseñas regularmente
- Revoca acceso de usuarios inactivos
- Audita logs de acceso periódicamente

---

## 🔧 Administración de Usuarios

### Agregar Nuevo Usuario

1. Genera el hash de la contraseña:
```bash
python auth.py "NuevaContraseña123"
```

2. Agrega el usuario a `users_config.py`:
```python
"usuario2": {
    "username": "usuario2",
    "password_hash": "$2b$12$hash_generado_aqui",
    "role": "user",
    "name": "Segundo Usuario",
    "enabled": True
}
```

3. Reinicia la aplicación

### Deshabilitar Usuario

Cambia `enabled: False` en `users_config.py`:
```python
"usuario1": {
    ...
    "enabled": False  # Usuario deshabilitado
}
```

### Cambiar Contraseña

1. Genera nuevo hash:
```bash
python auth.py "NuevaContraseña456"
```

2. Actualiza el hash en `users_config.py`

---

## 🐛 Solución de Problemas

### "Cuenta bloqueada temporalmente"
- **Causa:** Demasiados intentos fallidos de login
- **Solución:** Espera 5 minutos o reinicia la aplicación

### "Sesión expirada"
- **Causa:** 1 hora de inactividad
- **Solución:** Vuelve a iniciar sesión

### No puedo iniciar sesión
1. Verifica que el usuario esté en `users_config.py`
2. Verifica que `enabled: True`
3. Confirma que la contraseña es correcta
4. Revisa los logs en consola

### Error "ModuleNotFoundError: No module named 'jwt'"
- **Solución:**
```bash
pip install PyJWT bcrypt
```

---

## 📊 Monitoreo y Logs

Los intentos de login se registran en los logs:

```
✅ Login exitoso: admin
⚠️ Usuario bloqueado: usuario1 - 120s restantes
⚠️ Contraseña incorrecta para: admin
```

---

## 🔐 Características de Protección

### Rate Limiting
- 5 intentos fallidos → Bloqueo de 5 minutos
- Contador independiente por usuario
- Reset automático después del bloqueo

### Expiración de Sesión
- Token JWT válido por 1 hora
- Renovación automática con cada acción
- Logout automático al expirar

### Protección de Contraseñas
- Bcrypt con 12 rounds de hashing
- Salt único por contraseña
- Verificación de tiempo constante

---

## 📝 Checklist de Producción

Antes de desplegar en producción:

- [ ] Cambiar contraseña de `admin`
- [ ] Configurar `JWT_SECRET_KEY` única
- [ ] Agregar `users_config.py` a `.gitignore`
- [ ] Habilitar HTTPS en el servidor
- [ ] Configurar logs de auditoría
- [ ] Revisar y ajustar `SECURITY_CONFIG`
- [ ] Documentar credenciales en lugar seguro
- [ ] Configurar respaldos de usuarios

---

## 🆘 Soporte

Si tienes problemas con el sistema de login:

1. Revisa esta documentación
2. Verifica los logs de la aplicación
3. Consulta los archivos:
   - `auth.py` - Lógica de autenticación
   - `users_config.py` - Configuración de usuarios
   - `login_ui.py` - Interface de usuario

---

**SPEI BOT v2.0** | Sistema de Autenticación Seguro
