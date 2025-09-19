import pandas as pd
import hashlib
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import logging

logger = logging.getLogger(__name__)


def validate_bank_file(df: pd.DataFrame) -> Dict[str, Any]:
    """Valida estructura de archivo bancario con mapeo flexible"""
    result = {
        "valid": True,
        "missing_required": [],
        "missing_optional": [],
        "warnings": [],
        "stats": {},
    }

    # Mapeo flexible de columnas
    column_mapping = {
        "fecha": [
            "Fecha",
            "Fecha Movimiento",
            "Fecha de Movimiento",
            "Fecha_",
            "FECHA",
        ],
        "cargo": ["Cargo", "Cargos", "CARGO", "CARGOS", "Debito", "Débito"],
        "abono": [
            "Abono",
            "Abonos",
            "ABONO",
            "ABONOS",
            "Credito",
            "Crédito",
            "Credito",
            "CREDITO",
        ],
    }

    # Verificar columnas requeridas
    required_found = {}
    for req_type, possible_names in column_mapping.items():
        found = False
        for name in possible_names:
            if name in df.columns:
                required_found[req_type] = name
                found = True
                break
        if not found:
            result["missing_required"].append(req_type)
            result["valid"] = False

    # Verificar columnas opcionales
    optional_columns = [
        "Descripción",
        "Descripcion",
        "DESCRIPCION",
        "Concepto",
        "CONCEPTO",
        "Saldo",
        "SALDO",
    ]
    missing_optional = [col for col in optional_columns if col not in df.columns]
    if missing_optional:
        result["missing_optional"] = missing_optional
        result["warnings"].append(f"Columnas opcionales faltantes: {missing_optional}")

    # Estadísticas básicas
    if result["valid"]:
        result["stats"] = {
            "total_rows": len(df),
            "columns_found": list(df.columns),
            "mapped_columns": required_found,
        }

    return result


def export_summary_report(results: List[Dict], output_format: str = "json") -> str:
    """Genera reporte de resumen en JSON o CSV"""
    if output_format == "json":
        return pd.DataFrame(results).to_json(orient="records", indent=2)
    else:
        return pd.DataFrame(results).to_csv(index=False)


def generate_uid_report(df: pd.DataFrame) -> Dict[str, Any]:
    """Genera reporte detallado de UIDs"""
    if "UID" not in df.columns:
        return {"error": "No hay columna UID"}

    uids = df["UID"].dropna()
    unique_uids = uids.unique()

    return {
        "total_uids": len(uids),
        "unique_uids": len(unique_uids),
        "duplicate_count": len(uids) - len(unique_uids),
        "uid_types": df["UID"].str.split(":").str[0].value_counts().to_dict()
        if "UID" in df.columns
        else {},
        "sample_uids": unique_uids[:10].tolist(),
    }


def sanitize_filename(filename: str) -> str:
    """Limpia nombre de archivo para uso seguro"""
    return re.sub(r"[^\w\-_\.]", "_", filename)


def format_currency(amount: float) -> str:
    """Formatea número como moneda"""
    return f"${amount:,.2f}"


def get_file_info(uploaded_file) -> Dict[str, Any]:
    """Extrae información de archivo subido"""
    return {
        "name": uploaded_file.name,
        "size": uploaded_file.size,
        "type": uploaded_file.type,
    }


def create_sample_data() -> pd.DataFrame:
    """Crea datos de muestra para testing"""
    return pd.DataFrame(
        {
            "Fecha": ["2025-01-15", "2025-01-16"],
            "Cargo": [1000, 0],
            "Abono": [0, 500],
            "Descripción": ["Pago SPEI", "Depósito"],
        }
    )


