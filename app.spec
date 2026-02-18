# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

IS_LINUX = sys.platform.startswith("linux")

a = Analysis(
    ["app.py"],
    pathex=[os.getcwd()],
    binaries=[],
    datas=[
        ("Fonts", "Fonts"),
        ("Sons", "Sons"),
        ("classes", "classes"),
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

PYZ = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    PYZ,
    a.scripts,
    a.binaries,  # ← sempre isso
    a.zipfiles,
    a.datas,
    name="Pyng",
    debug=False,
    strip=False,
    upx=True,
    console=True,
    onefile=IS_LINUX,
)

if not IS_LINUX:
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name="Pyng",
    )
