# -*- mode: python ; coding: utf-8 -*-
"""
ITS 智能座舱测试系统 - PyInstaller spec

打包命令:
    pyinstaller --clean --noconfirm ITS.spec

输出:
    dist/ITS 智能座舱测试系统/

说明:
    本项目运行时会从 exe 同级目录读取 dll/script/config/key/配置基准文件，
    因此这里使用 onedir 打包，并启用 PyInstaller 6 的旧式目录布局
    contents_directory='.'，保证资源目录与 exe 同级。
"""

import os
from PyInstaller.utils.hooks import collect_submodules


# ============================================================
# 路径
# ============================================================
if '__file__' in globals():
    project_root = os.path.dirname(os.path.abspath(__file__))
else:
    project_root = os.getcwd()

subpy_dir = os.path.join(project_root, 'Subpy')


# ============================================================
# 隐藏导入
# ============================================================
hiddenimports = []

# 项目子模块自动收集，避免新增 Subpy/*.py 后漏打包。
hiddenimports += collect_submodules('Subpy')

# 第三方库中常见动态导入。
hiddenimports += [
    # GUI
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtMultimedia',

    # 数据处理
    'pandas',
    'pandas._libs.tslibs.timedeltas',
    'pandas._libs.tslibs.np_datetime',
    'pandas._libs.tslibs.nattype',
    'pandas._libs.skiplist',
    'numpy',
    'openpyxl',
    'openpyxl.cell._writer',

    # 通信/硬件
    'serial',
    'serial.tools',
    'serial.tools.list_ports',
    'requests',
    'paho',
    'paho.mqtt',
    'paho.mqtt.client',

    # 图像/抓包
    'cv2',
    'cv2.gapi.wip.draw',
    'PIL',
    'PIL.Image',
    'scapy',
    'scapy.all',

    # 音频/语音
    'pygame',
    'pygame.mixer',
    'pyttsx3',
    'pyttsx3.drivers',
    'pyttsx3.drivers.sapi5',
    'edge_tts',
    'pyaudio',
]

hiddenimports = sorted(set(hiddenimports))


# ============================================================
# 数据目录
# ============================================================
datas = []

required_data_dirs = [
    ('image', 'image'),
    ('script', 'script'),
    ('配置基准文件', '配置基准文件'),
]

optional_data_dirs = [
    ('config', 'config'),
    ('UDS', 'UDS'),
    ('dll', 'dll'),
    ('bin', 'bin'),
    ('key', 'key'),
    ('录音', '录音'),
]

for src_name, dest_name in required_data_dirs + optional_data_dirs:
    src_path = os.path.join(project_root, src_name)
    if os.path.exists(src_path):
        datas.append((src_path, dest_name))


# ============================================================
# 二进制与排除项
# ============================================================
binaries = []

excludes = [
    'tkinter',
    'wx',
    'PyQt5',
    'PyQt6',
    'matplotlib',
    'scipy',
    'sympy',
    'IPython',
    'notebook',
    'jupyter',
    'pytest',
    'nose',
]


# ============================================================
# 图标
# ============================================================
icon_path = os.path.join(project_root, 'image', 'Car.ico')
if not os.path.exists(icon_path):
    icon_path = None


# ============================================================
# PyInstaller 构建对象
# ============================================================
block_cipher = None

a = Analysis(
    ['ITS_app.py'],
    pathex=[project_root, subpy_dir],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='ITS 智能座舱测试系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
    contents_directory='.',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='ITS 智能座舱测试系统',
)


print('\n' + '=' * 60)
print('ITS 智能座舱测试系统 - spec 已加载')
print('=' * 60)
print(f'项目根目录: {project_root}')
print(f'Subpy 目录: {subpy_dir}')
print(f'图标路径: {icon_path}')
print(f'隐藏导入数: {len(hiddenimports)}')
print(f'数据目录数: {len(datas)}')
print('输出目录: dist/ITS 智能座舱测试系统')
print('=' * 60 + '\n')