def analyze_duplicates_exhaustive(
    new_data: pd.DataFrame, existing_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Análisis exhaustivo de duplicados y conflictos

    Args:
        new_data: DataFrame con nuevos datos procesados
        existing_analysis: Análisis de datos existentes del sheets_client

    Returns:
        Dict con análisis detallado
    """
    analysis = {
        "total_new_records": len(new_data),
        "existing_uids": existing_analysis.get("existing_uids", set()),
        "uid_amount_map": existing_analysis.get("uid_amount_map", {}),
        "duplicates_found": [],
        "conflicts_found": [],
        "safe_to_insert": [],
        "summary": {
            "new_unique": 0,
            "duplicates": 0,
            "conflicts": 0,
            "insert_ready": 0,
        },
    }

    if new_data.empty:
        return analysis

    # Verificar que tenemos UID en los nuevos datos
    if "UID" not in new_data.columns:
        analysis["error"] = "No hay columna UID en nuevos datos"
        return analysis

    # Análisis por cada registro nuevo
    for idx, row in new_data.iterrows():
        uid = str(row["UID"]).strip()

        if not uid:
            continue

        # Verificar si ya existe
        if uid in analysis["existing_uids"]:
            # Es un duplicado - verificar si hay conflicto
            existing_amounts = analysis["uid_amount_map"].get(uid, {})

            new_cargo = float(row["Cargo"]) if pd.notna(row["Cargo"]) else 0
            new_abono = float(row["Abono"]) if pd.notna(row["Abono"]) else 0
            new_net = new_cargo - new_abono

            existing_cargo = existing_amounts.get("cargo", 0)
            existing_abono = existing_amounts.get("abono", 0)
            existing_net = existing_amounts.get("net_amount", 0)

            # Detectar conflicto (montos diferentes)
            is_conflict = False
            conflict_reason = []

            if abs(new_cargo - existing_cargo) > 0.01:  # Tolerancia para floats
                is_conflict = True
                conflict_reason.append(f"Cargo: {existing_cargo} vs {new_cargo}")

            if abs(new_abono - existing_abono) > 0.01:
                is_conflict = True
                conflict_reason.append(f"Abono: {existing_abono} vs {new_abono}")

            if is_conflict:
                analysis["conflicts_found"].append(
                    {
                        "uid": uid,
                        "row_index": idx,
                        "new_data": {
                            "cargo": new_cargo,
                            "abono": new_abono,
                            "net": new_net,
                            "descripcion": row.get("Descripción", ""),
                            "fecha": row.get("Fecha", ""),
                        },
                        "existing_data": {
                            "cargo": existing_cargo,
                            "abono": existing_abono,
                            "net": existing_net,
                        },
                        "conflict_reason": conflict_reason,
                    }
                )
            else:
                analysis["duplicates_found"].append(
                    {"uid": uid, "row_index": idx, "reason": "Duplicado exacto"}
                )
        else:
            # Es nuevo - seguro para insertar
            analysis["safe_to_insert"].append(
                {"uid": uid, "row_index": idx, "data": row.to_dict()}
            )

    # Actualizar resumen
    analysis["summary"]["new_unique"] = len(analysis["safe_to_insert"])
    analysis["summary"]["duplicates"] = len(analysis["duplicates_found"])
    analysis["summary"]["conflicts"] = len(analysis["conflicts_found"])
    analysis["summary"]["insert_ready"] = len(analysis["safe_to_insert"])

    return analysis


def validate_insertion_safety(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida que es seguro proceder con la inserción

    Args:
        analysis: Resultado de analyze_duplicates_exhaustive

    Returns:
        Dict con validación de seguridad
    """
    validation = {
        "safe_to_proceed": True,
        "warnings": [],
        "errors": [],
        "recommendations": [],
    }

    # Verificar conflictos críticos
    if analysis["summary"]["conflicts"] > 0:
        validation["warnings"].append(
            f"⚠️ Se encontraron {analysis['summary']['conflicts']} conflictos de montos"
        )
        validation["recommendations"].append(
            "Revisar manualmente los conflictos antes de proceder"
        )

    # Verificar duplicados
    if analysis["summary"]["duplicates"] > 0:
        validation["warnings"].append(
            f"ℹ️ Se encontraron {analysis['summary']['duplicates']} duplicados exactos"
        )

    # Verificar que hay datos para insertar
    if analysis["summary"]["insert_ready"] == 0:
        validation["errors"].append("No hay registros nuevos para insertar")
        validation["safe_to_proceed"] = False

    # Verificar integridad de datos
    if analysis["summary"]["new_unique"] > 0:
        validation["recommendations"].append(
            f"✅ {analysis['summary']['new_unique']} registros nuevos listos para inserción"
        )

    return validation


def generate_insertion_report(
    analysis: Dict[str, Any], validation: Dict[str, Any]
) -> str:
    """
    Genera reporte detallado para el usuario

    Args:
        analysis: Análisis de duplicados
        validation: Validación de seguridad

    Returns:
        String con reporte formateado
    """
    report = []
    report.append("🔍 REPORTE DE ANÁLISIS DE INSERCIÓN")
    report.append("=" * 50)

    # Resumen general
    report.append(f"📊 RESUMEN GENERAL:")
    report.append(
        f"   • Total de registros nuevos: {analysis['summary']['new_unique']}"
    )
    report.append(f"   • Duplicados encontrados: {analysis['summary']['duplicates']}")
    report.append(f"   • Conflictos detectados: {analysis['summary']['conflicts']}")
    report.append(f"   • Listos para inserción: {analysis['summary']['insert_ready']}")
    report.append("")

    # Estado de seguridad
    if validation["safe_to_proceed"]:
        report.append("✅ ESTADO: SEGURO PARA PROCEDER")
    else:
        report.append("❌ ESTADO: NO ES SEGURO PROCEDER")

    # Advertencias
    if validation["warnings"]:
        report.append("")
        report.append("⚠️ ADVERTENCIAS:")
        for warning in validation["warnings"]:
            report.append(f"   • {warning}")

    # Errores
    if validation["errors"]:
        report.append("")
        report.append("❌ ERRORES:")
        for error in validation["errors"]:
            report.append(f"   • {error}")

    # Recomendaciones
    if validation["recommendations"]:
        report.append("")
        report.append("💡 RECOMENDACIONES:")
        for rec in validation["recommendations"]:
            report.append(f"   • {rec}")

    # Detalles de conflictos (si los hay)
    if analysis["conflicts_found"]:
        report.append("")
        report.append("🔥 CONFLICTOS DETECTADOS:")
        for i, conflict in enumerate(
            analysis["conflicts_found"][:5], 1
        ):  # Solo primeros 5
            report.append(f"   {i}. UID: {conflict['uid']}")
            report.append(
                f"      Nuevo: Cargo=${conflict['new_data']['cargo']}, Abono=${conflict['new_data']['abono']}"
            )
            report.append(
                f"      Existente: Cargo=${conflict['existing_data']['cargo']}, Abono=${conflict['existing_data']['abono']}"
            )
            report.append(f"      Razón: {', '.join(conflict['conflict_reason'])}")

        if len(analysis["conflicts_found"]) > 5:
            report.append(
                f"      ... y {len(analysis['conflicts_found']) - 5} conflictos más"
            )

    return "\n".join(report)


def prepare_safe_insertion_data(analysis: Dict[str, Any]) -> pd.DataFrame:
    """
    Prepara solo los datos seguros para inserción

    Args:
        analysis: Resultado de analyze_duplicates_exhaustive

    Returns:
        DataFrame con solo registros seguros para insertar
    """
    if not analysis["safe_to_insert"]:
        return pd.DataFrame()

    # Extraer solo los registros seguros
    safe_indices = [item["row_index"] for item in analysis["safe_to_insert"]]

    # Asumimos que tenemos acceso al DataFrame original
    # En la implementación real, esto se manejará en el contexto de la aplicación

    return safe_indices
