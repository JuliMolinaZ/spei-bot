#!/usr/bin/env python3
"""
Script de Gestión de Usuarios para SPEI BOT
Facilita la creación y administración de usuarios
"""

import sys
import auth

def print_banner():
    """Muestra el banner de la aplicación"""
    print("\n" + "="*60)
    print("🔐 SPEI BOT - Gestión de Usuarios")
    print("="*60 + "\n")

def generate_password_hash():
    """Genera un hash de contraseña"""
    print("📝 Generar Hash de Contraseña\n")

    if len(sys.argv) > 2:
        password = sys.argv[2]
    else:
        password = input("Ingresa la contraseña: ")

    if not password:
        print("❌ Error: Contraseña vacía\n")
        return

    print("\n⏳ Generando hash seguro...")
    password_hash = auth.hash_password(password)

    print("\n✅ Hash generado exitosamente!\n")
    print("="*60)
    print(f"Hash: {password_hash}")
    print("="*60)

    print("\n📋 Copia este hash a users_config.py:")
    print(f'\n"password_hash": "{password_hash}",\n')

def list_users():
    """Lista todos los usuarios configurados"""
    print("👥 Usuarios Configurados\n")

    try:
        from users_config import USERS_CONFIG

        if not USERS_CONFIG:
            print("⚠️ No hay usuarios configurados\n")
            return

        print(f"Total: {len(USERS_CONFIG)} usuario(s)\n")
        print("-" * 80)
        print(f"{'Usuario':<15} {'Nombre':<25} {'Rol':<10} {'Estado':<10}")
        print("-" * 80)

        for username, data in USERS_CONFIG.items():
            name = data.get("name", "N/A")
            role = data.get("role", "user")
            enabled = "✅ Activo" if data.get("enabled", True) else "🔴 Inactivo"

            print(f"{username:<15} {name:<25} {role:<10} {enabled:<10}")

        print("-" * 80 + "\n")

    except ImportError:
        print("❌ Error: No se encontró users_config.py")
        print("💡 Crea uno usando: cp users_config.example.py users_config.py\n")

def verify_password():
    """Verifica una contraseña contra un hash"""
    print("🔍 Verificar Contraseña\n")

    password = input("Ingresa la contraseña a verificar: ")
    password_hash = input("Ingresa el hash: ")

    if auth.verify_password(password, password_hash):
        print("\n✅ Contraseña CORRECTA\n")
    else:
        print("\n❌ Contraseña INCORRECTA\n")

def add_user_template():
    """Genera template para agregar un nuevo usuario"""
    print("➕ Generar Template de Usuario\n")

    username = input("Username: ")
    name = input("Nombre completo: ")
    role = input("Rol (admin/user) [user]: ") or "user"
    password = input("Contraseña: ")

    print("\n⏳ Generando hash...")
    password_hash = auth.hash_password(password)

    template = f'''
# Agregar este código a users_config.py en USERS_CONFIG:
"{username}": {{
    "username": "{username}",
    "password_hash": "{password_hash}",
    "role": "{role}",
    "name": "{name}",
    "enabled": True
}},
'''

    print("\n✅ Template generado!\n")
    print("="*60)
    print(template)
    print("="*60)
    print("\n📋 Copia este código a users_config.py\n")

def show_help():
    """Muestra ayuda de uso"""
    print_banner()
    print("Uso: python manage_users.py [comando] [argumentos]\n")
    print("Comandos disponibles:\n")
    print("  hash [contraseña]    - Genera hash de una contraseña")
    print("  list                 - Lista todos los usuarios")
    print("  verify               - Verifica una contraseña contra un hash")
    print("  add                  - Genera template para nuevo usuario")
    print("  help                 - Muestra esta ayuda")
    print("\nEjemplos:")
    print('  python manage_users.py hash "MiContraseña123"')
    print("  python manage_users.py list")
    print("  python manage_users.py add")
    print()

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    print_banner()

    if command == "hash":
        generate_password_hash()
    elif command == "list":
        list_users()
    elif command == "verify":
        verify_password()
    elif command == "add":
        add_user_template()
    elif command == "help":
        show_help()
    else:
        print(f"❌ Comando desconocido: {command}\n")
        print("💡 Usa 'python manage_users.py help' para ver comandos disponibles\n")

if __name__ == "__main__":
    main()
