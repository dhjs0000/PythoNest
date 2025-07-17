import os
import sys
import platform
import subprocess
import logging

# 设置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pythonest.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("PythoNest")

def get_system_info():
    """获取系统信息"""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "architecture": platform.architecture(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
    }

def is_admin():
    """检查当前进程是否具有管理员权限"""
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except:
        return False

def run_as_admin(cmd, wait=True):
    """以管理员权限运行命令"""
    if platform.system() == "Windows":
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                # 如果当前不是管理员权限，则请求提升
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, cmd, None, 1)
                return True
        except:
            logger.error("无法以管理员权限运行命令")
            return False
    
    # 已经是管理员或非Windows系统，直接执行命令
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except:
        logger.error(f"执行命令失败: {cmd}")
        return False

def ensure_dir(directory):
    """确保目录存在，如果不存在则创建"""
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            return True
        except:
            logger.error(f"无法创建目录: {directory}")
            return False
    return True

def get_resource_path(relative_path):
    """获取资源文件的绝对路径，兼容PyInstaller打包后的程序。
    
    Args:
        relative_path (str): 资源文件的相对路径
        
    Returns:
        str: 资源文件的绝对路径
    """
    import os
    import sys
    
    # PyInstaller会创建一个临时文件夹，并将路径存储在sys._MEIPASS中
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', relative_path) 