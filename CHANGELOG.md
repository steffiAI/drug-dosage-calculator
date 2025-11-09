# Changelog

All notable changes to the Drug Dosage Calculator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2025-11-09

### Fixed
- **Unit Conversion Bug**: Working solution calculator now properly handles different concentration units
  - Previously required stock and target concentrations to use the same unit (e.g., both mM)
  - Now automatically converts between M, mM, µM, and nM
  - Example: Can now dilute 10 mM stock → 1 µM working solution
  - Implements proper conversion factors for all unit combinations

### Changed
- Interactive HTML checklist now has properly clickable checkboxes
  - Can click either the checkbox or the text label
  - Green checkmarks appear when items are checked
  - Improved user experience

## [1.1.0] - 2025-11-09

### Added
- **Popup Result Windows**: Calculation results now appear in dedicated popup windows
  - No more scrolling needed to see full protocols
  - "Copy to Clipboard" button for easy copying of results
  - Cleaner, more professional interface
  - Windows center on screen automatically

- **Interactive HTML Testing Checklist**: Beautiful browser-based checklist
  - Clickable checkboxes for all test items
  - Auto-saves progress using browser localStorage
  - Live progress bar showing completion percentage
  - Export progress as text report
  - Print-friendly design
  - Reset functionality to start over

### Changed
- Removed scrollable text areas from calculator screens
- Input forms now remain visible when calculating
- Improved overall user experience

### Documentation
- Added UPDATES.md explaining v1.1 changes
- Added GITHUB_SETUP.md for repository setup instructions
- Updated QUICK_START.md with new popup window info

## [1.0.0] - 2025-11-09

### Added
- **Stock Solution Calculator**
  - Calculate mass of powder needed for stock solutions
  - Input: drug name, molecular weight, target concentration, volume, solvent
  - Output: Mass to weigh (mg and g), step-by-step preparation protocol
  - Support for M, mM, µM, nM concentration units
  - Support for L, mL, µL volume units

- **Working Solution Calculator**
  - Dilute stock solutions to working concentrations
  - Input: drug name, stock concentration, target concentration, volume, solvent
  - Output: Volumes to pipette, dilution factor, mixing instructions
  - C₁V₁ = C₂V₂ formula implementation

- **Calculation History**
  - Automatic saving of all calculations
  - Timestamped entries (ISO format)
  - Drug name and solvent tracking
  - Complete input/output storage
  - Persistent JSON storage in data/ directory
  - Newest-first ordering in viewer

- **Input Validation**
  - Validates positive values for molecular weight, concentration, volume
  - Clear error messages for invalid inputs
  - Unit selection dropdowns
  - Solvent selection with common options and custom entry

- **User Interface**
  - Clean tkinter-based GUI
  - Welcome screen with calculator selection
  - Back to menu navigation
  - Clear input button
  - Calculation counter display

### Documentation
- Comprehensive README.md with features, installation, usage
- MIT LICENSE
- .gitignore configured for Python projects
- requirements.txt (no external dependencies - uses standard library only)
- QUICK_START.md with examples and troubleshooting
- TESTING_CHECKLIST.md for verification
- PROJECT_SUMMARY.md with technical overview
- READ_ME_FIRST.md for new users

### Technical
- Numpy-style docstrings on all functions
- Type hints in function signatures
- Proper error handling with try-except blocks
- Modular code structure:
  - `main.py`: GUI application
  - `src/calculators.py`: Calculation logic
  - `src/data_storage.py`: History management
- No external dependencies (pure Python + tkinter)
- Cross-platform compatible (Windows, macOS, Linux)

---

## Version Numbering

We use Semantic Versioning:
- **MAJOR** version (X.0.0): Incompatible API changes
- **MINOR** version (0.X.0): New functionality (backwards-compatible)
- **PATCH** version (0.0.X): Bug fixes (backwards-compatible)

Current: v1.1.1

---

## Upcoming Features (Planned)

### Phase 2
- [ ] Serial dilution calculator
- [ ] Enhanced history viewer with filtering
- [ ] Selection and batch export from history
- [ ] Improved unit handling and conversion display

### Phase 3
- [ ] PDF export with formatted protocols
- [ ] PubChem API integration for automatic MW lookup
- [ ] Drug identifiers support (CAS number, Catalog #, RRID)
- [ ] Custom drug database
- [ ] Aliquot calculator

---

## Links

- [Repository](https://github.com/YOUR_USERNAME/drug-dosage-calculator)
- [Issues](https://github.com/YOUR_USERNAME/drug-dosage-calculator/issues)
- [Releases](https://github.com/YOUR_USERNAME/drug-dosage-calculator/releases)
