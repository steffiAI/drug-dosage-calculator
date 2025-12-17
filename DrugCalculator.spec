# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Drug Concentration Calculator
Optimized build with icon support
"""

block_cipher = None

# Packages to exclude
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
    datas=[('icon.ico', '.')],  # Bundle icon.ico with .exe for runtime
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
    icon='icon.ico',  # .exe file icon in File Explorer
)
