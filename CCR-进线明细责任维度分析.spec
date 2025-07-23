# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('modules/*.py', 'modules'), ('ui/*.py', 'ui'), ('utils/*.py', 'utils'), ('favicon.ico', '.')],
    hiddenimports=['pandas', 'matplotlib', 'numpy', 'openpyxl', 'pillow', 'ttkbootstrap', 'xlrd'],
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
    name='CCR-进线明细责任维度分析',
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
    icon=["D:\\文件\Computer-Language exercise\\Python-exercise\\工作自动化\\CCR\\CCR-进线明细责任维度分析\\favicon.ico"],
)
