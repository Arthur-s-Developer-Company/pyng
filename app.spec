import sys
import os

IS_LINUX = sys.platform.startswith("linux")

exe = EXE(
    pyz,
    a.scripts,
    a.binaries if IS_LINUX else [],
    a.zipfiles,
    a.datas,
    name='Pyng',
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
        name='Pyng',
    )
