#!/usr/bin/env python3
"""
Script de Verificación de Conexión a Google Sheets
Verifica que todo esté configurado correctamente para SPEI BOT
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def print_step(emoji, message, status=None):
    """Imprime un paso con formato"""
    if status == "ok":
        print(f"{emoji} {message} ✅")
    elif status == "error":
        print(f"{emoji} {message} ❌")
    elif status == "warning":
        print(f"{emoji} {message} ⚠️")
    else:
        print(f"{emoji} {message}")

def check_env_file():
    """Verifica que existe el archivo .env"""
    print_step("📄", "Verificando archivo .env...", "")
    
    if not os.path.exists(".env"):
        print_step("  ", "Archivo .env NO encontrado", "error")
        print("  💡 Solución: cp env.example .env")
        return False
    
    print_step("  ", "Archivo .env encontrado", "ok")
    return True

def check_env_variables():
    """Verifica las variables de entorno"""
    print_step("🔧", "Verificando variables de entorno...", "")
    
    load_dotenv(override=True)
    
    errors = []
    warnings = []
    
    # SHEET_ID
    sheet_id = os.getenv("SHEET_ID", "")
    if not sheet_id or sheet_id == "TU_SHEET_ID_AQUI":
        errors.append("SHEET_ID no está configurado")
        print_step("  ", "SHEET_ID", "error")
    else:
        print_step("  ", f"SHEET_ID: {sheet_id[:20]}...", "ok")
    
    # SHEET_TAB
    sheet_tab = os.getenv("SHEET_TAB", "")
    if sheet_tab:
        print_step("  ", f"SHEET_TAB: {sheet_tab}", "ok")
    else:
        warnings.append("SHEET_TAB no configurado (usará default)")
        print_step("  ", "SHEET_TAB no configurado (usará 'Movimientos_Nuevos')", "warning")
    
    # Credenciales
    google_sa_json = os.getenv("GOOGLE_SA_JSON", "")
    google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    
    if google_sa_json:
        print_step("  ", "GOOGLE_SA_JSON configurado", "ok")
    elif google_credentials_path:
        if os.path.exists(google_credentials_path):
            print_step("  ", f"GOOGLE_APPLICATION_CREDENTIALS: {Path(google_credentials_path).name}", "ok")
        else:
            errors.append(f"Archivo de credenciales no existe: {google_credentials_path}")
            print_step("  ", "Archivo de credenciales NO encontrado", "error")
    else:
        errors.append("No hay credenciales de Google configuradas")
        print_step("  ", "Credenciales de Google NO configuradas", "error")
    
    return len(errors) == 0, errors, warnings

def check_credentials_file():
    """Verifica archivos de credenciales JSON"""
    print_step("🔑", "Verificando archivos de credenciales...", "")
    
    json_files = list(Path(".").glob("*.json"))
    
    # Filtrar archivos de sistema
    json_files = [f for f in json_files if not f.name.startswith(".")]
    
    if not json_files:
        print_step("  ", "No se encontraron archivos de credenciales JSON", "warning")
        print("  💡 Necesitas descargar las credenciales desde Google Cloud")
        return False
    
    print_step("  ", f"Archivos JSON encontrados: {len(json_files)}", "ok")
    for f in json_files:
        print(f"     - {f.name}")
    
    return True

def check_gitignore():
    """Verifica que .gitignore está configurado correctamente"""
    print_step("🔒", "Verificando seguridad (.gitignore)...", "")
    
    if not os.path.exists(".gitignore"):
        print_step("  ", ".gitignore NO encontrado", "error")
        return False
    
    with open(".gitignore", "r") as f:
        gitignore_content = f.read()
    
    checks = {
        ".env": ".env" in gitignore_content,
        "*.json": "*.json" in gitignore_content or ".json" in gitignore_content,
        "credentials": "credentials" in gitignore_content or "spei-bot-" in gitignore_content
    }
    
    all_ok = True
    for item, is_ok in checks.items():
        if is_ok:
            print_step("  ", f"{item} protegido", "ok")
        else:
            print_step("  ", f"{item} NO protegido", "warning")
            all_ok = False
    
    return all_ok

def test_google_connection():
    """Intenta conectar a Google Sheets"""
    print_step("🌐", "Probando conexión a Google Sheets...", "")
    
    try:
        # Importar después de cargar .env
        load_dotenv(override=True)
        from sheets_client import _get_client
        
        print("  → Obteniendo cliente de Google...")
        gc = _get_client()
        
        print_step("  ", "Cliente de Google creado correctamente", "ok")
        
        # Intentar abrir la hoja
        sheet_id = os.getenv("SHEET_ID", "")
        if sheet_id and sheet_id != "TU_SHEET_ID_AQUI":
            print(f"  → Intentando acceder a la hoja {sheet_id[:20]}...")
            sheet = gc.open_by_key(sheet_id)
            print_step("  ", f"Hoja '{sheet.title}' accedida correctamente", "ok")
            
            # Listar pestañas
            worksheets = sheet.worksheets()
            print(f"  → Pestañas disponibles: {len(worksheets)}")
            for ws in worksheets[:5]:  # Mostrar solo las primeras 5
                print(f"     - {ws.title} ({ws.row_count} filas x {ws.col_count} columnas)")
            
            return True
        else:
            print_step("  ", "SHEET_ID no configurado, omitiendo prueba de hoja", "warning")
            return False
        
    except Exception as e:
        print_step("  ", f"Error: {str(e)}", "error")
        return False

def print_summary(results):
    """Imprime resumen final"""
    print("\n" + "="*60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("="*60)
    
    all_ok = all(results.values())
    
    for check, status in results.items():
        emoji = "✅" if status else "❌"
        print(f"{emoji} {check}")
    
    print("="*60)
    
    if all_ok:
        print("\n🎉 ¡TODO ESTÁ CONFIGURADO CORRECTAMENTE!")
        print("\nPuedes ejecutar la aplicación con:")
        print("  source venv/bin/activate")
        print("  streamlit run main.py")
    else:
        print("\n⚠️  HAY PROBLEMAS DE CONFIGURACIÓN")
        print("\nConsulta la documentación:")
        print("  docs/CONFIGURACION_GOOGLE_SHEETS.md")
        print("  INICIO_RAPIDO_SHEETS.md")

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN - SPEI BOT")
    print("="*60 + "\n")
    
    results = {}
    
    # 1. Verificar archivo .env
    results["Archivo .env"] = check_env_file()
    print()
    
    # 2. Verificar variables de entorno
    if results["Archivo .env"]:
        env_ok, errors, warnings = check_env_variables()
        results["Variables de entorno"] = env_ok
        
        if errors:
            print("\n  ⚠️  Errores encontrados:")
            for error in errors:
                print(f"     - {error}")
        
        if warnings:
            print("\n  ℹ️  Advertencias:")
            for warning in warnings:
                print(f"     - {warning}")
    else:
        results["Variables de entorno"] = False
    
    print()
    
    # 3. Verificar credenciales
    results["Archivos de credenciales"] = check_credentials_file()
    print()
    
    # 4. Verificar .gitignore
    results["Seguridad (.gitignore)"] = check_gitignore()
    print()
    
    # 5. Probar conexión (solo si configuración básica está ok)
    if results.get("Variables de entorno", False):
        results["Conexión a Google Sheets"] = test_google_connection()
    else:
        print_step("🌐", "Omitiendo prueba de conexión (configuración incompleta)", "warning")
        results["Conexión a Google Sheets"] = False
    
    # Resumen final
    print_summary(results)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Verificación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

