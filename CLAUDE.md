# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an NPS (Net Promoter Score) automation system specialized for "Mercadão dos Óculos" business operations. The system extracts data from Google Sheets, analyzes customer satisfaction metrics using AI, and generates comprehensive PDF reports for post-sales analysis.

## Architecture

### Core Components

- **`analisador_nps_completo.py`**: Complete NPS analysis system - handles extraction, metrics calculation, and AI analysis in one module
- **`main.py`**: CLI interface with menu system for generating reports and configuration
- **`gerador_pdf.py`**: **Adaptive PDF generator** with WeasyPrint - automatically detects data type and creates professional reports with custom styling and emoji support
- **`analisador_ia_simple.py`**: AI analysis engine using OpenAI GPT-4o for generating business insights
- **`adaptador_dados.py`**: Data format converter - bridges between different data structures used by components
- **`frontend/server.py`**: Flask web server providing REST API and web interface

### Data Flow

1. **`analisador_nps_completo.py`** extracts data from Google Sheets using public CSV endpoints
2. Automatically identifies and categorizes data by tabs: D+1 (Atendimento), D+30 (Produto), NPS Ruim (Critical cases)
3. Calculates NPS metrics using industry-standard formulas
4. Sends structured data to OpenAI GPT-4o for intelligent business analysis
5. **`gerador_pdf.py`** converts AI insights into professionally formatted PDF reports

### Sheet Structure

The system expects Google Sheets with specific tabs (flexible naming):
- **D+1 or NPS D+1**: Customer service evaluation data
- **D+30 or NPS D+30**: Product satisfaction data  
- **NPS Ruim**: Critical/negative feedback cases

The system automatically recognizes tabs with these naming patterns:
- D+1 variations: "D+1", "NPS D+1", "d+1", "nps d+1"
- D+30 variations: "D+30", "NPS D+30", "d+30", "nps d+30"
- NPS Ruim variations: "NPS Ruim", "ruim", case-insensitive

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python3 -m venv nps_env
source nps_env/bin/activate  # Linux/Mac
# or nps_env\Scripts\activate  # Windows

# Install dependencies (no requirements.txt found - install manually)
pip install pandas requests openai weasyprint flask flask-cors
```

### Running the Application

```bash
# CLI interface (main application)
python3 main.py

# Web server (Flask API)
python3 frontend/server.py

# Direct component testing
python3 analisador_nps_completo.py
python3 gerador_pdf.py
python3 analisador_ia_simple.py
```

### Common Operations

```bash
# Test complete analysis system
python3 -c "from analisador_nps_completo import AnalisadorNPSCompleto; a = AnalisadorNPSCompleto('Test'); print('Complete analyzer ready')"

# Test adaptive PDF generator (NEW)
python3 -c "from gerador_pdf import gerar_pdf_inteligente; gerar_pdf_inteligente('Test data', 'TestLoja')"

# Generate sample PDF report
python3 -c "from gerador_pdf import GeradorPDFCustomizado; g = GeradorPDFCustomizado(); g.main()"

