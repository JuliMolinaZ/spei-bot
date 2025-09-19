# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Running the Application
```bash
# Start the Streamlit app
streamlit run app.py

# Run with specific port
streamlit run app.py --server.port=8502
```

### Development Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest tests/ -v --cov=. --cov-report=xml

# Run specific test types
pytest -m unit      # Unit tests only
pytest -m integration  # Integration tests only
pytest -m "not slow"   # Exclude slow tests
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8

# Type checking
mypy .
```

### Docker Development
```bash
# Build and run production container
docker-compose up --build

# Run development container with hot-reload
docker-compose --profile dev up

# Build image only
docker build -t conciliador .
```

## Architecture Overview

### Core Components

**Main Application (`app.py`)**
- Streamlit web interface with 4 main tabs: File Upload, Dashboard, Statistics, Import Logs
- Multi-file processing with hash-based duplicate detection
- Real-time metrics and data visualization
- Batch insertion to Google Sheets with rate limiting

**Bank Parser (`bank_parser.py`)**
- Normalizes column names from various bank TXT/CSV formats
- Converts dates to ISO format, handles multiple date formats including Spanish months
- Generates unique UIDs for transactions: `SPEI:<clave>` for SPEI transfers, `REC:<recibo>|<fecha>|<hora>|<digest>` for others
- Classifies transaction types (SPEI, Comisión, POS, etc.)

**Google Sheets Client (`sheets_client.py`)**
- Handles authentication via service account JSON or credentials file
- Provides caching mechanism for read operations
- Batch processing for large data insertions (1000 rows per batch)
- Automatic worksheet creation with proper headers
- Comprehensive validation and error handling

**Configuration (`config.py`)**
- Environment-based configuration loading via `.env` files
- Validation for required settings and reasonable defaults
- Google credentials management (JSON or file path)

### Data Flow Architecture

1. **File Upload**: Multiple TXT/CSV files processed simultaneously
2. **Parsing**: Bank-specific format normalization and UID generation
3. **Deduplication**: Hash-based file tracking + UID-based record deduplication
4. **Conflict Detection**: Same UID with different amounts flagged as conflictive
5. **Batch Insertion**: Only new, non-conflictive records inserted to Google Sheets
6. **Audit Logging**: Every import logged to `Imports_Log` worksheet

### Google Sheets Structure

**Movimientos Worksheet**
- Columns: Fecha, Hora, Tipo, Recibo, ClaveRastreo, Descripción, Cargo, Abono, Saldo, UID, ArchivoOrigen, ImportadoEn

**Imports_Log Worksheet**  
- Columns: Archivo, HashArchivo, FilasLeídas, NuevosInsertados, DuplicadosSaltados, Conflictivos, FechaHora

### Key Business Logic

**UID Generation Strategy**
- SPEI transactions with tracking codes ≥6 chars: `SPEI:<ClaveRastreo>`
- All others: `REC:<Recibo>|<Fecha>|<Hora>|<DescriptionDigest24chars>`

**Idempotency Mechanisms**
- MD5 hash prevents re-importing same file
- UID prevents duplicate transaction records
- Conflict detection for same UID with different amounts

### Configuration Requirements

Create `.env` file with:
```bash
SHEET_ID=your_google_sheet_id
SHEET_TAB=Movimientos
GOOGLE_SA_JSON={"type":"service_account",...}  # OR
GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa.json
```

### Test Structure
- Unit tests in `tests/test_bank_parser.py` 
- Integration tests throughout `test_*.py` files in root directory
- Test markers: `unit`, `integration`, `slow` for selective test execution

### Development Notes
- The app supports "test mode" when no Google Sheets credentials are configured
- Rate limiting built-in (100ms delays between batch operations)
- Extensive logging throughout all components for debugging
- Docker support for both production and development environments