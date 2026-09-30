# Changelog

All notable changes to the Drug Dosage Calculator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.2.0] - 2025-09-30

### Added
- **PDF Export System**: Professional print-optimized protocol export
  - Clean minimal design with white background for efficient printing
  - Multi-select export with checkboxes in history table
  - Customizable export options dialog (sort order, page breaks)
  - File save dialog with editable default filenames
  - Auto-open PDF after generation
  - Footer with version number and GitHub link
- **Multi-Select Calculation Export**
  - Checkbox column in history table for selection
  - "Select All" / "Deselect All" buttons
  - Live selection counter display
  - Export single or multiple calculations as one PDF
  - Sort options: table order, by drug name, by date, by type
  - Optional page breaks between protocols
- **Adjustable Font Scaling**
  - User-configurable font size slider (100%-150%)
  - 10% increments for smooth adjustment
  - Default set to 120% for improved readability
  - Persistent preference storage
  - All UI elements scale including tooltips and history table
  - Centralized font management system
- **Dark Mode Consistency**
  - Custom dark-themed success dialog (replaces Windows messageboxes)
  - All dialogs follow dark theme (export options, confirmations)
  - Consistent color palette throughout application

### Changed
- **About Dialog**: Now properly centers on screen with explicit sizing
- **History Table**: Added checkbox column as first column
- **User Preferences**: Now stored in `data/user_preferences.json`
- **Export Options**: Separate dialog for multi-calculation export settings

### Fixed
- About dialog centering issues on all screen sizes
- Checkbox column only responds to clicks in first column (not entire row)
- Double-click functionality preserved for viewing calculation details
- Column indices updated to account for checkbox column
- Export dialogs properly sized to prevent button cutoff

### Technical
- New module: `src/font_manager.py` - Centralized font scaling
- New module: `src/pdf_export.py` - PDF generation with reportlab
- Added reportlab dependency for PDF generation
- Updated PyInstaller spec with new hidden imports
- Enhanced data storage with user preferences support

## [3.1.0] - 2025-09-30

### Added
- Adjustable font scaling with slider control
- User preference persistence
- Centered main window content

### Changed
- Default font scale increased to 120%
- About dialog updated with version number

## [3.0.0] - 2025-09-30

### Changed
- **Complete UI Migration to CustomTkinter**
  - Modern dark-themed interface
  - Improved visual consistency
  - Better cross-platform appearance
  - Professional design aesthetic

## [1.2.0] - 2025-11-21

### Added
- **Smart Decimal Formatting**: Dynamic precision based on measurement accuracy
  - Values < 10: 2 decimal places (e.g., 5.23 µl)
  - Values 10-100: 1 decimal place (e.g., 25.8 µl)
  - Values > 100: no decimals (e.g., 499 µl)
  - No more misleading trailing zeros (499.0000 → 499)
- **Input Validation for Decimal Separators**: Detects comma vs period usage
  - Catches German locale comma confusion (5,2 vs 5.2)
  - Clear error message: "Please use period (.) for decimals, not comma (,)"
  - Prevents program crashes from invalid float conversion
- **Interactive Tooltips**: Hover guidance system for input fields
  - ℹ️ info icons next to numeric input fields
  - Light yellow tooltip appears on hover
  - Reminds users to use period (.) for decimals
- **Formatters Module** (`src/formatters.py`): Centralized number formatting utilities
  - `format_number()`: Smart rounding based on value magnitude
  - `validate_decimal_input()`: Input validation with helpful error messages
  - `format_result_with_unit()`: Consistent number + unit formatting
  - Reusable across all calculators

### Changed
- **Default Volume Unit**: Changed from mL to µL for better lab workflow consistency
  - Stock solution calculator now defaults to µL
  - Working solution calculator now defaults to µL
  - Aligns with typical pipetting volumes in cell culture
- **Error Messages**: More specific and actionable validation errors
  - Now indicates which field has the error
  - Provides example of correct format
- **Results Display**: Cleaner, more professional number presentation
  - Removed gram weight from popup display (kept in history for records)
  - All values now show appropriate precision
  - More scannable and less cluttered

### Technical
- Added `ToolTip` class for GUI hover help
- Implements pipette precision guidelines (P1000, P200, P20 accuracy standards)
- Better separation of concerns (formatting logic separated from GUI)

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

Current: v3.2.0

---

## Upcoming Features (Planned)

- [ ] Serial dilution calculator
- [ ] Additional drug identifiers support (Catalog #, RRID)
- [ ] Custom drug database expansion
- [ ] Aliquot calculator
- [ ] Batch calculation templates

---

## Links

- [Repository](https://github.com/steffiAI/drug-dosage-calculator)
- [Issues](https://github.com/steffiAI/drug-dosage-calculator/issues)
- [Releases](https://github.com/steffiAI/drug-dosage-calculator/releases)