# Test AI analysis engine
python3 -c "from analisador_ia_simple import AnalisadorIACustomizado; print('IA analyzer ready')"
```

## API Configuration

The system uses OpenAI API (GPT-4o model) for intelligent analysis. API key is configured in:
- `analisador_nps_completo.py:25` (main system)
- `analisador_ia_simple.py:19` (analysis engine)

**Security Note**: API keys are currently hardcoded - should be moved to environment variables.

**AI Analysis**: The system uses `analisador_ia_simple.py` for generating business insights with structured prompts optimized for NPS data analysis.

## File Structure

```
nps_automation/
├── main.py                      # Main CLI application
├── analisador_nps_completo.py   # Core system: extraction + analysis + AI
├── gerador_pdf.py              # PDF report generation with WeasyPrint
├── analisador_ia_simple.py     # AI analysis engine (OpenAI GPT-4o)
├── adaptador_dados.py          # Data format conversion utilities
├── frontend/
│   ├── server.py               # Flask web server + REST API
│   ├── index.html              # Web interface
│   ├── script.js               # Frontend JavaScript
│   ├── style.css               # Web styling
│   └── api.js                  # API client functions
├── relatorios/                 # Generated PDF reports directory
├── fonts/                      # Custom fonts for PDF generation
├── nps_env/                    # Python virtual environment
└── CLAUDE.md                   # This documentation
```

## Key Design Patterns

- **Data Extraction**: Uses public Google Sheets CSV export to avoid authentication complexity
- **🎯 Adaptive Recognition**: Intelligent fallback system analyzes unknown sheet structures automatically
- **AI Integration**: Structured prompts with business context for relevant insights
- **🤖 Adaptive PDF Generation**: **NEW!** Smart PDF generator that automatically detects data type and applies appropriate formatting
- **Error Handling**: Graceful fallbacks throughout the pipeline
- **Modularity**: Each component can be tested independently

## 🆕 Adaptive PDF Generation System

The new `PDFGeneratorAdaptativo` class provides intelligent PDF generation that adapts to any data structure:

### Supported Data Types
- **Text Analysis**: AI-generated analysis text → Professional formatted reports
- **Structured Data**: Dictionaries with metrics → Organized metric reports  
- **Tabular Data**: Lists of dictionaries → Professional tables
- **Pre-structured**: Existing format with `tipo` field → Direct rendering

### Automatic Detection Features
- **Content Analysis**: Detects NPS, metrics, vendor data automatically
- **Format Recognition**: String, dict, list, or structured formats
- **Template Selection**: Chooses optimal layout based on content
- **Professional Styling**: Consistent Mercadão dos Óculos branding

### Usage Examples
```python
from gerador_pdf import gerar_pdf_inteligente

# Any string (analysis text)
gerar_pdf_inteligente("NPS: 85.4%\nExcelente resultado!", "MinhaLoja")

# Any dictionary (metrics data)  
gerar_pdf_inteligente({"nps": 85.4, "vendas": 234}, "MinhaLoja")

# Any list (tabular data)
gerar_pdf_inteligente([{"Vendedor": "Maria", "NPS": 92.1}], "MinhaLoja")

# Pre-structured data (existing format)
gerar_pdf_inteligente([{"tipo": "metrica", "conteudo": "NPS: 85.4%"}], "MinhaLoja")
```

## 🔄 Adaptive System Features

### Fallback Intelligence
The system now includes intelligent fallbacks for handling different sheet structures:

**Automatic Pattern Detection:**
- **Communication columns**: WhatsApp vs Telefone detection
- **Management columns**: Status, Situação, Resolução patterns
- **Essential columns**: Nome, Avaliação, Vendedor recognition
- **ID patterns**: Bot IDs, general IDs, sources

**Scoring System:**
- Assigns confidence scores to each possible tab type
- Chooses highest scoring classification
- Falls back to generic types for unknown structures

**Supported Fallback Types:**
- `D1`, `D30`, `NPS_Ruim` (original types)
- `Dados_Gerais` (generic data with essential columns)
- `Aba_Desconhecida` (completely unknown structures)

### Usage Examples
```python
# System automatically handles variations like:
# - "Customer Name" instead of "Nome Completo"
# - "Rating" instead of "Avaliação"  
# - "Agent" instead of "Vendedor"
# - "WhatsApp" vs "Zap" vs "WPP"
```

## Business Context

The system is specifically designed for optical retail business ("Mercadão dos Óculos") with focus on:
- Customer service evaluation (D+1)
- Product satisfaction tracking (D+30)  
- Critical case management (NPS Ruim)
- Vendor performance analysis
- Store comparison metrics

## Testing and Debugging

- Each main module includes `if __name__ == "__main__"` test sections
- Flask server includes `/api/test` endpoint for extraction testing
- Use `test_ia_analysis.py` for AI analysis testing
- Generated reports are saved to `relatorios/` directory with timestamps