# -*- mode: python ; coding: utf-8 -*-
import os

datas = [
    ('frontend/dist/index.html', 'frontend/dist/index.html'),
    ('frontend/dist/assets/*', 'frontend/dist/assets/')
]

hiddenimports = [
    'passlib.handlers.bcrypt',
    'tzdata',
    '_cffi_backend',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='icon',
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
    windowed=True,
    noconsole=True,
)
