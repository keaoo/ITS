# -*- coding: utf-8 -*-
"""
ITS 打包配置验证脚本
用于在正式打包前检查配置是否正确
"""

import os
import sys


def check_file_exists(path, description):
    """检查文件是否存在"""
    if os.path.exists(path):
        print(f"  [OK] {description}: {path}")
        return True
    else:
        print(f"  [FAIL] {description} (不存在): {path}")
        return False


def check_dir_exists(path, description):
    """检查目录是否存在"""
    if os.path.isdir(path):
        print(f"  [OK] {description}: {path}")
        return True
    else:
        print(f"  [WARN] 目录不存在，但不影响打包：{path}")
        return False


def validate_spec():
    """验证 spec 配置"""
    print("="*60)
    print("ITS 智能座舱测试系统 - 打包配置验证")
    print("="*60)
    print()
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 1. 检查主程序
    print("1. 检查主程序文件...")
    main_ok = check_file_exists(
        os.path.join(project_root, 'ITS_app.py'),
        '主程序'
    )
    print()
    
    # 2. 检查 spec 文件
    print("2. 检查 spec 文件...")
    spec_ok = check_file_exists(
        os.path.join(project_root, 'ITS.spec'),
        'Spec 配置'
    )
    print()
    
    # 3. 检查 Subpy 目录
    print("3. 检查 Subpy 目录...")
    subpy_dir = os.path.join(project_root, 'Subpy')
    subpy_ok = check_dir_exists(subpy_dir, 'Subpy 目录')
    
    if subpy_ok:
        # 统计 Python 文件数量
        py_files = [f for f in os.listdir(subpy_dir) if f.endswith('.py')]
        print(f"  [INFO] Subpy 目录包含 {len(py_files)} 个 Python 文件")
        
        # 检查关键模块
        key_modules = [
            'doip_client.py',
            'test_executor.py',
            'test_runner.py',
            'zonghe_testdialog.py',
            'voice_test_dialog.py',
            'socket_220v_cycle_test.py',
        ]
        
        print("\n  检查关键模块:")
        for module in key_modules:
            check_file_exists(
                os.path.join(subpy_dir, module),
                module
            )
    print()
    
    # 4. 检查数据目录
    print("4. 检查数据目录...")
    data_dirs = [
        ('image', '图标资源'),
        ('script', '脚本文件'),
        ('配置基准文件', '语音基准'),
        ('config', '配置文件'),
        ('DTC', 'DTC 数据库'),
        ('UDS', 'UDS 配置'),
    ]
    
    for dir_name, desc in data_dirs:
        check_dir_exists(
            os.path.join(project_root, dir_name),
            desc
        )
    print()
    
    # 5. 检查图标文件
    print("5. 检查图标文件...")
    icon_path = os.path.join(project_root, 'image', 'Car.ico')
    icon_ok = check_file_exists(icon_path, '程序图标')
    print()
    
    # 6. 检查依赖
    print("6. 检查 Python 依赖...")
    required_packages = [
        'PySide6',
        'pandas',
        'numpy',
        'openpyxl',
        'pyserial',
        'cv2',
        'pygame',
        'pyttsx3',
        'edge_tts',
        'PyInstaller',
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  [OK] {package}")
        except ImportError:
            print(f"  [FAIL] {package} (缺失)")
            missing.append(package)
    
    if missing:
        print(f"\n[WARN] 警告：缺失以下包：{', '.join(missing)}")
        print("   安装命令：pip install -r requirements.txt")
    print()
    
    # 7. 总结
    print("="*60)
    print("验证总结")
    print("="*60)
    
    issues = []
    
    if not main_ok:
        issues.append("[FAIL] 主程序文件不存在")
    
    if not spec_ok:
        issues.append("[FAIL] spec 文件不存在")
    
    if not icon_ok:
        issues.append("[WARN] 图标文件不存在（会使用默认图标）")
    
    if missing:
        issues.append(f"[WARN] 缺失 {len(missing)} 个依赖包")
    
    if issues:
        print("\n发现的问题:")
        for issue in issues:
            print(f"  {issue}")
        print("\n[INFO] 建议先解决上述问题再执行打包")
    else:
        print("\n[OK] 所有检查通过！可以开始打包")
        print("\n打包命令:")
        print("  pyinstaller ITS.spec")
        print("  或")
        print("  build.bat")
    
    print("="*60)
    
    return len([i for i in issues if i.startswith('[FAIL]')]) == 0


if __name__ == '__main__':
    success = validate_spec()
    sys.exit(0 if success else 1)
