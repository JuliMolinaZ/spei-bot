import pytest
import pandas as pd
from bank_parser import parse_bank_txt, add_uids, classify_tipo


class TestBankParser:
    def test_parse_bank_txt_basic(self):
        """Test básico de parseo de archivo bancario"""
        # Datos de prueba
        test_data = {
            "Fecha Movimiento": ["15/01/2024", "16/01/2024"],
            "Hora": ["09:30", "14:15"],
            "Recibo": ["REF001", "REF002"],
            "Descripción": ["SPEI recibido", "Comisión"],
            "Cargo": ["0", "25.50"],
            "Abono": ["1000.00", "0"],
            "Saldo": ["5000.00", "4974.50"],
        }
        df = pd.DataFrame(test_data)

        result = parse_bank_txt(df)

        assert "Fecha" in result.columns
        assert "Hora" in result.columns
        assert "Recibo" in result.columns
        assert "Descripción" in result.columns
        assert "Cargo" in result.columns
        assert "Abono" in result.columns
        assert "Saldo" in result.columns
        assert len(result) == 2

    def test_classify_tipo(self):
        """Test de clasificación de tipos de movimiento"""
        # Test SPEI
        assert classify_tipo("SPEI recibido") == "SPEI Recibido"
        assert classify_tipo("SPEI enviado") == "SPEI Enviado"

        # Test comisión
        assert classify_tipo("Comisión por servicio") == "Comisión"

        # Test POS
        assert classify_tipo("Pago POS Terminal") == "POS"

        # Test vacío
        assert classify_tipo("") == ""
        assert classify_tipo(None) == ""

    def test_add_uids(self):
        """Test de generación de UIDs"""
        test_data = {
            "Fecha": ["2024-01-15", "2024-01-15"],
            "Hora": ["09:30", "14:15"],
            "Recibo": ["REF001", "REF002"],
            "Descripción": [
                "SPEI recibido Clave de rastreo ABC123456789",
                "Comisión por servicio",
            ],
            "Cargo": [0, 25.50],
            "Abono": [1000.00, 0],
            "Saldo": [5000.00, 4974.50],
        }
        df = pd.DataFrame(test_data)
        df["Tipo"] = df["Descripción"].map(classify_tipo)

        result = add_uids(df)

        assert "UID" in result.columns
        assert len(result["UID"]) == 2
        assert result["UID"].iloc[0].startswith("SPEI:")  # SPEI con clave
        assert result["UID"].iloc[1].startswith("REC:")  # Otro tipo

    def test_normalize_numbers(self):
        """Test de normalización de números"""
        from bank_parser import _normalize_numbers

        # Test con comas
        series = pd.Series(["1,000.50", "2,500", "0"])
        result = _normalize_numbers(series)

        assert result.iloc[0] == 1000.50
        assert result.iloc[1] == 2500.0
        assert result.iloc[2] == 0.0

    def test_to_iso_date(self):
        """Test de conversión de fechas"""
        from bank_parser import _to_iso_date

        # Test formato dd/mm/yyyy
        assert _to_iso_date("15/01/2024") == "2024-01-15"

        # Test formato yyyy-mm-dd
        assert _to_iso_date("2024-01-15") == "2024-01-15"

        # Test formato dd-mm-yyyy
        assert _to_iso_date("15-01-2024") == "2024-01-15"

        # Test valor nulo
        assert _to_iso_date(None) is None
        assert _to_iso_date("") is None
