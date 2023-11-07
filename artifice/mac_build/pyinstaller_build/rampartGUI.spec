# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['../../rampart.pyw'],
    pathex=[],
    binaries=[],
    datas=[('../../rampart.yml', '.'), ('../../resources', './resources')],
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
    name='rampartGUIv1.5.2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../resources/rampart-icon.icns',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='artifice',
)
app = BUNDLE(
    coll,
    name='rampartGUIv1.5.2.app',
    icon='../../resources/rampart-icon.icns',
    bundle_identifier=None,
)
