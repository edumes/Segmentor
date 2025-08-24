# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Configurações específicas para macOS
block_cipher = None

# Adicionar apenas arquivos essenciais
added_files = []
# Adicionar arquivos de recursos se existirem
if os.path.exists('assets'):
    added_files.append(('assets', 'assets'))

# Módulos ocultos necessários
hidden_imports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'cv2',
    'numpy',
    'PIL',
    'PIL.Image',
    'platform_utils',
    'video_utils'
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'pandas'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Filtrar arquivos desnecessários para reduzir tamanho
a.datas = [x for x in a.datas if not x[0].startswith('tcl')]
a.datas = [x for x in a.datas if not x[0].startswith('tk')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Segmentor',
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Segmentor',
)

# Configuração específica para macOS .app bundle
app = BUNDLE(
    coll,
    name='Segmentor.app',
    icon='assets/icon.icns',
    bundle_identifier='com.segmentor.app',
    version='1.0.0',
    info_plist={
        'CFBundleName': 'Segmentor',
        'CFBundleDisplayName': 'Segmentor',
        'CFBundleIdentifier': 'com.segmentor.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': 'SGMT',
        'CFBundleExecutable': 'Segmentor',
        'CFBundleIconFile': 'icon.icns',
        'LSMinimumSystemVersion': '10.15.0',
        'LSApplicationCategoryType': 'public.app-category.video',
        'NSHighResolutionCapable': True,
        'NSSupportsAutomaticGraphicsSwitching': True,
        'NSRequiresAquaSystemAppearance': False,
        'NSCameraUsageDescription': 'Este aplicativo não usa a câmera.',
        'NSMicrophoneUsageDescription': 'Este aplicativo não usa o microfone.',
        'NSDocumentsFolderUsageDescription': 'Para salvar vídeos processados.',
        'NSDesktopFolderUsageDescription': 'Para acessar vídeos na área de trabalho.',
        'NSDownloadsFolderUsageDescription': 'Para acessar vídeos na pasta Downloads.',
        'NSRemovableVolumesUsageDescription': 'Para acessar vídeos em volumes externos.',
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Video Files',
                'CFBundleTypeRole': 'Viewer',
                'LSItemContentTypes': [
                    'public.movie',
                    'public.video',
                    'com.apple.quicktime-movie',
                    'public.mpeg-4'
                ],
                'LSHandlerRank': 'Alternate'
            }
        ],
        'UTExportedTypeDeclarations': [],
        'UTImportedTypeDeclarations': []
    },
)