# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for the CustomTkinter build (main_ctk.py).
"""

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

excludes = [
    'numpy',
    'pandas',
    'scipy',
    'matplotlib',
    'IPython',
    'jupyter',
    'notebook',
    'numba',
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
# PIL is NOT excluded here - the CTk build needs it for CTkImage/Image.open,
# unlike the old tkinter build.

a = Analysis(
    ['main_ctk.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('assets', 'assets'),  # icon.ico, pill3.png, icons/ - matches _asset_path()'s lookup
        *collect_data_files('customtkinter'),  # CTk's own fonts + theme JSONs
    ],
    hiddenimports=[
        'pubchempy',
        'calculators',
        'data_storage',
        'formatters',
        'gui_integration_ctk',
        'pubchem_api',
        'darkdetect',
        'PIL._tkinter_finder',
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
    name='DrugCalculator-v3.0.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)
