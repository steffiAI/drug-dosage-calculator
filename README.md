# Drug Concentration Calculator - Lab Edition

A Python GUI application for calculation of stock and working dilutions. This tool helps researchers quickly calculate the exact amounts needed to prepare stock solutions from powder and dilute stock solutions to working concentrations.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)]()

## Features

- ✅ **Stock Solution Calculator**: Calculate mass of powder needed to prepare stock solutions
- ✅ **Working Solution Calculator**: Dilute stock solutions to working concentrations
- ✅ **PubChem integration**: Automatic molecular weight lookup by drug name or CAS number
- ✅ **Calculation History**: Automatically saves all calculations with timestamps, with search, filtering, and sortable columns
- ✅ **PDF Export**: Professional print-optimized protocols with multi-select export, sort options, and auto-open
- ✅ **Multi-select Export**: Select multiple calculations and export as a single PDF with customizable formatting
- ✅ **Adjustable Font Scaling**: User-configurable font size (100%-150%) for improved readability
- ✅ **Unit Conversions**: Support for M, mM, µM, nM (concentration) and L, mL, µL (volume)
- ✅ **Solvent Tracking**: Record which solvent was used for each preparation
- ✅ **Modern dark-themed GUI**: Built with CustomTkinter with consistent dark mode across all dialogs

### Coming Soon
- Serial dilution calculator
- Custom unit preferences
- Batch calculations

## Requirements

- **Python**: 3.11+
- **OS**: Windows 11 (tested); the packaged `.exe` is Windows-only
- **Dependencies**: customtkinter, Pillow, pubchempy (see `pyproject.toml`)

## Installation

### Option 1: Using the Executable (Windows Only)
1. Download the latest `.exe` file from the [Releases](https://github.com/steffiAI/drug-dosage-calculator/releases) page
2. Double-click to run - no installation needed!

### Option 2: Running from Source

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Clone the repository
git clone https://github.com/steffiAI/drug-dosage-calculator.git
cd drug-dosage-calculator

# Install dependencies into a managed virtual environment
uv sync

# Run the application
uv run python main_ctk.py
```

## Usage

### Stock Solution Calculator

Use this when you need to prepare a stock solution from powder:

1. Click "Stock Solution Calculator"
2. Enter:
   - Drug name
   - Molecular weight (g/mol) - or click "Lookup MW" to fetch it from PubChem
   - Desired concentration (with unit)
   - Desired volume (with unit)
   - Solvent type
3. Click "Calculate"
4. Follow the step-by-step protocol displayed

**Example**: Prepare 10 mM Staurosporine stock
- Drug: Staurosporine
- MW: 466.54 g/mol
- Target: 10 mM in 1 mL DMSO
- Result: Weigh 4.6654 mg

### Working Solution Calculator

Use this to dilute stock solutions to working concentrations:

1. Click "Working Solution Calculator"
2. Enter:
   - Drug name
   - Stock concentration (with unit)
   - Target concentration (with unit - must be lower than stock concentration)
   - Desired volume (with unit)
   - Solvent type
3. Click "Calculate"
4. Follow the dilution protocol displayed

**Example**: Dilute 10 mM stock to 20 µM working solution
- Stock: 10 mM
- Target: 20 µM in 500 µL media
- Result: Add 1 µL stock to 499 µL media (500x dilution)

### Viewing & Exporting History

- Click "View Calculation History" from the main menu
- Search by drug name or solvent, filter by calculation type, and click any column header to sort by it
- Double-click an entry (or select it and click "View Details") to see the full protocol again
- **Export to PDF**: Click checkboxes to select one or more calculations, then click "Export PDF"
  - Single calculation: Saves immediately with editable filename
  - Multiple calculations: Choose sort order (by drug name, date, type, or table order) and page break options
  - PDFs are optimized for printing (clean white background, minimal design) and auto-open after generation

## Project Structure

```
drug-dosage-calculator/
├── main_ctk.py                    # Main GUI application (CustomTkinter)
├── assets/                        # Icons, app icon, hero image
├── src/
│   ├── calculators.py             # Core calculation functions
│   ├── data_storage.py            # History & preferences management
│   ├── font_manager.py            # Centralized font scaling system
│   ├── formatters.py              # Number/unit formatting
│   ├── gui_integration_ctk.py     # PubChem lookup widget, About dialog
│   ├── pdf_export.py              # PDF protocol generation
│   └── pubchem_api.py             # PubChem API wrapper
├── data/
│   ├── calculation_history.json   # Saved calculations (auto-generated)
│   └── user_preferences.json      # User settings (auto-generated)
├── DrugCalculator-ctk-windows.spec # PyInstaller build config
├── README.md
├── LICENSE
└── pyproject.toml
```

## Building the Executable

```bash
# Add PyInstaller to the project (one-time)
uv add --dev pyinstaller

# Build using the spec file
uv run python -m PyInstaller DrugCalculator-ctk-windows.spec

# Find the executable in dist/
```

## Contributing

Contributions are welcome! This project is maintained by a researcher to help other researchers streamline their lab workflows.

**Areas for contribution:**
- Additional calculator types
- Enhanced UI/UX
- Bug fixes
- Documentation improvements

## License

MIT License - See [LICENSE](LICENSE) file for details

## Citation

If you use this tool in your research, please cite:

```
Strasser, S. (2025). Drug Concentration Calculator - Lab Edition. 
GitHub repository: https://github.com/steffiAI/drug-dosage-calculator
```

## Contact

- **Author**: Stefanie Strasser
- **GitHub**: [@steffiAI](https://github.com/steffiAI)
- **Issues**: [Report bugs or request features](https://github.com/steffiAI/drug-dosage-calculator/issues)

## Acknowledgments

Built with the goal of making lab work more efficient and reducing calculation errors in drug preparation.

---

**Note**: This tool is for laboratory research use only. Always verify calculations independently and follow your institution's safety protocols.
