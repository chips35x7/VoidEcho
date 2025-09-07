# main.spec
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files
import os

# Panda3D runtime
panda3d_libs = collect_dynamic_libs("panda3d")
panda3d_data = collect_data_files("panda3d")

# Ursina built-in assets (models, textures, prefabs, etc.)
ursina_data = collect_data_files("ursina")

# Your custom assets
extra_datas = [
    ('assets', 'assets'),
    ('music', 'music'),
    ('assets/fonts', 'assets/fonts'),
]

datas = panda3d_data + ursina_data + extra_datas
binaries = panda3d_libs

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=['panda3d.core', 'direct', 'ursina'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='VoidEcho',
    icon='VoidEcho.ico',
    debug=False,
    strip=False,
    upx=True,
    console=False  # True if you want a debug console
)
