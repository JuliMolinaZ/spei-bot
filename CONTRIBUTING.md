# 🤝 Guía de Contribución

¡Gracias por tu interés en contribuir al Conciliador Bancario! Este documento te guiará a través del proceso de contribución.

## 🚀 Cómo Contribuir

### 1. Fork del Repositorio
```bash
# Fork en GitHub y luego clona tu fork
git clone https://github.com/tu-usuario/conciliador-bancario.git
cd conciliador-bancario
```

### 2. Configurar Entorno de Desarrollo
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias de desarrollo
pip install -r requirements.txt
pip install pytest black flake8 mypy
```

### 3. Crear Rama Feature
```bash
git checkout -b feature/nueva-funcionalidad
```

## 📋 Estándares de Código

### Python
- **Formateo**: Usar `black` para formateo automático
- **Linting**: Usar `flake8` para análisis de código
- **Type Hints**: Usar `mypy` para verificación de tipos
- **Estilo**: Seguir PEP 8

```bash
# Formatear código
black src/

# Verificar linting
flake8 src/

# Verificar tipos
mypy src/
```

### Commits
Usar commits semánticos:
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bugs
- `docs:` Cambios en documentación
- `style:` Cambios de formato (no afectan funcionalidad)
- `refactor:` Refactoring de código
- `test:` Agregar o modificar tests
- `chore:` Tareas de mantenimiento

Ejemplo:
```bash
git commit -m "feat: agregar validación de archivos CSV"
```

## 🧪 Testing

### Ejecutar Tests
```bash
# Todos los tests
pytest

# Tests con cobertura
pytest --cov=src --cov-report=html

# Tests específicos
pytest tests/unit/
pytest tests/integration/
```

### Escribir Tests
- Crear tests para nuevas funcionalidades
- Mantener cobertura > 80%
- Usar nombres descriptivos para tests
- Incluir tests unitarios e integración

## 📖 Documentación

### Actualizar Documentación
- Documentar nuevas funcionalidades en README.md
- Agregar docstrings a funciones y clases
- Actualizar docs/ si es necesario
- Incluir ejemplos de uso

### Formato de Docstrings
```python
def procesar_archivo(archivo: str, formato: str) -> dict:
    """
    Procesa un archivo bancario según el formato especificado.
    
    Args:
        archivo: Ruta al archivo a procesar
        formato: Formato del archivo ('csv', 'txt', etc.)
    
    Returns:
        Diccionario con datos procesados
        
    Raises:
        ValueError: Si el formato no es soportado
        FileNotFoundError: Si el archivo no existe
    """
    pass
```

## 🐛 Reportar Issues

### Antes de Reportar
1. Buscar issues existentes
2. Verificar que no sea un problema de configuración
3. Probar con la última versión

### Template de Issue
```markdown
## Descripción
Descripción clara del problema o funcionalidad solicitada.

## Pasos para Reproducir
1. Paso 1
2. Paso 2
3. Paso 3

## Comportamiento Esperado
Lo que debería suceder.

## Comportamiento Actual
Lo que realmente sucede.

## Entorno
- OS: [Ubuntu 20.04, macOS 12, Windows 10]
- Python: [3.8, 3.9, 3.10]
- Versión del proyecto: [v1.0.0]

## Información Adicional
Logs, capturas de pantalla, etc.
```

## 🔄 Proceso de Pull Request

### 1. Antes de Enviar
- [ ] Tests pasan (`pytest`)
- [ ] Código formateado (`black src/`)
- [ ] Linting limpio (`flake8 src/`)
- [ ] Documentación actualizada
- [ ] Commit messages claros

### 2. Template de PR
```markdown
## Descripción
Descripción de los cambios realizados.

## Tipo de Cambio
- [ ] Bug fix
- [ ] Nueva funcionalidad
- [ ] Breaking change
- [ ] Documentación

## Testing
- [ ] Tests existentes pasan
- [ ] Nuevos tests agregados
- [ ] Tests manuales realizados

## Checklist
- [ ] Código sigue estándares del proyecto
- [ ] Auto-review realizado
- [ ] Documentación actualizada
- [ ] No hay warnings de linting
```

### 3. Proceso de Review
1. Revisión automática (CI/CD)
2. Revisión por mantenedores
3. Discusión y ajustes si es necesario
4. Merge cuando esté aprobado

## 🏷️ Versionado

Seguimos [Semantic Versioning](https://semver.org/):
- **MAJOR**: Cambios incompatibles
- **MINOR**: Nueva funcionalidad compatible
- **PATCH**: Correcciones compatibles

## 👥 Mantenedores

- [@tu-usuario](https://github.com/tu-usuario) - Mantenedor principal

## 🆘 Ayuda

¿Necesitas ayuda?
- 💬 [GitHub Discussions](https://github.com/tu-usuario/conciliador-bancario/discussions)
- 🐛 [GitHub Issues](https://github.com/tu-usuario/conciliador-bancario/issues)

## 📄 Licencia

Al contribuir, aceptas que tus contribuciones serán licenciadas bajo la [MIT License](LICENSE).

---

¡Gracias por contribuir al Conciliador Bancario! 🎉
