# Drug Dosage Calculator - Lab Edition

A Python GUI application for calculating drug solution preparations in laboratory settings. This tool helps researchers quickly calculate the exact amounts needed to prepare stock solutions from powder and dilute stock solutions to working concentrations.

## Features

### Phase 1 (Current - MVP)
- ✅ **Stock Solution Calculator**: Calculate mass of powder needed to prepare stock solutions
- ✅ **Working Solution Calculator**: Dilute stock solutions to working concentrations
- ✅ **Calculation History**: Automatically saves all calculations with timestamps
- ✅ **Unit Conversions**: Support for M, mM, µM, nM (concentration) and L, mL, µL (volume)
- ✅ **Solvent Tracking**: Record which solvent was used for each preparation
- ✅ **User-Friendly GUI**: Clean tkinter interface with step-by-step instructions

### Coming Soon (Phase 2)
- Serial dilution calculator
- Enhanced history viewer with selection and filtering
- Custom unit preferences

### Future Plans (Phase 3)
- PDF export with formatted protocols
- PubChem API integration for automatic molecular weight lookup
- Drug identifier support (CAS numbers, catalog numbers, RRID)

## Requirements

- **Python**: 3.11+
- **OS**: Windows 11 (tested), likely compatible with macOS/Linux but not yet verified
- **Dependencies**: Only Python standard library (tkinter)

## Installation

### Option 1: Using the Executable (Windows Only)
1. Download the latest `.exe` file from the [Releases](https://github.com/steffiAI/drug-dosage-calculator/releases) page
2. Double-click to run - no installation needed!
3. **Note:** macOS/Linux users should use Option 2 (run from source)

### Option 2: Running from Source

```bash
# Clone the repository
git clone https://github.com/steffiAI/drug-dosage-calculator.git
cd drug-dosage-calculator

# Create virtual environment (recommended)
python -m venv venv
source venv/Scripts/activate  # On Windows (Git Bash)
# or
source venv/bin/activate       # On macOS/Linux

# Run the application
python main.py
```

## Usage

### Stock Solution Calculator

Use this when you need to prepare a stock solution from powder:

1. Click "Stock Solution Calculator"
2. Enter:
   - Drug name
   - Molecular weight (g/mol)
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
   - Target concentration (with unit - must match stock unit)
   - Desired volume (with unit)
   - Solvent type
3. Click "Calculate"
4. Follow the dilution protocol displayed

**Example**: Dilute 10 mM stock to 1 µM working solution
- Stock: 10 mM
- Target: 1 µM in 10 mL media
- Result: Add 1 µL stock to 9.999 mL media (10,000x dilution)

### Viewing History

- Click "View Calculation History" from the main menu
- See all past calculations with timestamps
- Useful for record-keeping and reproducing preparations

## Project Structure

```
drug-dosage-calculator/
├── main.py                 # Main GUI application
├── src/
│   ├── calculators.py     # Core calculation functions
│   └── data_storage.py    # History management
├── data/
│   └── calculation_history.json  # Saved calculations (auto-generated)
├── README.md
├── LICENSE
└── requirements.txt
```

## Building Executable

To create a standalone `.exe` file:

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed --name "DrugCalculator" main.py

# Find the executable in dist/
```

## Contributing

Contributions are welcome! This project is maintained by a PhD candidate to help researchers streamline their lab workflows.

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
Strasser, S. (2025). Drug Dosage Calculator - Lab Edition. 
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
