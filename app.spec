# app.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import sys

IS_LINUX = sys.platform.startswith("linux")


a = Analysis(
    ['app.py'],       # Seu script principal
    pathex=[],
    binaries=[],
    datas=[
        ('Fonts', 'Fonts'),    # Copia a pasta Fonts da raiz para dentro do EXE
        ('classes', 'classes'),
        ('Sons', 'Sons'),
        # Adicione outras pastas aqui se precisar, ex:
        # ('assets', 'assets'),
        # ('img', 'img'), 
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Pyng',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,        # Mantém o terminal aberto para ver erros (mude para False depois)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=IS_LINUX
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Pyng',
)