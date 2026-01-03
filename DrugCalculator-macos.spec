# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Drug Concentration Calculator - macOS Build
Matches Windows spec but creates .app bundle for macOS
"""

block_cipher = None

# Packages to exclude (same as Windows for consistency)
excludes = [
    'numpy',
    'pandas',
    'scipy',
    'matplotlib',
    'IPython',
    'jupyter',
    'notebook',
    'numba',
    'PIL',
    'PyQt5',
    'zmq',
    'jedi',
    'parso',
    'pygments',
    'jinja2',
    'certifi',
    'lxml',
    'openpyxl',
    'win32com',
    'pytest',
    'setuptools',
    'distutils',
]

a = Analysis(
    ['main.py'],
    pathex=['src'],
    binaries=[],
    datas=[],  # No icon needed in datas for macOS
    hiddenimports=[
        'pubchempy',
        'calculators',
        'data_storage',
        'formatters',
        'gui_integration',
        'pubchem_api',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DrugCalculator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# macOS-specific: Create .app bundle
app = BUNDLE(
    exe,
    name='DrugCalculator.app',
    bundle_identifier='com.steffi.drugcalculator',
    version='2.1.1',
    info_plist={
        'CFBundleName': 'Drug Calculator',
        'CFBundleDisplayName': 'Drug Calculator',
        'CFBundleGetInfoString': 'Calculate drug concentrations for research',
        'CFBundleVersion': '2.1.1',
        'CFBundleShortVersionString': '2.1.1',
        'NSHumanReadableCopyright': 'Copyright © 2025 Steffi',
        'NSHighResolutionCapable': 'True',
        'LSMinimumSystemVersion': '10.13.0',  # macOS High Sierra or later
        'NSRequiresAquaSystemAppearance': 'False',  # Support dark mode
    },
)