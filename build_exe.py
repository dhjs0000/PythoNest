import os
import sys
import shutil
import subprocess
import traceback
from datetime import datetime
import logging

def create_exe():
    try:
        # 配置日志
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"build_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        logging.info("开始构建PythoNest可执行文件...")
        
        # 获取当前日期，格式为YYYYMMDD
        today = datetime.now().strftime("%Y%m%d")
        
        # 创建build/日期文件夹
        build_dir = os.path.join("build", today)
        os.makedirs(build_dir, exist_ok=True)
        
        logging.info(f"输出目录: {build_dir}")
        
        # 检查是否已安装PyInstaller
        try:
            import PyInstaller
            logging.info(f"已找到PyInstaller版本: {PyInstaller.__version__}")
        except ImportError:
            logging.info("正在安装PyInstaller...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyInstaller"])
            logging.info("PyInstaller安装完成")
        
        # 构建PyInstaller命令
        pyinstaller_cmd = [
            "pyinstaller",
            "--name=PythoNest",
            "--windowed",  # 不显示控制台窗口
            "--icon=website/images/logo.png",  # 图标文件
            # 添加资源文件
            "--add-data=src/ui/images;src/ui/images",
            "--add-data=website/images;website/images",
            # 确保包含所有必要的模块
            "--hidden-import=PyQt6.QtCore",
            "--hidden-import=PyQt6.QtGui",
            "--hidden-import=PyQt6.QtWidgets",
            "--hidden-import=src.core.python_manager",
            "--hidden-import=src.core.venv_manager",
            "--hidden-import=src.core.package_manager",
            "--hidden-import=requests",
            "--exclude-module=tkinter",  # 排除不需要的模块
            "--exclude-module=unittest",
            "--exclude-module=test",
            "--exclude-module=numpy",
            "--onedir",  # 创建单文件夹
            "--clean",
            "--noconfirm",
            "--log-level=WARN",
            "--distpath", build_dir,  # 指定输出目录
            "main.py"
        ]
        
        # 执行PyInstaller命令
        logging.info("正在执行PyInstaller命令...")
        logging.info(" ".join(pyinstaller_cmd))
        subprocess.check_call(pyinstaller_cmd)
        
        # 复制配置文件和其他必要文件到打包目录
        dist_dir = os.path.join(build_dir, "PythoNest")
        logging.info(f"打包完成，正在复制额外文件到: {dist_dir}")
        
        # 如果有README或LICENSE，也复制到打包目录
        for file in ["README.md", "LICENSE"]:
            if os.path.exists(file):
                shutil.copy(file, dist_dir)
                logging.info(f"已复制 {file} 到打包目录")
        
        # 创建一个运行脚本
        launch_bat = os.path.join(dist_dir, "启动PythoNest.bat")
        with open(launch_bat, "w", encoding="utf-8") as f:
            f.write("@echo off\n")
            f.write("start PythoNest.exe\n")
        logging.info(f"已创建启动脚本: {launch_bat}")
        
        # 将日志文件也复制到输出目录
        shutil.copy(log_file, dist_dir)
        logging.info(f"已复制构建日志到: {dist_dir}")
        
        logging.info(f"构建成功！程序已保存到 {dist_dir}")
        print(f"\n打包成功！程序已保存到 {dist_dir}")
        print("您可以运行 PythoNest.exe 或 启动PythoNest.bat 来启动应用程序")
        
        return True
        
    except Exception as e:
        logging.error(f"构建失败: {str(e)}")
        logging.error(traceback.format_exc())
        print(f"\n错误: 构建失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_exe()
    sys.exit(0 if success else 1) 