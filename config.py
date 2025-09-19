import os
from dotenv import load_dotenv


def load_config():
    """Carga la configuración desde variables de entorno"""
    load_dotenv(override=True)

    config = {
        "SHEET_ID": os.getenv("SHEET_ID", ""),
        "SHEET_TAB": os.getenv("SHEET_TAB", "Movimientos"),
        "BATCH_SIZE": int(os.getenv("BATCH_SIZE", "1000")),
        "ENABLE_CACHE": os.getenv("ENABLE_CACHE", "true").lower() == "true",
        "LOG_IMPORTS": os.getenv("LOG_IMPORTS", "true").lower() == "true",
        "GOOGLE_SA_JSON": os.getenv("GOOGLE_SA_JSON", ""),
        "GOOGLE_APPLICATION_CREDENTIALS": os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""),
    }

    return config


def validate_config(config):
    """Valida que la configuración sea correcta"""
    errors = []

    if not config["SHEET_ID"]:
        errors.append("SHEET_ID no está configurado")

    if not config["SHEET_TAB"]:
        errors.append("SHEET_TAB no está configurado")

    if config["BATCH_SIZE"] < 1 or config["BATCH_SIZE"] > 10000:
        errors.append("BATCH_SIZE debe estar entre 1 y 10000")

    return errors


def get_google_credentials():
    """Obtiene las credenciales de Google"""
    load_dotenv(override=True)  # Cargar variables de entorno desde .env
    sa_json = os.getenv("GOOGLE_SA_JSON")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if not sa_json and not credentials_path:
        raise ValueError(
            "Debes configurar GOOGLE_SA_JSON o GOOGLE_APPLICATION_CREDENTIALS"
        )

    return {"sa_json": sa_json, "credentials_path": credentials_path}
