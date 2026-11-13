# -*- coding: utf-8 -*-
"""
ITS 智能座舱测试系统 - 高级打包脚本
功能：
- 自动检查环境和依赖
- 清理构建缓存
- 执行 PyInstaller 打包
- 生成版本信息
- 可选压缩打包
"""

import os
import sys
import subprocess
import shutil
import json
from datetime import datetime
from pathlib import Path


class ITSBuilder:
    """ITS 项目打包器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.spec_file = self.project_root / "ITS.spec"
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.output_name = "ITS 智能座舱测试系统.exe"
        
        # 必需的依赖包
        self.required_packages = [
            'PySide6',
            'pandas',
            'numpy',
            'openpyxl',
            'pyserial',
            'opencv-python',
            'pygame',
            'pyttsx3',
            'edge-tts',
            'pyinstaller'
        ]
        
    def print_header(self, text):
        """打印标题"""
        print("\n" + "="*60)
        print(f"  {text}")
        print("="*60)
    
    def print_info(self, text):
        """打印信息"""
        print(f"ℹ️  {text}")
    
    def print_success(self, text):
        """打印成功信息"""
        print(f"✅ {text}")
    
    def print_error(self, text):
        """打印错误信息"""
        print(f"❌ {text}")
    
    def print_warning(self, text):
        """打印警告信息"""
        print(f"⚠️  {text}")
    
    def check_python_version(self):
        """检查 Python 版本"""
        self.print_info("检查 Python 版本...")
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.print_error(f"Python 版本过低：{version.major}.{version.minor}")
            self.print_error("需要 Python 3.8 或更高版本")
            return False
        
        self.print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    
    def check_dependencies(self):
        """检查依赖包"""
        self.print_info("检查依赖包...")
        missing = []
        
        for package in self.required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"  ✓ {package}")
            except ImportError:
                print(f"  ✗ {package} (缺失)")
                missing.append(package)
        
        if missing:
            self.print_warning(f"缺失以下包：{', '.join(missing)}")
            response = input("是否自动安装？(y/n): ").strip().lower()
            if response == 'y':
                self.install_dependencies(missing)
            else:
                return False
        else:
            self.print_success("所有依赖包已安装")
        
        return True
    
    def install_dependencies(self, packages):
        """安装缺失的依赖包"""
        self.print_info("安装依赖包...")
        
        # 使用清华镜像源加速
        pip_cmd = [
            sys.executable, "-m", "pip", "install",
            "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
        ] + packages
        
        try:
            subprocess.run(pip_cmd, check=True)
            self.print_success("依赖包安装完成")
            return True
        except subprocess.CalledProcessError as e:
            self.print_error(f"安装失败：{e}")
            return False
    
    def clean_build(self):
        """清理构建目录"""
        self.print_info("清理旧的构建文件...")
        
        try:
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
                self.print_success("已清理 build 目录")
            
            if self.dist_dir.exists():
                shutil.rmtree(self.dist_dir)
                self.print_success("已清理 dist 目录")
            
            # 清理 __pycache__
            pycache_dirs = list(self.project_root.rglob("__pycache__"))
            for d in pycache_dirs:
                shutil.rmtree(d)
            self.print_success(f"已清理 {len(pycache_dirs)} 个 __pycache__ 目录")
            
            return True
        except Exception as e:
            self.print_error(f"清理失败：{e}")
            return False
    
    def build(self, debug=False, noconfirm=False):
        """执行打包"""
        self.print_header("开始打包")
        
        if not self.spec_file.exists():
            self.print_error(f"找不到 spec 文件：{self.spec_file}")
            return False
        
        # 构建 PyInstaller 命令
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",  # 清理临时文件
        ]
        
        if debug:
            cmd.append("--debug=all")
        
        if noconfirm:
            cmd.append("--noconfirm")
        
        cmd.append(str(self.spec_file))
        
        self.print_info(f"执行命令：{' '.join(cmd)}")
        print()
        
        try:
            # 执行打包
            result = subprocess.run(cmd, check=True)
            
            # 检查输出
            output_exe = self.dist_dir / self.output_name
            if output_exe.exists():
                self.print_success("打包完成！")
                
                # 显示文件信息
                file_size = output_exe.stat().st_size
                size_mb = file_size / (1024 * 1024)
                self.print_info(f"文件大小：{size_mb:.2f} MB ({file_size:,} 字节)")
                
                # 显示目录内容
                self.print_info("dist 目录内容:")
                for item in self.dist_dir.iterdir():
                    if item.is_file():
                        size = item.stat().st_size / 1024
                        print(f"  📄 {item.name} ({size:.1f} KB)")
                    else:
                        print(f"  📁 {item.name}/")
                
                return True
            else:
                self.print_error("打包完成但未找到生成的 exe 文件")
                return False
                
        except subprocess.CalledProcessError as e:
            self.print_error(f"打包失败：{e}")
            return False
        except Exception as e:
            self.print_error(f"打包过程出错：{e}")
            return False
    
    def create_version_info(self):
        """创建版本信息文件"""
        self.print_info("创建版本信息...")
        
        version_info = {
            "name": "ITS 智能座舱测试系统",
            "version": "1.0.0",
            "build_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform
        }
        
        version_file = self.dist_dir / "version.json"
        try:
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(version_info, f, ensure_ascii=False, indent=2)
            self.print_success(f"版本信息已保存到：{version_file}")
            return True
        except Exception as e:
            self.print_error(f"创建版本信息失败：{e}")
            return False
    
    def create_readme(self):
        """创建使用说明"""
        self.print_info("创建使用说明...")
        
        readme_content = f"""# ITS 智能座舱测试系统

## 版本信息
- 构建日期：{datetime.now().strftime("%Y-%m-%d")}
- Python 版本：{sys.version_info.major}.{sys.version_info.minor}

## 使用方法

### 直接运行
双击 `ITS 智能座舱测试系统.exe` 即可启动程序。

### 命令行运行
```bash
ITS 智能座舱测试系统.exe
```

## 文件夹说明
- `image/` - 程序图标和资源文件
- `script/` - 批处理脚本
- `配置基准文件/` - 语音测试基准配置

## 注意事项
1. 首次运行可能需要安装 ADB 驱动
2. 确保车辆网络连接正常
3. 程序需要管理员权限访问串口

## 技术支持
如有问题，请联系开发团队。

---
构建日期：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        readme_file = self.dist_dir / "README.md"
        try:
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            self.print_success(f"使用说明已保存到：{readme_file}")
            return True
        except Exception as e:
            self.print_error(f"创建使用说明失败：{e}")
            return False
    
    def run(self, clean=True, debug=False, create_docs=True):
        """
        执行完整打包流程
        :param clean: 是否清理旧文件
        :param debug: 是否启用调试模式
        :param create_docs: 是否创建文档
        """
        self.print_header("ITS 智能座舱测试系统 - 打包工具")
        
        # 1. 检查环境
        if not self.check_python_version():
            return False
        
        # 2. 检查依赖
        if not self.check_dependencies():
            return False
        
        # 3. 清理
        if clean and not self.clean_build():
            response = input("清理失败，继续打包？(y/n): ").strip().lower()
            if response != 'y':
                return False
        
        # 4. 打包
        if not self.build(debug=debug, noconfirm=True):
            return False
        
        # 5. 创建文档
        if create_docs:
            self.create_version_info()
            self.create_readme()
        
        self.print_header("打包完成")
        print(f"\n📦 输出目录：{self.dist_dir}")
        print(f"📄 可执行文件：{self.dist_dir / self.output_name}")
        print("\n💡 提示：可以将 dist 文件夹整个复制给其他电脑使用\n")
        
        return True


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ITS 智能座舱测试系统打包工具')
    parser.add_argument('--no-clean', action='store_true', help='不清理旧文件')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--no-docs', action='store_true', help='不创建文档')
    
    args = parser.parse_args()
    
    builder = ITSBuilder()
    success = builder.run(
        clean=not args.no_clean,
        debug=args.debug,
        create_docs=not args.no_docs
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
